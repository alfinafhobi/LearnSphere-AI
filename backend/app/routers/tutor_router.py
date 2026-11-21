from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, ChatHistory
from ..schemas import TutorChatRequest, TutorChatResponse
from ..auth import get_current_user
from ..agents.tutor_agent import IntelligentTutorAgent

router = APIRouter(prefix="/tutor", tags=["AI Tutor"])

@router.post("/chat", response_model=TutorChatResponse)
def tutor_chat(
    req: TutorChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    agent = IntelligentTutorAgent(db)
    response = agent.chat(
        user_id=current_user.id,
        subject_id=req.subject_id,
        message=req.message,
        topic_id=req.topic_id,
        topic_name=req.topic_name,
        difficulty_level=req.difficulty_level or "Intermediate"
    )
    return response

@router.get("/history")
def get_tutor_history(
    subject_id: Optional[int] = Query(None),
    limit: int = Query(20, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(ChatHistory).filter(ChatHistory.user_id == current_user.id)
    if subject_id:
        query = query.filter(ChatHistory.subject_id == subject_id)
        
    messages = query.order_by(ChatHistory.timestamp.asc()).limit(limit).all()
    
    return [
        {
            "id": m.id,
            "role": m.role,
            "content": m.content,
            "difficulty_level": m.difficulty_level,
            "timestamp": m.timestamp
        }
        for m in messages
    ]
