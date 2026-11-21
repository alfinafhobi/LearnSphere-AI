import json
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from ..models import Quiz, QuizQuestion, QuizAttempt, StudentResponse, Subject, Topic
from .tools import log_agent_action, update_topic_mastery

# High quality curated question bank across topics
TOPIC_QUESTION_BANK = {
    "Object-Oriented Programming (OOP)": {
        "Easy": [
            {
                "question": "What is the primary purpose of 'Encapsulation' in OOP?",
                "options": ["A) Increasing runtime speed", "B) Bundling data with methods and restricting direct access", "C) Allowing multiple inheritance in all classes", "D) Eliminating constructors"],
                "correct": "B",
                "explanation": "Encapsulation keeps fields private and provides controlled public getter/setter access.",
                "concept": "Encapsulation"
            },
            {
                "question": "Which keyword in Java is used to inherit from a class?",
                "options": ["A) implements", "B) extends", "C) inherits", "D) super"],
                "correct": "B",
                "explanation": "In Java, 'extends' is used for class inheritance; 'implements' is used for interfaces.",
                "concept": "Inheritance"
            },
            {
                "question": "What is an instance of a class called?",
                "options": ["A) Method", "B) Variable", "C) Object", "D) Interface"],
                "correct": "C",
                "explanation": "An object is a concrete runtime instance created from a class template.",
                "concept": "Object Instantiation"
            },
            {
                "question": "Which access modifier restricts visibility to the defining class only?",
                "options": ["A) public", "B) protected", "C) private", "D) default (package-private)"],
                "correct": "C",
                "explanation": "The 'private' access modifier ensures only members within the same class can access the field or method.",
                "concept": "Access Modifiers"
            },
            {
                "question": "Can an abstract class in Java be instantiated using the 'new' operator?",
                "options": ["A) Yes, always", "B) No, it cannot be directly instantiated", "C) Only if it has no abstract methods", "D) Only in static contexts"],
                "correct": "B",
                "explanation": "Abstract classes cannot be directly instantiated with 'new'; they must be subclassed.",
                "concept": "Abstraction"
            }
        ],
        "Medium": [
            {
                "question": "What is method overloading (compile-time polymorphism) in Java?",
                "options": [
                    "A) Defining methods with the same name but different parameter signatures in the same class",
                    "B) Redefining a parent class method in a subclass with identical signature",
                    "C) Creating methods that cannot return values",
                    "D) Using static methods instead of instance methods"
                ],
                "correct": "A",
                "explanation": "Method overloading involves multiple methods in the same class sharing the same name but differing in number or type of parameters.",
                "concept": "Method Overloading"
            },
            {
                "question": "What happens if a subclass overrides a method and does not use the @Override annotation?",
                "options": [
                    "A) Compilation error occurs",
                    "B) The method still overrides if signatures match, but compiler checks are skipped",
                    "C) The JVM crashes at runtime",
                    "D) The parent method is permanently deleted"
                ],
                "correct": "B",
                "explanation": "@Override is an optional annotation for compiler checking; overriding still occurs without it if signatures match.",
                "concept": "Method Overriding"
            },
            {
                "question": "Which of the following is TRUE about Java interfaces?",
                "options": [
                    "A) A class can implement only one interface",
                    "B) Interfaces can have default and static method implementations since Java 8",
                    "C) Interface variables are by default private and mutable",
                    "D) Interfaces cannot have any methods"
                ],
                "correct": "B",
                "explanation": "Java 8 introduced default and static methods in interfaces with concrete bodies.",
                "concept": "Interfaces"
            },
            {
                "question": "What does the 'super' keyword accomplish in a subclass constructor?",
                "options": [
                    "A) Creates a superclass thread",
                    "B) Invokes the parent class constructor explicitly",
                    "C) Terminates the object lifecycle",
                    "D) Converts private fields to public"
                ],
                "correct": "B",
                "explanation": "Calling super() explicitly invokes the immediate parent class constructor and must be the first statement in the subclass constructor.",
                "concept": "Constructor Chaining"
            },
            {
                "question": "What is dynamic method dispatch?",
                "options": [
                    "A) Resolving overloaded methods at compile time",
                    "B) Resolving an overridden method call at runtime based on the actual object type",
                    "C) Spawning a background thread for each method invocation",
                    "D) Disabling garbage collection during method execution"
                ],
                "correct": "B",
                "explanation": "Dynamic method dispatch is the mechanism by which a call to an overridden method is resolved at runtime rather than compile-time.",
                "concept": "Dynamic Polymorphism"
            }
        ],
        "Hard": [
            {
                "question": "Why can an overridden method in a subclass NOT declare a narrower (more restrictive) access privilege than the parent method?",
                "options": [
                    "A) It violates the Liskov Substitution Principle (subclass must be usable wherever superclass is expected)",
                    "B) JVM bytecode cannot encode private methods in child classes",
                    "C) Because compilers cannot generate vtables for restricted methods",
                    "D) It causes an immediate OutOfMemoryError"
                ],
                "correct": "A",
                "explanation": "According to LSP, a subclass must honor all contracts of its parent; reducing visibility would break clients calling via parent reference.",
                "concept": "Liskov Substitution Principle"
            },
            {
                "question": "In Java, what is the precise behavior of a 'covariant return type' when overriding a method?",
                "options": [
                    "A) The overriding method can return any unrelated primitive type",
                    "B) The overriding method can return a subtype of the return type declared in the parent method",
                    "C) The overriding method must return void",
                    "D) The return type must always be java.lang.Object"
                ],
                "correct": "B",
                "explanation": "Covariant returns allow a subclass method override to return a more specific subtype of the parent method's return type.",
                "concept": "Covariant Returns"
            },
            {
                "question": "Consider: class A has method foo(). class B extends A and overrides foo(). If reference A a = new B(), and foo() throws a checked Exception in B but not in A, what occurs?",
                "options": [
                    "A) Compiles cleanly",
                    "B) Compilation error: an overridden method cannot throw broader checked exceptions than the superclass method",
                    "C) The exception is automatically ignored at runtime",
                    "D) Runtime ClassCastException occurs"
                ],
                "correct": "B",
                "explanation": "A subclass overridden method cannot throw newer or broader checked exceptions than the superclass declaration.",
                "concept": "Exception Contract in Overriding"
            },
            {
                "question": "What is the Diamond Problem in multiple inheritance, and how does Java avoid it for classes?",
                "options": [
                    "A) Diamond memory layouts; avoided by using Garbage Collection",
                    "B) Ambiguity when two parents provide conflicting implementations of the same method; avoided by disallowing multiple class inheritance",
                    "C) Recursive constructor loops; avoided by lazy classloaders",
                    "D) Cryptographic hashing collisions in bytecodes"
                ],
                "correct": "B",
                "explanation": "Java disallows multiple inheritance of state/classes to eliminate ambiguity about which parent implementation to execute.",
                "concept": "Diamond Problem"
            },
            {
                "question": "Which design pattern is directly used to enforce that a class has only one instance while providing a global access point?",
                "options": ["A) Factory Pattern", "B) Observer Pattern", "C) Singleton Pattern", "D) Strategy Pattern"],
                "correct": "C",
                "explanation": "The Singleton pattern restricts class instantiation to a single unique instance.",
                "concept": "Singleton Pattern"
            }
        ]
    }
}

