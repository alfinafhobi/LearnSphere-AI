from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Subject, Topic, User, TopicMastery
from ..schemas import SubjectResponse, CustomSubjectCreate
from ..auth import get_current_user

router = APIRouter(prefix="/subjects", tags=["Subjects & Curriculum"])

@router.get("", response_model=List[SubjectResponse])
def get_subjects(db: Session = Depends(get_db)):
    subjects = db.query(Subject).order_by(Subject.id).all()
    return subjects

@router.get("/{subject_id}", response_model=SubjectResponse)
def get_subject_detail(subject_id: int, db: Session = Depends(get_db)):
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    return subject

@router.post("/custom", response_model=SubjectResponse)
def create_custom_subject(
    data: CustomSubjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    existing = db.query(Subject).filter(Subject.name.ilike(data.name)).first()
    if existing:
        raise HTTPException(status_code=400, detail="A subject with this name already exists")

    subject = Subject(
        name=data.name,
        code=data.code.upper(),
        description=data.description or f"Custom curriculum for {data.name}",
        icon="Layers",
        is_custom=True
    )
    db.add(subject)
    db.flush()

    for idx, t_name in enumerate(data.topics):
        topic = Topic(
            subject_id=subject.id,
            name=t_name.strip(),
            order_index=idx + 1,
            difficulty_level="Medium",
            key_concepts=f"Core concepts of {t_name.strip()}"
        )
        db.add(topic)

    db.commit()
    db.refresh(subject)
    return subject
