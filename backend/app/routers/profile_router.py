from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, StudentGoal, Subject
from ..schemas import StudentGoalCreate, StudentGoalResponse, UserResponse
from ..auth import get_current_user

router = APIRouter(prefix="/profile", tags=["Student Profile"])

@router.get("")
def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    goal = db.query(StudentGoal).filter(StudentGoal.user_id == current_user.id).first()
    if not goal:
        goal = StudentGoal(
            user_id=current_user.id,
            target_grade="A",
            available_hours_per_day=2.0,
            preferred_learning_style="Interactive & Practical",
            academic_focus="Master foundational concepts and ace exams"
        )
        db.add(goal)
        db.commit()
        db.refresh(goal)

    subject_name = goal.subject.name if goal.subject else "Java Programming"

    return {
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "full_name": current_user.full_name,
            "avatar_color": current_user.avatar_color,
            "created_at": current_user.created_at
        },
        "goal": {
            "id": goal.id,
            "target_grade": goal.target_grade,
            "available_hours_per_day": goal.available_hours_per_day,
            "preferred_learning_style": goal.preferred_learning_style,
            "academic_focus": goal.academic_focus,
            "subject_name": subject_name
        }
    }

@router.put("/goal")
def update_goal(
    goal_in: StudentGoalCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    goal = db.query(StudentGoal).filter(StudentGoal.user_id == current_user.id).first()
    if not goal:
        goal = StudentGoal(user_id=current_user.id)
        db.add(goal)

    goal.target_grade = goal_in.target_grade
    goal.available_hours_per_day = goal_in.available_hours_per_day
    goal.preferred_learning_style = goal_in.preferred_learning_style
    goal.academic_focus = goal_in.academic_focus
    if goal_in.subject_id:
        goal.subject_id = goal_in.subject_id

    db.commit()
    db.refresh(goal)

    return {"status": "Success", "message": "Academic goals updated successfully"}
