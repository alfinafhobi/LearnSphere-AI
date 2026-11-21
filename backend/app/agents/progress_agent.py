import json
import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from ..models import QuizAttempt, Quiz, TopicMastery, Topic, StudyPlan, AgentActivityLog
from .tools import log_agent_action, compute_proficiency_level
from .planner_agent import PersonalizedStudyPlannerAgent

class ProgressMonitoringAndAdaptiveLearningAgent:
    """
    Agent 5: Progress Monitoring and Adaptive Learning Agent
    Responsibilities:
    - Continuously monitor student learning progress
    - Analyze quiz scores and assessment history
    - Identify recurring mistakes & detect improving or declining trends
    - Automatically recommend study-plan modifications
    - Coordinate with the Study Planner Agent to adjust timetable & priorities
    - Demonstrate the complete loop: Observe -> Analyze -> Plan -> Act -> Evaluate -> Adapt
    """

    def __init__(self, db: Session):
        self.db = db
        self.name = "Progress Monitoring & Adaptive Learning Agent"

    def analyze_student_progress(
        self,
        user_id: int,
        subject_id: int,
        latest_quiz_attempt_id: Optional[int] = None
    ) -> Dict[str, Any]:
        # Fetch recent attempts for this subject
        attempts = (
            self.db.query(QuizAttempt)
            .join(Quiz, QuizAttempt.quiz_id == Quiz.id)
            .filter(QuizAttempt.user_id == user_id, Quiz.subject_id == subject_id)
            .order_by(QuizAttempt.completed_at.desc())
            .limit(5)
            .all()
        )

        # Get latest attempt
        latest_attempt = None
        if latest_quiz_attempt_id:
            latest_attempt = self.db.query(QuizAttempt).filter(QuizAttempt.id == latest_quiz_attempt_id).first()
        elif attempts:
            latest_attempt = attempts[0]

        # Analyze performance trend
        scores = [a.percentage for a in attempts]
        avg_score = round(sum(scores) / len(scores), 1) if scores else 0.0

        trend = "Stable"
        if len(scores) >= 2:
            if scores[0] > scores[1]:
                trend = "Improving"
            elif scores[0] < scores[1]:
                trend = "Declining"

        # Check weak topics from masteries
        masteries = (
            self.db.query(TopicMastery)
            .join(Topic, TopicMastery.topic_id == Topic.id)
            .filter(TopicMastery.user_id == user_id, Topic.subject_id == subject_id)
            .all()
        )

        weak_topics = []
        improving_topics = []
        strong_topics = []

        for m in masteries:
            t_name = m.topic.name if m.topic else "Unknown Topic"
            if m.proficiency_level == "Beginner" or m.score_percentage < 60.0:
                weak_topics.append(t_name)
            elif m.proficiency_level == "Advanced" or m.score_percentage >= 80.0:
                strong_topics.append(t_name)
            else:
                improving_topics.append(t_name)

        # Adaptive Decision Logic:
        # If latest attempt scored < 60% or weak topics persist, trigger study plan adaptation!
        needs_adaptation = False
        adaptation_reason = ""
        latest_score = latest_attempt.percentage if latest_attempt else 0.0

        if latest_attempt and latest_score < 60.0:
            needs_adaptation = True
            adaptation_reason = f"Recent quiz score of {latest_score}% fell below the 60% mastery threshold."
        elif weak_topics:
            needs_adaptation = True
            adaptation_reason = f"Detected lingering knowledge gaps in: {', '.join(weak_topics)}."

        adaptive_rec = ""
        plan_updated = False
        plan_id = None

        if needs_adaptation:
            adaptive_rec = (
                f"Autonomous Adaptation Triggered: {adaptation_reason} "
                f"Reprioritizing study timetable to allocate maximum focus to {', '.join(weak_topics) or 'critical modules'}."
            )

            # Delegate to Study Planner Agent to automatically adapt schedule!
            planner = PersonalizedStudyPlannerAgent(self.db)
            plan_result = planner.create_or_update_plan(
                user_id=user_id,
                subject_id=subject_id,
                available_hours=2.5,
                weak_topics=weak_topics,
                is_adaptive_revision=True,
                require_approval=True  # Human in the loop!
            )
            plan_updated = True
            plan_id = plan_result.get("plan_id")

            # Log Agent Adaptation Decision
            log_agent_action(
                db=self.db,
                user_id=user_id,
                agent_name=self.name,
                action=f"Trigger Adaptive Study-Plan Revision (Trend: {trend})",
                reasoning=f"Identified score drop / weak topics: {weak_topics}. Coordinated with Study Planner Agent to increase study duration and prioritize foundational exercises.",
                decision="Generated proposed revision for student approval",
                state_cycle="Adapt",
                input_data={"latest_score": latest_score, "weak_topics": weak_topics},
                output_data={"plan_id": plan_id, "recommendation": adaptive_rec}
            )
        else:
            adaptive_rec = "Student demonstrating steady mastery. Maintaining active study plan schedule with recommended advanced challenges."
            log_agent_action(
                db=self.db,
                user_id=user_id,
                agent_name=self.name,
                action=f"Continuous Monitoring: Steady Progress (Avg: {avg_score}%)",
                reasoning=f"Analyzed latest {len(attempts)} attempts. Performance is healthy and mastery levels are trending positive.",
                decision="Keep current plan active",
                state_cycle="Evaluate",
                output_data={"avg_score": avg_score, "trend": trend}
            )

        return {
            "average_score": avg_score,
            "performance_trend": trend,
            "weak_topics": weak_topics,
            "improving_topics": improving_topics,
            "strong_topics": strong_topics,
            "adaptation_triggered": needs_adaptation,
            "adaptation_reason": adaptation_reason,
            "recommendation": adaptive_rec,
            "plan_updated": plan_updated,
            "plan_id": plan_id
        }
