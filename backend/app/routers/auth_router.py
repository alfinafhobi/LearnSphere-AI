from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, StudentGoal, Subject
from ..schemas import UserRegister, UserLogin, Token, UserResponse
from ..auth import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=Token)
def register(user_in: UserRegister, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A student with this email address already exists"
        )
    
    colors = ["#4F46E5", "#0ea5e9", "#10b981", "#8b5cf6", "#ec4899", "#f59e0b"]
    avatar_color = colors[len(user_in.email) % len(colors)]

    user = User(
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=hash_password(user_in.password),
        avatar_color=avatar_color
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Attach default student goal
    java_subj = db.query(Subject).filter(Subject.name == "Java Programming").first()
    goal = StudentGoal(
        user_id=user.id,
        subject_id=java_subj.id if java_subj else None,
        target_grade="A",
        available_hours_per_day=2.0,
        preferred_learning_style="Interactive & Practical"
    )
    db.add(goal)
    db.commit()

    token = create_access_token(data={"sub": str(user.id), "email": user.email})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user
    }

@router.post("/login", response_model=Token)
def login(user_in: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_in.email).first()
    if not user or not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    token = create_access_token(data={"sub": str(user.id), "email": user.email})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user
    }

@router.post("/demo-login", response_model=Token)
def demo_login(db: Session = Depends(get_db)):
    """One-click demo login for reviewers and college presentations."""
    user = db.query(User).filter(User.email == "demo@learnsphere.ai").first()
    if not user:
        user = User(
            email="demo@learnsphere.ai",
            full_name="Alex Rivera",
            hashed_password=hash_password("password123"),
            avatar_color="#6366F1"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    token = create_access_token(data={"sub": str(user.id), "email": user.email})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user
    }

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
