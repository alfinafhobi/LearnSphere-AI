import json
import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from ..models import AgentActivityLog, TopicMastery, Topic, Subject

def log_agent_action(
    db: Session,
    user_id: int,
    agent_name: str,
    action: str,
    reasoning: str,
    decision: Optional[str] = None,
    state_cycle: str = "Act",
    input_data: Optional[Dict[str, Any]] = None,
    output_data: Optional[Dict[str, Any]] = None
) -> AgentActivityLog:
    """Persist an agent decision and reasoning step into the database."""
    log_entry = AgentActivityLog(
        user_id=user_id,
        agent_name=agent_name,
        action=action,
        reasoning=reasoning,
        decision=decision,
        state_cycle=state_cycle,
        input_data_json=json.dumps(input_data) if input_data else None,
        output_data_json=json.dumps(output_data) if output_data else None,
        timestamp=datetime.datetime.utcnow()
    )
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)
    return log_entry

def compute_proficiency_level(percentage: float) -> str:
    """Deterministic proficiency classification rules."""
    if percentage >= 80.0:
        return "Advanced"
    elif percentage >= 60.0:
        return "Intermediate"
    else:
        return "Beginner"

def update_topic_mastery(
    db: Session,
    user_id: int,
    topic_id: int,
    score_percentage: float
) -> TopicMastery:
    """Update or insert student mastery level for a specific topic."""
    mastery = db.query(TopicMastery).filter(
        TopicMastery.user_id == user_id,
        TopicMastery.topic_id == topic_id
    ).first()

    level = compute_proficiency_level(score_percentage)

    if mastery:
        # Running average of performance
        total_prev = mastery.score_percentage * mastery.attempts_count
        mastery.attempts_count += 1
        mastery.score_percentage = round((total_prev + score_percentage) / mastery.attempts_count, 1)
        mastery.proficiency_level = compute_proficiency_level(mastery.score_percentage)
        mastery.last_evaluated_at = datetime.datetime.utcnow()
    else:
        mastery = TopicMastery(
            user_id=user_id,
            topic_id=topic_id,
            proficiency_level=level,
            score_percentage=score_percentage,
            attempts_count=1,
            last_evaluated_at=datetime.datetime.utcnow()
        )
        db.add(mastery)

    db.commit()
    db.refresh(mastery)
    return mastery

def calculate_time_allocations(
    available_hours: float,
    topics_list: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Weighted time allocation:
    - Beginner / Weak topics get 50% extra study time
    - Intermediate topics get standard study time
    - Advanced topics get 30% reduced review time
    """
    total_minutes = int(available_hours * 60)
    
    # Calculate weights
    weights = []
    for t in topics_list:
        prof = t.get("proficiency", "Intermediate")
        if prof == "Beginner":
            weights.append(1.5)
        elif prof == "Advanced":
            weights.append(0.7)
        else:
            weights.append(1.0)
            
    sum_weights = sum(weights) if sum(weights) > 0 else 1.0
    allocations = []
    
    for i, t in enumerate(topics_list):
        allocated = int((weights[i] / sum_weights) * total_minutes)
        # Ensure reasonable bounds
        allocated = max(20, min(allocated, 75))
        priority = "High" if t.get("proficiency") == "Beginner" else ("Low" if t.get("proficiency") == "Advanced" else "Medium")
        allocations.append({
            "topic_id": t.get("id"),
            "topic_name": t.get("name"),
            "priority": priority,
            "estimated_minutes": allocated,
            "proficiency": t.get("proficiency", "Intermediate")
        })
        
    return allocations
