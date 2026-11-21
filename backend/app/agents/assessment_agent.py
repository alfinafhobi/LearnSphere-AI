import json
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from ..models import Subject, Topic, Assessment, AssessmentQuestion, AssessmentAnswer
from .tools import log_agent_action, update_topic_mastery, compute_proficiency_level
from ..seed_data import DIAGNOSTIC_QUESTIONS

class LearningAssessmentAgent:
    """
    Agent 1: Learning Assessment Agent
    Responsibilities:
    - Assess students' existing knowledge
    - Generate diagnostic questions
    - Evaluate submitted answers
    - Identify knowledge gaps & topic proficiency (Beginner, Intermediate, Advanced)
    - Recommend next steps and hand off to Study Planner Agent
    """

    def __init__(self, db: Session):
        self.db = db
        self.name = "Learning Assessment Agent"

    def generate_diagnostic_test(self, user_id: int, subject_id: int) -> Dict[str, Any]:
        subject = self.db.query(Subject).filter(Subject.id == subject_id).first()
        if not subject:
            raise ValueError(f"Subject with id {subject_id} not found")

        topics = self.db.query(Topic).filter(Topic.subject_id == subject_id).order_by(Topic.order_index).all()
        
        # Check if pre-seeded diagnostic questions exist for subject
        seed_questions = DIAGNOSTIC_QUESTIONS.get(subject.name, [])

        assessment = Assessment(
            user_id=user_id,
            subject_id=subject_id,
            total_questions=len(topics) if len(topics) > 0 else 5,
            proficiency_summary=json.dumps({})
        )
        self.db.add(assessment)
        self.db.flush()

        questions_payload = []

        if seed_questions and len(seed_questions) >= len(topics):
            for i, sq in enumerate(seed_questions):
                matching_topic = next((t for t in topics if t.name == sq["topic"]), topics[i % len(topics)] if topics else None)
                q_model = AssessmentQuestion(
                    assessment_id=assessment.id,
                    topic_id=matching_topic.id if matching_topic else None,
                    question_text=sq["question"],
                    options_json=json.dumps(sq["options"]),
                    correct_option=sq["correct"],
                    explanation=sq["explanation"]
                )
                self.db.add(q_model)
                self.db.flush()
                questions_payload.append({
                    "id": q_model.id,
                    "topic_id": matching_topic.id if matching_topic else None,
                    "topic_name": matching_topic.name if matching_topic else sq["topic"],
                    "question_text": sq["question"],
                    "options": sq["options"]
                })
        else:
            # Fallback dynamic questions generator for custom/other subjects
            for i, topic in enumerate(topics):
                opts = [
                    f"A) Foundational principle of {topic.name}",
                    f"B) Secondary utility pattern for {topic.name}",
                    f"C) Anti-pattern in {topic.name}",
                    f"D) Deprecated runtime syntax for {topic.name}"
                ]
                q_model = AssessmentQuestion(
                    assessment_id=assessment.id,
                    topic_id=topic.id,
                    question_text=f"Which architectural principle is paramount when designing solutions with {topic.name} ({topic.key_concepts or 'core principles'})?",
                    options_json=json.dumps(opts),
                    correct_option="A",
                    explanation=f"Foundational principle of {topic.name} ensures optimal cohesion and predictable state transitions."
                )
                self.db.add(q_model)
                self.db.flush()
                questions_payload.append({
                    "id": q_model.id,
                    "topic_id": topic.id,
                    "topic_name": topic.name,
                    "question_text": q_model.question_text,
                    "options": opts
                })

        self.db.commit()

        # Log agent observation
        log_agent_action(
            db=self.db,
            user_id=user_id,
            agent_name=self.name,
            action=f"Generate Diagnostic Test for {subject.name}",
            reasoning=f"Generated {len(questions_payload)} comprehensive diagnostic questions across all core topics of {subject.name}.",
            decision="Awaiting student submission for gap analysis",
            state_cycle="Observe",
            output_data={"assessment_id": assessment.id, "questions_count": len(questions_payload)}
        )

        return {
            "assessment_id": assessment.id,
            "subject_id": subject.id,
            "subject_name": subject.name,
            "questions": questions_payload
        }

    def evaluate_diagnostic_test(self, user_id: int, assessment_id: int, answers_data: List[Dict[str, str]]) -> Dict[str, Any]:
        assessment = self.db.query(Assessment).filter(
            Assessment.id == assessment_id,
            Assessment.user_id == user_id
        ).first()

        if not assessment:
            raise ValueError(f"Assessment {assessment_id} not found for student")

        questions = self.db.query(AssessmentQuestion).filter(AssessmentQuestion.assessment_id == assessment_id).all()
        q_dict = {q.id: q for q in questions}

        total_correct = 0
        topic_scores: Dict[str, Dict[str, Any]] = {}

        for ans in answers_data:
            q_id = ans.get("question_id")
            selected = ans.get("selected_option", "").strip().upper()
            q = q_dict.get(q_id)
            if not q:
                continue

            is_corr = (selected == q.correct_option.strip().upper())
            if is_corr:
                total_correct += 1

            # Save student answer
            db_answer = AssessmentAnswer(
                assessment_id=assessment.id,
                question_id=q.id,
                selected_option=selected,
                is_correct=is_corr
            )
            self.db.add(db_answer)

            # Map topic
            topic_name = q.topic.name if q.topic else f"Topic {q.topic_id}"
            topic_id = q.topic_id or 0
            if topic_name not in topic_scores:
                topic_scores[topic_name] = {"topic_id": topic_id, "correct": 0, "total": 0}
            topic_scores[topic_name]["total"] += 1
            if is_corr:
                topic_scores[topic_name]["correct"] += 1

        total_questions = len(questions) if len(questions) > 0 else 1
        percentage = round((total_correct / total_questions) * 100, 1)

        strong_topics = []
        weak_topics = []
        proficiency_summary = {}

        for t_name, data in topic_scores.items():
            t_pct = (data["correct"] / data["total"]) * 100 if data["total"] > 0 else 0
            level = compute_proficiency_level(t_pct)
            proficiency_summary[t_name] = level

            if level == "Beginner":
                weak_topics.append(t_name)
            elif level == "Advanced":
                strong_topics.append(t_name)

            # Update topic mastery table in database
            if data["topic_id"]:
                update_topic_mastery(self.db, user_id, data["topic_id"], t_pct)

        # Recommendation logic
        if weak_topics:
            rec = f"Focus prioritized study on weak areas: {', '.join(weak_topics)}. Strengthen foundational theory and practical exercises."
        else:
            rec = "Strong baseline performance across all topics! Proceed with advanced problem-solving."

        assessment.score = float(total_correct)
        assessment.total_questions = total_questions
        assessment.percentage = percentage
        assessment.strong_topics = json.dumps(strong_topics)
        assessment.weak_topics = json.dumps(weak_topics)
        assessment.proficiency_summary = json.dumps(proficiency_summary)
        assessment.recommendations = rec
        self.db.commit()

        # Log Agent Reasoning & Action
        log_agent_action(
            db=self.db,
            user_id=user_id,
            agent_name=self.name,
            action=f"Diagnose Performance ({percentage}%)",
            reasoning=f"Evaluated {total_questions} questions. Identified {len(weak_topics)} weak topics ({', '.join(weak_topics) if weak_topics else 'None'}) and {len(strong_topics)} strong topics.",
            decision=f"Classified proficiency into {len(weak_topics)} Beginner, {len(strong_topics)} Advanced. Handoff to Personalized Study Planner Agent.",
            state_cycle="Analyze",
            input_data={"answers_submitted": len(answers_data)},
            output_data={
                "score": percentage,
                "weak_topics": weak_topics,
                "strong_topics": strong_topics,
                "proficiency_summary": proficiency_summary
            }
        )

        return {
            "assessment_id": assessment.id,
            "score": float(total_correct),
            "total_questions": total_questions,
            "percentage": percentage,
            "strong_topics": strong_topics,
            "weak_topics": weak_topics,
            "proficiency_summary": proficiency_summary,
            "recommendations": rec
        }
