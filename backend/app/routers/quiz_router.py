from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, Quiz, QuizAttempt, QuizQuestion
from ..schemas import (
    QuizGenerateRequest,
    QuizPublicResponse,
    QuizSubmitRequest,
    QuizResultResponse
)
from ..auth import get_current_user
from ..agents.quiz_agent import QuizGenerationAndEvaluationAgent
from ..agents.progress_agent import ProgressMonitoringAndAdaptiveLearningAgent

router = APIRouter(prefix="/quiz", tags=["Quizzes & Practice"])

@router.post("/generate", response_model=QuizPublicResponse)
def generate_quiz(
    req: QuizGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    agent = QuizGenerationAndEvaluationAgent(db)
    quiz_data = agent.generate_quiz(
        user_id=current_user.id,
        subject_id=req.subject_id,
        topic_id=req.topic_id,
        topic_name=req.topic_name,
        difficulty=req.difficulty or "Medium",
        question_count=req.question_count or 5
    )
    return quiz_data

@router.post("/submit", response_model=QuizResultResponse)
def submit_quiz(
    req: QuizSubmitRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    quiz_agent = QuizGenerationAndEvaluationAgent(db)
    answers_dicts = [a.model_dump() for a in req.answers]

    # 1. Quiz Agent evaluates score and identifies misconceptions
    eval_result = quiz_agent.evaluate_quiz(
        user_id=current_user.id,
        quiz_id=req.quiz_id,
        answers=answers_dicts
    )

    # 2. Agent Handoff: Progress Monitoring Agent inspects student trajectory
    quiz = db.query(Quiz).filter(Quiz.id == req.quiz_id).first()
    subject_id = quiz.subject_id if quiz else 1

    progress_agent = ProgressMonitoringAndAdaptiveLearningAgent(db)
    prog_analysis = progress_agent.analyze_student_progress(
        user_id=current_user.id,
        subject_id=subject_id,
        latest_quiz_attempt_id=eval_result["attempt_id"]
    )

    return {
        "attempt_id": eval_result["attempt_id"],
        "quiz_id": eval_result["quiz_id"],
        "score": eval_result["score"],
        "total_questions": eval_result["total_questions"],
        "percentage": eval_result["percentage"],
        "passed": eval_result["passed"],
        "weak_concepts": eval_result["weak_concepts"],
        "questions_review": eval_result["questions_review"],
        "adaptive_recommendation": prog_analysis.get("recommendation"),
        "plan_revision_triggered": prog_analysis.get("adaptation_triggered", False)
    }

@router.get("/history")
def get_quiz_history(
    subject_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = (
        db.query(QuizAttempt)
        .join(Quiz, QuizAttempt.quiz_id == Quiz.id)
        .filter(QuizAttempt.user_id == current_user.id)
    )
    if subject_id:
        query = query.filter(Quiz.subject_id == subject_id)

    attempts = query.order_by(QuizAttempt.completed_at.desc()).limit(20).all()

    return [
        {
            "id": a.id,
            "quiz_id": a.quiz_id,
            "quiz_title": a.quiz.title if a.quiz else "Practice Quiz",
            "score": a.score,
            "total_questions": a.total_questions,
            "percentage": a.percentage,
            "completed_at": a.completed_at
        }
        for a in attempts
    ]
