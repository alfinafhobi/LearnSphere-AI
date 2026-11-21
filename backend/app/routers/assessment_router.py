from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User
from ..schemas import (
    DiagnosticStartRequest,
    DiagnosticSubmitRequest,
    DiagnosticEvaluationResponse
)
from ..auth import get_current_user
from ..agents.assessment_agent import LearningAssessmentAgent
from ..agents.planner_agent import PersonalizedStudyPlannerAgent

router = APIRouter(prefix="/assessment", tags=["Diagnostic Assessment"])

@router.post("/start")
def start_diagnostic(
    req: DiagnosticStartRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    agent = LearningAssessmentAgent(db)
    result = agent.generate_diagnostic_test(
        user_id=current_user.id,
        subject_id=req.subject_id
    )
    return result

@router.post("/submit", response_model=DiagnosticEvaluationResponse)
def submit_diagnostic(
    req: DiagnosticSubmitRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    assessment_agent = LearningAssessmentAgent(db)
    answers_dicts = [a.model_dump() for a in req.answers]
    
    # 1. Assessment Agent evaluates performance & diagnoses weak topics
    eval_result = assessment_agent.evaluate_diagnostic_test(
        user_id=current_user.id,
        assessment_id=req.assessment_id,
        answers_data=answers_dicts
    )

    # 2. Agent Handoff: Study Planner Agent automatically constructs personalized study schedule
    planner_agent = PersonalizedStudyPlannerAgent(db)
    # Determine subject id from assessment
    from ..models import Assessment
    assessment = db.query(Assessment).filter(Assessment.id == req.assessment_id).first()
    subject_id = assessment.subject_id if assessment else 1

    plan_result = planner_agent.create_or_update_plan(
        user_id=current_user.id,
        subject_id=subject_id,
        available_hours=2.5,
        weak_topics=eval_result["weak_topics"],
        is_adaptive_revision=False
    )

    return {
        "assessment_id": eval_result["assessment_id"],
        "score": eval_result["score"],
        "total_questions": eval_result["total_questions"],
        "percentage": eval_result["percentage"],
        "strong_topics": eval_result["strong_topics"],
        "weak_topics": eval_result["weak_topics"],
        "proficiency_summary": eval_result["proficiency_summary"],
        "recommendations": eval_result["recommendations"],
        "generated_study_plan_id": plan_result.get("plan_id")
    }
