import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db
from app.seed_data import seed_database
from app.agents.assessment_agent import LearningAssessmentAgent
from app.agents.planner_agent import PersonalizedStudyPlannerAgent
from app.agents.quiz_agent import QuizGenerationAndEvaluationAgent
from app.agents.progress_agent import ProgressMonitoringAndAdaptiveLearningAgent
from app.agents.tutor_agent import IntelligentTutorAgent

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_learnsphere.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    seed_database(db)
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_demo_login():
    response = client.post("/api/v1/auth/demo-login")
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "demo@learnsphere.ai"

def test_subjects_listing():
    response = client.get("/api/v1/subjects")
    assert response.status_code == 200
    subjects = response.json()
    assert len(subjects) >= 5
    java = next(s for s in subjects if s["name"] == "Java Programming")
    assert len(java["topics"]) == 5

def test_agent_orchestration_cycle():
    db = TestingSessionLocal()
    try:
        # 1. Assessment Agent
        ass_agent = LearningAssessmentAgent(db)
        diag = ass_agent.generate_diagnostic_test(user_id=1, subject_id=1)
        assert "questions" in diag
        assert len(diag["questions"]) == 5

        # Evaluate with simulated low score in OOP
        answers = [{"question_id": q["id"], "selected_option": "D"} for q in diag["questions"]]
        eval_res = ass_agent.evaluate_diagnostic_test(user_id=1, assessment_id=diag["assessment_id"], answers_data=answers)
        assert eval_res["score"] <= 2.0
        assert len(eval_res["weak_topics"]) > 0

        # 2. Planner Agent
        planner = PersonalizedStudyPlannerAgent(db)
        plan_res = planner.create_or_update_plan(
            user_id=1,
            subject_id=1,
            available_hours=2.5,
            weak_topics=eval_res["weak_topics"]
        )
        assert "tasks" in plan_res
        assert len(plan_res["tasks"]) > 0

        # Verify high priority task exists for weak topics
        high_tasks = [t for t in plan_res["tasks"] if t["priority"] == "High"]
        assert len(high_tasks) > 0

        # Verify AI-recommended learning resources attached to tasks
        for task in plan_res["tasks"]:
            assert "resources" in task
            assert len(task["resources"]) >= 3
            for r in task["resources"]:
                assert "title" in r
                assert "platform" in r
                assert "resource_type" in r
                assert r["url"].startswith("http")

        # 3. Tutor Agent
        tutor = IntelligentTutorAgent(db)
        tutor_res = tutor.chat(user_id=1, subject_id=1, message="Explain polymorphism simply", difficulty_level="Beginner")
        assert "reply" in tutor_res
        assert len(tutor_res["step_by_step_points"]) > 0

        # 4. Quiz Agent
        quiz_agent = QuizGenerationAndEvaluationAgent(db)
        quiz_res = quiz_agent.generate_quiz(user_id=1, subject_id=1, difficulty="Medium", question_count=5)
        assert len(quiz_res["questions"]) == 5

        # Evaluate quiz
        q_answers = [{"question_id": q["id"], "selected_option": "A"} for q in quiz_res["questions"]]
        eval_quiz = quiz_agent.evaluate_quiz(user_id=1, quiz_id=quiz_res["quiz_id"], answers=q_answers)
        assert "percentage" in eval_quiz

        # 5. Progress Monitoring Agent
        progress_agent = ProgressMonitoringAndAdaptiveLearningAgent(db)
        prog_res = progress_agent.analyze_student_progress(user_id=1, subject_id=1, latest_quiz_attempt_id=eval_quiz["attempt_id"])
        assert "performance_trend" in prog_res
        assert "recommendation" in prog_res

    finally:
        db.close()
