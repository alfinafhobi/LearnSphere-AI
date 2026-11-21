import json
import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, StudyPlan, StudyTask, Subject
from ..schemas import (
    StudyPlanResponse,
    StudyPlanGenerateRequest,
    StudyPlanApprovalRequest
)
from ..auth import get_current_user
from ..agents.planner_agent import PersonalizedStudyPlannerAgent

router = APIRouter(prefix="/study-plans", tags=["Study Planner"])

@router.get("/current", response_model=StudyPlanResponse)
def get_current_study_plan(
    subject_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(StudyPlan).filter(
        StudyPlan.user_id == current_user.id,
        StudyPlan.is_active == True
    )
    if subject_id:
        query = query.filter(StudyPlan.subject_id == subject_id)
    
    plan = query.order_by(StudyPlan.updated_at.desc()).first()

    if not plan:
        # If no active plan, auto-generate default baseline plan for subject
        target_subject = None
        if subject_id:
            target_subject = db.query(Subject).filter(Subject.id == subject_id).first()
        if not target_subject:
            target_subject = db.query(Subject).first()

        if target_subject:
            agent = PersonalizedStudyPlannerAgent(db)
            res = agent.create_or_update_plan(
                user_id=current_user.id,
                subject_id=target_subject.id,
                available_hours=2.0
            )
            plan = db.query(StudyPlan).filter(StudyPlan.id == res["plan_id"]).first()

    if not plan:
        raise HTTPException(status_code=404, detail="No study plan found. Please select a subject.")

    # Prepare response
    tasks = db.query(StudyTask).filter(StudyTask.study_plan_id == plan.id).order_by(StudyTask.id).all()
    tasks_schema = []
    for t in tasks:
        resources = []
        if getattr(t, "learning_resources_json", None):
            try:
                resources = json.loads(t.learning_resources_json)
            except Exception:
                resources = []

        # If legacy task has no resources stored, auto-populate dynamically
        if not resources:
            from ..agents.planner_agent import recommend_learning_resources
            topic_name = t.topic.name if t.topic else "General Concepts"
            subj_name = plan.subject.name if plan.subject else "General"
            resources = recommend_learning_resources(
                subject_name=subj_name,
                topic_name=topic_name,
                proficiency="Beginner" if t.priority == "High" else "Intermediate",
                priority=t.priority
            )
            t.learning_resources_json = json.dumps(resources)
            db.commit()

        tasks_schema.append({
            "id": t.id,
            "topic_id": t.topic_id,
            "topic_name": t.topic.name if t.topic else "General",
            "title": t.title,
            "description": t.description,
            "day_of_week": t.day_of_week,
            "estimated_minutes": t.estimated_minutes,
            "priority": t.priority,
            "is_completed": t.is_completed,
            "resources": resources
        })

    pending_rev = json.loads(plan.pending_revision_json) if plan.pending_revision_json else None

    return {
        "id": plan.id,
        "subject_id": plan.subject_id,
        "subject_name": plan.subject.name if plan.subject else "General",
        "title": plan.title,
        "weekly_objectives": json.loads(plan.weekly_objectives or "[]"),
        "focus_topics": json.loads(plan.focus_topics or "[]"),
        "available_hours": plan.available_hours,
        "is_active": plan.is_active,
        "status": plan.status,
        "adaptation_count": plan.adaptation_count,
        "pending_revision": pending_rev,
        "tasks": tasks_schema,
        "created_at": plan.created_at,
        "updated_at": plan.updated_at
    }

@router.post("/generate", response_model=StudyPlanResponse)
def generate_study_plan(
    req: StudyPlanGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    agent = PersonalizedStudyPlannerAgent(db)
    res = agent.create_or_update_plan(
        user_id=current_user.id,
        subject_id=req.subject_id,
        available_hours=req.available_hours or 2.0,
        learning_goal=req.learning_goal
    )
    return get_current_study_plan(subject_id=req.subject_id, current_user=current_user, db=db)

@router.patch("/tasks/{task_id}/toggle")
def toggle_study_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    task = (
        db.query(StudyTask)
        .join(StudyPlan, StudyTask.study_plan_id == StudyPlan.id)
        .filter(StudyTask.id == task_id, StudyPlan.user_id == current_user.id)
        .first()
    )
    if not task:
        raise HTTPException(status_code=404, detail="Study task not found")

    task.is_completed = not task.is_completed
    task.completed_at = datetime.datetime.utcnow() if task.is_completed else None
    db.commit()

    return {"task_id": task.id, "is_completed": task.is_completed}

@router.post("/approve-revision")
def approve_revision(
    req: StudyPlanApprovalRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    agent = PersonalizedStudyPlannerAgent(db)
    result = agent.approve_pending_plan(
        user_id=current_user.id,
        plan_id=req.study_plan_id,
        approved=req.approved
    )
    return result
