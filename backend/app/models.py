import datetime
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Float
)
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    avatar_color = Column(String(50), default="#4F46E5")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    goals = relationship("StudentGoal", back_populates="user", cascade="all, delete-orphan")
    assessments = relationship("Assessment", back_populates="user", cascade="all, delete-orphan")
    study_plans = relationship("StudyPlan", back_populates="user", cascade="all, delete-orphan")
    quiz_attempts = relationship("QuizAttempt", back_populates="user", cascade="all, delete-orphan")
    topic_masteries = relationship("TopicMastery", back_populates="user", cascade="all, delete-orphan")
    chat_histories = relationship("ChatHistory", back_populates="user", cascade="all, delete-orphan")
    agent_logs = relationship("AgentActivityLog", back_populates="user", cascade="all, delete-orphan")


class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    code = Column(String(20), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    icon = Column(String(50), default="BookOpen")
    is_custom = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    topics = relationship("Topic", back_populates="subject", cascade="all, delete-orphan")
    assessments = relationship("Assessment", back_populates="subject")
    study_plans = relationship("StudyPlan", back_populates="subject")
    quizzes = relationship("Quiz", back_populates="subject")


class Topic(Base):
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    name = Column(String(150), nullable=False)
    order_index = Column(Integer, default=0)
    difficulty_level = Column(String(50), default="Medium")  # Easy, Medium, Hard
    key_concepts = Column(Text, nullable=True)  # JSON or comma-separated string
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    subject = relationship("Subject", back_populates="topics")
    tasks = relationship("StudyTask", back_populates="topic")
    masteries = relationship("TopicMastery", back_populates="topic")
    quizzes = relationship("Quiz", back_populates="topic")


class StudentGoal(Base):
    __tablename__ = "student_goals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=True)
    target_grade = Column(String(10), default="A")  # A+, A, B, etc.
    available_hours_per_day = Column(Float, default=2.0)
    preferred_learning_style = Column(String(50), default="Visual & Practical")
    academic_focus = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    user = relationship("User", back_populates="goals")
    subject = relationship("Subject")


class Assessment(Base):
    __tablename__ = "assessments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    score = Column(Float, default=0.0)
    total_questions = Column(Integer, default=5)
    percentage = Column(Float, default=0.0)
    strong_topics = Column(Text, default="[]")  # JSON string list
    weak_topics = Column(Text, default="[]")    # JSON string list
    proficiency_summary = Column(Text, default="{}")  # JSON topic -> level
    recommendations = Column(Text, nullable=True)
    completed_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="assessments")
    subject = relationship("Subject", back_populates="assessments")
    questions = relationship("AssessmentQuestion", back_populates="assessment", cascade="all, delete-orphan")
    answers = relationship("AssessmentAnswer", back_populates="assessment", cascade="all, delete-orphan")


class AssessmentQuestion(Base):
    __tablename__ = "assessment_questions"

    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id"), nullable=False)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=True)
    question_text = Column(Text, nullable=False)
    options_json = Column(Text, nullable=False)  # JSON array of strings
    correct_option = Column(String(10), nullable=False)
    explanation = Column(Text, nullable=True)

    assessment = relationship("Assessment", back_populates="questions")
    topic = relationship("Topic")
    answers = relationship("AssessmentAnswer", back_populates="question")


class AssessmentAnswer(Base):
    __tablename__ = "assessment_answers"

    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("assessment_questions.id"), nullable=False)
    selected_option = Column(String(10), nullable=False)
    is_correct = Column(Boolean, default=False)

    assessment = relationship("Assessment", back_populates="answers")
    question = relationship("AssessmentQuestion", back_populates="answers")


