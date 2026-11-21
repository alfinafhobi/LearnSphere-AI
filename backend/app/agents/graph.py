import json
from typing import Dict, Any
from langgraph.graph import StateGraph, END
from sqlalchemy.orm import Session

from .state import AcademicAgentState
from .assessment_agent import LearningAssessmentAgent
from .planner_agent import PersonalizedStudyPlannerAgent
from .tutor_agent import IntelligentTutorAgent
from .quiz_agent import QuizGenerationAndEvaluationAgent
from .progress_agent import ProgressMonitoringAndAdaptiveLearningAgent

def create_academic_graph(db: Session):
    """
    Constructs the multi-agent LangGraph orchestration graph.
    Demonstrates: Observe -> Analyze -> Plan -> Act -> Evaluate -> Adapt
    """

    assessment_agent = LearningAssessmentAgent(db)
    planner_agent = PersonalizedStudyPlannerAgent(db)
    tutor_agent = IntelligentTutorAgent(db)
    quiz_agent = QuizGenerationAndEvaluationAgent(db)
    progress_agent = ProgressMonitoringAndAdaptiveLearningAgent(db)

    # 1. Assessment Node
    def assessment_node(state: AcademicAgentState) -> Dict[str, Any]:
        student_id = state.get("student_id")
        diag_in = state.get("diagnostic_input") or {}
        assessment_id = diag_in.get("assessment_id")
        answers = diag_in.get("answers", [])

        if assessment_id and answers:
            diag_out = assessment_agent.evaluate_diagnostic_test(
                user_id=student_id,
                assessment_id=assessment_id,
                answers_data=answers
            )
            return {
                "diagnostic_output": diag_out,
                "current_step": "Assessment Evaluated",
                "next_step": "planner"
            }
        return {"current_step": "Assessment Skipped"}

    # 2. Planner Node
    def planner_node(state: AcademicAgentState) -> Dict[str, Any]:
        student_id = state.get("student_id")
        subject_id = state.get("subject_id")
        diag_out = state.get("diagnostic_output") or {}
        weak_topics = diag_out.get("weak_topics", [])
        avail_hours = state.get("available_hours", 2.0)
        is_adaptive = state.get("adaptation_triggered", False)

        plan_res = planner_agent.create_or_update_plan(
            user_id=student_id,
            subject_id=subject_id,
            available_hours=avail_hours,
            weak_topics=weak_topics,
            is_adaptive_revision=is_adaptive,
            require_approval=is_adaptive
        )
        return {
            "plan_output": plan_res,
            "human_approval_required": plan_res.get("status") == "Pending_Approval",
            "current_step": "Plan Created/Updated",
            "next_step": "tutor" if not is_adaptive else "end"
        }

    # 3. Tutor Node
    def tutor_node(state: AcademicAgentState) -> Dict[str, Any]:
        student_id = state.get("student_id")
        subject_id = state.get("subject_id")
        tutor_in = state.get("tutor_input") or {}
        msg = tutor_in.get("message", "Explain the primary foundational concepts.")
        t_id = tutor_in.get("topic_id")
        t_name = tutor_in.get("topic_name")

        tutor_res = tutor_agent.chat(
            user_id=student_id,
            subject_id=subject_id,
            message=msg,
            topic_id=t_id,
            topic_name=t_name
        )
        return {
            "tutor_output": tutor_res,
            "current_step": "Tutor Session Completed",
            "next_step": "quiz"
        }

    # 4. Quiz Node
    def quiz_node(state: AcademicAgentState) -> Dict[str, Any]:
        student_id = state.get("student_id")
        q_in = state.get("quiz_input") or {}
        quiz_id = q_in.get("quiz_id")
        answers = q_in.get("answers", [])

        if quiz_id and answers:
            quiz_res = quiz_agent.evaluate_quiz(
                user_id=student_id,
                quiz_id=quiz_id,
                answers=answers
            )
            return {
                "quiz_output": quiz_res,
                "current_step": "Quiz Evaluated",
                "next_step": "progress"
            }
        return {"current_step": "Quiz Skipped"}

    # 5. Progress & Adaptive Node
    def progress_node(state: AcademicAgentState) -> Dict[str, Any]:
        student_id = state.get("student_id")
        subject_id = state.get("subject_id")
        quiz_out = state.get("quiz_output") or {}
        attempt_id = quiz_out.get("attempt_id")

        prog_res = progress_agent.analyze_student_progress(
            user_id=student_id,
            subject_id=subject_id,
            latest_quiz_attempt_id=attempt_id
        )

        adaptation_needed = prog_res.get("adaptation_triggered", False)
        return {
            "progress_output": prog_res,
            "adaptation_triggered": adaptation_needed,
            "current_step": "Progress Evaluated",
            "next_step": "planner" if adaptation_needed else "end"
        }

    # Conditional Routing Functions
    def route_after_assessment(state: AcademicAgentState) -> str:
        return "planner"

    def route_after_progress(state: AcademicAgentState) -> str:
        if state.get("adaptation_triggered"):
            return "planner"
        return END

    def entry_router(state: AcademicAgentState) -> str:
        if state.get("diagnostic_input"):
            return "assessment"
        elif state.get("quiz_input"):
            return "quiz"
        elif state.get("tutor_input"):
            return "tutor"
        elif state.get("adaptation_triggered"):
            return "planner"
        return "assessment"

    # Assemble State Graph
    workflow = StateGraph(AcademicAgentState)

    workflow.add_node("assessment", assessment_node)
    workflow.add_node("planner", planner_node)
    workflow.add_node("tutor", tutor_node)
    workflow.add_node("quiz", quiz_node)
    workflow.add_node("progress", progress_node)

    # Set conditional entry point
    workflow.set_conditional_entry_point(
        entry_router,
        {
            "assessment": "assessment",
            "planner": "planner",
            "tutor": "tutor",
            "quiz": "quiz"
        }
    )

    workflow.add_edge("assessment", "planner")
    workflow.add_edge("planner", END)
    workflow.add_edge("tutor", END)
    workflow.add_edge("quiz", "progress")
    workflow.add_conditional_edges(
        "progress",
        route_after_progress,
        {
            "planner": "planner",
            END: END
        }
    )

    return workflow.compile()