class QuizGenerationAndEvaluationAgent:
    """
    Agent 4: Quiz Generation and Evaluation Agent
    Responsibilities:
    - Generate topic-specific quizzes with chosen difficulty (Easy, Medium, Hard)
    - Generate 5-10 multiple choice questions
    - Guard correct answers from being exposed before submission
    - Evaluate student responses
    - Provide correct answers and comprehensive explanations
    - Identify frequently missed concepts
    - Send results to Progress Monitoring Agent
    """

    def __init__(self, db: Session):
        self.db = db
        self.name = "Quiz Generation & Evaluation Agent"

    def generate_quiz(
        self,
        user_id: int,
        subject_id: int,
        topic_id: Optional[int] = None,
        topic_name: Optional[str] = None,
        difficulty: str = "Medium",
        question_count: int = 5
    ) -> Dict[str, Any]:
        subject = self.db.query(Subject).filter(Subject.id == subject_id).first()
        if not subject:
            raise ValueError(f"Subject {subject_id} not found")

        active_topic = None
        if topic_id:
            active_topic = self.db.query(Topic).filter(Topic.id == topic_id).first()
        elif topic_name:
            active_topic = self.db.query(Topic).filter(
                Topic.subject_id == subject_id,
                Topic.name.ilike(f"%{topic_name}%")
            ).first()

        target_topic_name = active_topic.name if active_topic else (topic_name or "Core Principles")
        
        quiz = Quiz(
            user_id=user_id,
            subject_id=subject_id,
            topic_id=active_topic.id if active_topic else None,
            title=f"{difficulty} Practice Quiz: {target_topic_name}",
            difficulty=difficulty
        )
        self.db.add(quiz)
        self.db.flush()

        # Find questions in bank
        bank_topic = TOPIC_QUESTION_BANK.get(target_topic_name, {})
        questions_pool = bank_topic.get(difficulty, [])

        if not questions_pool:
            # Fallback to any difficulty in bank topic or generate contextual questions
            for diff_key in ["Medium", "Easy", "Hard"]:
                if diff_key in bank_topic:
                    questions_pool = bank_topic[diff_key]
                    break

        created_questions = []

        if questions_pool:
            selected_qs = questions_pool[:question_count]
            for q_data in selected_qs:
                q_model = QuizQuestion(
                    quiz_id=quiz.id,
                    question_text=q_data["question"],
                    options_json=json.dumps(q_data["options"]),
                    correct_option=q_data["correct"],
                    explanation=q_data["explanation"],
                    key_concept=q_data.get("concept", target_topic_name)
                )
                self.db.add(q_model)
                self.db.flush()
                # DO NOT send correct_option or explanation in the public response!
                created_questions.append({
                    "id": q_model.id,
                    "question_text": q_model.question_text,
                    "options": q_data["options"],
                    "key_concept": q_model.key_concept
                })
        else:
            # Dynamic generator for other subjects/topics
            for idx in range(1, question_count + 1):
                options = [
                    f"A) Primary standard pattern for {target_topic_name}",
                    f"B) Secondary implementation variant",
                    f"C) Anti-pattern causing memory leaks",
                    f"D) Deprecated legacy syntax"
                ]
                q_model = QuizQuestion(
                    quiz_id=quiz.id,
                    question_text=f"Question {idx} ({difficulty}): In {subject.name}, what is the best practice regarding {target_topic_name} under standard design guidelines?",
                    options_json=json.dumps(options),
                    correct_option="A",
                    explanation=f"Option A represents the officially recommended design pattern for {target_topic_name} in {subject.name}.",
                    key_concept=target_topic_name
                )
                self.db.add(q_model)
                self.db.flush()
                created_questions.append({
                    "id": q_model.id,
                    "question_text": q_model.question_text,
                    "options": options,
                    "key_concept": target_topic_name
                })

        self.db.commit()

        # Log Quiz Generation Action
        log_agent_action(
            db=self.db,
            user_id=user_id,
            agent_name=self.name,
            action=f"Generate {difficulty} Quiz for {target_topic_name}",
            reasoning=f"Created {len(created_questions)} questions at {difficulty} difficulty. Stripped correct answers before dispatching to client.",
            decision="Ready for student execution",
            state_cycle="Act",
            output_data={"quiz_id": quiz.id, "questions_count": len(created_questions)}
        )

        return {
            "quiz_id": quiz.id,
            "subject_id": subject.id,
            "subject_name": subject.name,
            "topic_name": target_topic_name,
            "title": quiz.title,
            "difficulty": quiz.difficulty,
            "questions": created_questions
        }

    def evaluate_quiz(
        self,
        user_id: int,
        quiz_id: int,
        answers: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        quiz = self.db.query(Quiz).filter(Quiz.id == quiz_id).first()
        if not quiz:
            raise ValueError(f"Quiz {quiz_id} not found")

        db_questions = self.db.query(QuizQuestion).filter(QuizQuestion.quiz_id == quiz_id).all()
        q_map = {q.id: q for q in db_questions}

        score = 0
        total = len(db_questions)
        weak_concepts = []
        review_details = []

        # Create QuizAttempt
        attempt = QuizAttempt(
            quiz_id=quiz.id,
            user_id=user_id,
            total_questions=total
        )
        self.db.add(attempt)
        self.db.flush()

        for ans in answers:
            q_id = ans.get("question_id")
            selected = ans.get("selected_option", "").strip().upper()
            q = q_map.get(q_id)
            if not q:
                continue

            is_corr = (selected == q.correct_option.strip().upper())
            if is_corr:
                score += 1
            else:
                if q.key_concept and q.key_concept not in weak_concepts:
                    weak_concepts.append(q.key_concept)

            # Record response
            resp = StudentResponse(
                quiz_attempt_id=attempt.id,
                question_id=q.id,
                selected_option=selected,
                is_correct=is_corr
            )
            self.db.add(resp)

            # Build review payload
            review_details.append({
                "question_id": q.id,
                "question_text": q.question_text,
                "options": json.loads(q.options_json),
                "selected_option": selected,
                "correct_option": q.correct_option,
                "is_correct": is_corr,
                "explanation": q.explanation,
                "key_concept": q.key_concept
            })

        percentage = round((score / total) * 100, 1) if total > 0 else 0.0
        passed = percentage >= 60.0

        attempt.score = score
        attempt.percentage = percentage
        attempt.weak_concepts = json.dumps(weak_concepts)
        self.db.commit()

        # Update topic mastery in database
        if quiz.topic_id:
            update_topic_mastery(self.db, user_id, quiz.topic_id, percentage)

        # Log Quiz Evaluation Action
        log_agent_action(
            db=self.db,
            user_id=user_id,
            agent_name=self.name,
            action=f"Evaluated Quiz '{quiz.title}' ({percentage}%)",
            reasoning=f"Student scored {score}/{total} ({percentage}%). Identified {len(weak_concepts)} misconception concepts: {', '.join(weak_concepts) if weak_concepts else 'None'}.",
            decision="Dispatched score and weak concepts to Progress Monitoring Agent",
            state_cycle="Evaluate",
            input_data={"quiz_id": quiz.id, "answers_count": len(answers)},
            output_data={"score": score, "percentage": percentage, "weak_concepts": weak_concepts}
        )

        return {
            "attempt_id": attempt.id,
            "quiz_id": quiz.id,
            "score": score,
            "total_questions": total,
            "percentage": percentage,
            "passed": passed,
            "weak_concepts": weak_concepts,
            "questions_review": review_details
        }
