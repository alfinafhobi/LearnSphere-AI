from typing import TypedDict, List, Dict, Any, Optional

class AcademicAgentState(TypedDict, total=False):
    student_id: int
    subject_id: int
    subject_name: str
    available_hours: float
    goal_description: str
    
    # Assessment Agent data
    diagnostic_input: Optional[Dict[str, Any]]
    diagnostic_output: Optional[Dict[str, Any]]
    
    # Study Planner Agent data
    plan_output: Optional[Dict[str, Any]]
    human_approval_required: bool
    human_approved: bool
    
    # Tutor Agent data
    tutor_input: Optional[Dict[str, Any]]
    tutor_output: Optional[Dict[str, Any]]
    
    # Quiz Agent data
    quiz_input: Optional[Dict[str, Any]]
    quiz_output: Optional[Dict[str, Any]]
    
    # Progress & Adaptive Agent data
    progress_output: Optional[Dict[str, Any]]
    adaptation_triggered: bool
    
    # Execution Tracking & Collaboration Logs
    action_logs: List[Dict[str, Any]]
    current_step: str
    next_step: Optional[str]
    errors: List[str]
