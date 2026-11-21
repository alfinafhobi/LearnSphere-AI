from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel

# Auth Schemas
class UserRegister(BaseModel):
    email: str
    full_name: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    avatar_color: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

# Goal Schemas
class StudentGoalCreate(BaseModel):
    subject_id: Optional[int] = None
    target_grade: str = "A"
    available_hours_per_day: float = 2.0
    preferred_learning_style: str = "Visual & Practical"
    academic_focus: Optional[str] = "Master foundational concepts and ace exams"

class StudentGoalResponse(BaseModel):
    id: int
    user_id: int
    subject_id: Optional[int] = None
    target_grade: str
    available_hours_per_day: float
    preferred_learning_style: str
    academic_focus: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Subject & Topic Schemas
class TopicResponse(BaseModel):
    id: int
    subject_id: int
    name: str
    order_index: int
    difficulty_level: str
    key_concepts: Optional[str] = None

    class Config:
        from_attributes = True

class SubjectResponse(BaseModel):
    id: int
    name: str
    code: str
    description: Optional[str] = None
    icon: str
    is_custom: bool
    topics: List[TopicResponse] = []

    class Config:
        from_attributes = True

class CustomSubjectCreate(BaseModel):
    name: str
    code: str
    description: Optional[str] = None
    topics: List[str]

# Assessment Schemas
class DiagnosticQuestionSchema(BaseModel):
    id: int
    topic_id: Optional[int] = None
    topic_name: Optional[str] = None
    question_text: str
    options: List[str]

class DiagnosticStartRequest(BaseModel):
    subject_id: int

class DiagnosticSubmitAnswer(BaseModel):
    question_id: int
    selected_option: str

class DiagnosticSubmitRequest(BaseModel):
    assessment_id: int
    answers: List[DiagnosticSubmitAnswer]

class DiagnosticEvaluationResponse(BaseModel):
    assessment_id: int
    score: float
    total_questions: int
    percentage: float
    strong_topics: List[str]
    weak_topics: List[str]
    proficiency_summary: Dict[str, str]
    recommendations: str
    generated_study_plan_id: Optional[int] = None

# Study Plan Schemas
class LearningResourceSchema(BaseModel):
    title: str
    platform: str
    resource_type: str
    url: str

class StudyTaskSchema(BaseModel):
    id: int
    topic_id: Optional[int] = None
    topic_name: Optional[str] = None
    title: str
    description: Optional[str] = None
    day_of_week: str
    estimated_minutes: int
    priority: str
    is_completed: bool
    resources: List[LearningResourceSchema] = []

    class Config:
        from_attributes = True

class StudyPlanResponse(BaseModel):
    id: int
    subject_id: int
    subject_name: Optional[str] = None
    title: str
    weekly_objectives: List[str]
    focus_topics: List[str]
    available_hours: float
    is_active: bool
    status: str
    adaptation_count: int
    pending_revision: Optional[Dict[str, Any]] = None
    tasks: List[StudyTaskSchema] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class StudyPlanGenerateRequest(BaseModel):
    subject_id: int
    available_hours: Optional[float] = 2.0
    learning_goal: Optional[str] = "Score top grades and master weak topics"

class StudyPlanApprovalRequest(BaseModel):
    study_plan_id: int
    approved: bool

# Tutor Schemas
class TutorChatRequest(BaseModel):
    subject_id: int
    topic_id: Optional[int] = None
    topic_name: Optional[str] = None
    message: str
    difficulty_level: Optional[str] = "Intermediate"  # Beginner, Intermediate, Advanced

class TutorChatResponse(BaseModel):
    reply: str
    recommended_next_topic: Optional[str] = None
    step_by_step_points: List[str] = []
    code_example: Optional[str] = None
    suggested_questions: List[str] = []
    agent_reasoning: str

# Quiz Schemas
class QuizGenerateRequest(BaseModel):
    subject_id: int
    topic_id: Optional[int] = None
    topic_name: Optional[str] = None
    difficulty: str = "Medium"  # Easy, Medium, Hard
    question_count: int = 5

class QuizQuestionPublic(BaseModel):
    id: int
    question_text: str
    options: List[str]
    key_concept: Optional[str] = None

class QuizPublicResponse(BaseModel):
    quiz_id: int
    subject_id: int
    subject_name: str
    topic_name: Optional[str] = None
    title: str
    difficulty: str
    questions: List[QuizQuestionPublic]

class QuizSubmitAnswer(BaseModel):
    question_id: int
    selected_option: str

class QuizSubmitRequest(BaseModel):
    quiz_id: int
    answers: List[QuizSubmitAnswer]

class QuestionReviewDetail(BaseModel):
    question_id: int
    question_text: str
    options: List[str]
    selected_option: str
    correct_option: str
    is_correct: bool
    explanation: str
    key_concept: Optional[str] = None

class QuizResultResponse(BaseModel):
    attempt_id: int
    quiz_id: int
    score: int
    total_questions: int
    percentage: float
    passed: bool
    weak_concepts: List[str]
    questions_review: List[QuestionReviewDetail]
    adaptive_recommendation: Optional[str] = None
    plan_revision_triggered: bool = False

# Analytics Schemas
class AnalyticsOverview(BaseModel):
    total_subjects: int
    completed_assessments: int
    total_quizzes_taken: int
    average_quiz_score: float
    study_streak_days: int
    tasks_completed: int
    total_tasks: int
    completion_rate: float
    weak_topics: List[Dict[str, Any]]
    strong_topics: List[Dict[str, Any]]
    performance_trends: List[Dict[str, Any]]
    subject_breakdown: List[Dict[str, Any]]
    recent_agent_decisions: List[str]

# Agent Activity Schemas
class AgentActivityLogResponse(BaseModel):
    id: int
    agent_name: str
    action: str
    reasoning: str
    decision: Optional[str] = None
    state_cycle: str
    input_data_json: Optional[str] = None
    output_data_json: Optional[str] = None
    timestamp: datetime

    class Config:
        from_attributes = True

class AgentWorkflowRunRequest(BaseModel):
    subject_id: int
    action_type: str = "full_cycle"  # diagnostic_to_plan, tutor_session, quiz_evaluate_adapt
