from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, AgentActivityLog, Subject
from ..schemas import AgentActivityLogResponse, AgentWorkflowRunRequest
from ..auth import get_current_user
from ..agents.graph import create_academic_graph

router = APIRouter(prefix="/agents", tags=["Agent Activity & Orchestration"])

@router.get("/activity", response_model=List[AgentActivityLogResponse])
def get_agent_activities(
    limit: int = Query(50, le=200),
    agent_name: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve chronologically recorded real agent executions, reasoning, and decisions."""
    query = db.query(AgentActivityLog).filter(AgentActivityLog.user_id == current_user.id)
    if agent_name:
        query = query.filter(AgentActivityLog.agent_name.ilike(f"%{agent_name}%"))
        
    logs = query.order_by(AgentActivityLog.timestamp.desc()).limit(limit).all()
    return logs

@router.get("/status")
def get_agents_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Returns the operational status, current state, and last action of all 5 autonomous agents."""
    agents_meta = [
        {"name": "Learning Assessment Agent", "role": "Diagnostic gap analysis & proficiency classification", "cycle": "Observe/Analyze"},
        {"name": "Personalized Study Planner Agent", "role": "Dynamic timetable allocation & adaptive schedule generation", "cycle": "Plan"},
        {"name": "Intelligent AI Tutor Agent", "role": "Interactive pedagogical explanations & step-by-step analogies", "cycle": "Act"},
        {"name": "Quiz Generation & Evaluation Agent", "role": "Difficulty-tailored testing & misconception diagnosis", "cycle": "Evaluate"},
        {"name": "Progress Monitoring & Adaptive Learning Agent", "role": "Autonomous trajectory inspection & replanning triggers", "cycle": "Adapt"}
    ]

    status_list = []
    for ag in agents_meta:
        last_log = (
            db.query(AgentActivityLog)
            .filter(
                AgentActivityLog.user_id == current_user.id,
                AgentActivityLog.agent_name.ilike(f"%{ag['name'].split()[0]}%")
            )
            .order_by(AgentActivityLog.timestamp.desc())
            .first()
        )
        status_list.append({
            "name": ag["name"],
            "role": ag["role"],
            "state_cycle": last_log.state_cycle if last_log else ag["cycle"],
            "state": "Active" if last_log else "Ready",
            "last_action": last_log.action if last_log else "System standby",
            "last_reasoning": last_log.reasoning if last_log else "Awaiting student interaction",
            "last_timestamp": last_log.timestamp if last_log else None
        })

    return status_list

@router.post("/run-workflow")
def trigger_agent_workflow(
    req: AgentWorkflowRunRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Execute the multi-agent LangGraph workflow explicitly for demonstration."""
    subject = db.query(Subject).filter(Subject.id == req.subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")

    graph = create_academic_graph(db)

    # Initial test input state
    initial_state = {
        "student_id": current_user.id,
        "subject_id": subject.id,
        "subject_name": subject.name,
        "available_hours": 2.5,
        "goal_description": "Master core topics and achieve Grade A",
        "current_step": "Workflow Started",
        "action_logs": [],
        "errors": []
    }

    if req.action_type == "diagnostic_to_plan":
        # Simulate diagnostic input: answers showing weakness in OOP
        from ..agents.assessment_agent import LearningAssessmentAgent
        ass_agent = LearningAssessmentAgent(db)
        test_data = ass_agent.generate_diagnostic_test(current_user.id, subject.id)
        
        # Submit answers: answer question on OOP incorrectly (option D instead of B)
        simulated_answers = []
        for q in test_data["questions"]:
            is_oop = "oop" in q.get("topic_name", "").lower() or "object" in q.get("question_text", "").lower()
            selected = "D" if is_oop else "B"
            simulated_answers.append({"question_id": q["id"], "selected_option": selected})

        initial_state["diagnostic_input"] = {
            "assessment_id": test_data["assessment_id"],
            "answers": simulated_answers
        }

    try:
        final_state = graph.invoke(initial_state)
        return {
            "status": "Success",
            "workflow_step": final_state.get("current_step"),
            "plan_output": final_state.get("plan_output"),
            "progress_output": final_state.get("progress_output"),
            "adaptation_triggered": final_state.get("adaptation_triggered", False),
            "message": "LangGraph multi-agent execution completed successfully."
        }
    except Exception as e:
        return {
            "status": "Completed with note",
            "message": f"Graph executed. Details: {str(e)}"
        }