class StudyPlan(Base):
    __tablename__ = "study_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    title = Column(String(255), nullable=False)
    weekly_objectives = Column(Text, default="[]")  # JSON list
    focus_topics = Column(Text, default="[]")      # JSON list
    available_hours = Column(Float, default=2.0)
    is_active = Column(Boolean, default=True)
    adaptation_count = Column(Integer, default=0)
    status = Column(String(50), default="Active")  # Active, Pending_Approval, Completed, Revised
    pending_revision_json = Column(Text, nullable=True)  # JSON of proposed plan waiting for human approval
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    user = relationship("User", back_populates="study_plans")
    subject = relationship("Subject", back_populates="study_plans")
    tasks = relationship("StudyTask", back_populates="study_plan", cascade="all, delete-orphan")


class StudyTask(Base):
    __tablename__ = "study_tasks"

    id = Column(Integer, primary_key=True, index=True)
    study_plan_id = Column(Integer, ForeignKey("study_plans.id"), nullable=False)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    day_of_week = Column(String(20), default="Monday")  # Monday ... Sunday
    estimated_minutes = Column(Integer, default=30)
    priority = Column(String(20), default="Medium")    # High, Medium, Low
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)
    learning_resources_json = Column(Text, default="[]")  # JSON list of recommended resources

    study_plan = relationship("StudyPlan", back_populates="tasks")
    topic = relationship("Topic", back_populates="tasks")


class Quiz(Base):
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=True)
    title = Column(String(255), nullable=False)
    difficulty = Column(String(20), default="Medium")  # Easy, Medium, Hard
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    subject = relationship("Subject", back_populates="quizzes")
    topic = relationship("Topic", back_populates="quizzes")
    questions = relationship("QuizQuestion", back_populates="quiz", cascade="all, delete-orphan")
    attempts = relationship("QuizAttempt", back_populates="quiz", cascade="all, delete-orphan")


class QuizQuestion(Base):
    __tablename__ = "quiz_questions"

    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False)
    question_text = Column(Text, nullable=False)
    options_json = Column(Text, nullable=False)  # JSON array
    correct_option = Column(String(10), nullable=False)
    explanation = Column(Text, nullable=False)
    key_concept = Column(String(150), nullable=True)

    quiz = relationship("Quiz", back_populates="questions")
    responses = relationship("StudentResponse", back_populates="question")


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    score = Column(Integer, default=0)
    total_questions = Column(Integer, default=0)
    percentage = Column(Float, default=0.0)
    weak_concepts = Column(Text, default="[]")  # JSON string list
    completed_at = Column(DateTime, default=datetime.datetime.utcnow)

    quiz = relationship("Quiz", back_populates="attempts")
    user = relationship("User", back_populates="quiz_attempts")
    responses = relationship("StudentResponse", back_populates="attempt", cascade="all, delete-orphan")


class StudentResponse(Base):
    __tablename__ = "student_responses"

    id = Column(Integer, primary_key=True, index=True)
    quiz_attempt_id = Column(Integer, ForeignKey("quiz_attempts.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("quiz_questions.id"), nullable=False)
    selected_option = Column(String(10), nullable=False)
    is_correct = Column(Boolean, default=False)

    attempt = relationship("QuizAttempt", back_populates="responses")
    question = relationship("QuizQuestion", back_populates="responses")


class TopicMastery(Base):
    __tablename__ = "topic_mastery"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    proficiency_level = Column(String(30), default="Beginner")  # Beginner, Intermediate, Advanced
    score_percentage = Column(Float, default=0.0)
    attempts_count = Column(Integer, default=0)
    last_evaluated_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="topic_masteries")
    topic = relationship("Topic", back_populates="masteries")


class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=True)
    role = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    difficulty_level = Column(String(30), default="Intermediate")
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="chat_histories")
    subject = relationship("Subject")
    topic = relationship("Topic")


class AgentActivityLog(Base):
    __tablename__ = "agent_activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    agent_name = Column(String(100), nullable=False)  # Assessment, Planner, Tutor, Quiz, Progress Monitoring
    action = Column(String(255), nullable=False)
    reasoning = Column(Text, nullable=False)
    decision = Column(String(255), nullable=True)
    state_cycle = Column(String(50), default="Act")  # Observe, Analyze, Plan, Act, Evaluate, Adapt
    input_data_json = Column(Text, nullable=True)
    output_data_json = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="agent_logs")
