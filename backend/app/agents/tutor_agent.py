import os
import json
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from ..models import ChatHistory, Subject, Topic, TopicMastery
from .tools import log_agent_action
from ..config import settings

class IntelligentTutorAgent:
    """
    Agent 3: Intelligent AI Tutor Agent
    Responsibilities:
    - Explain concepts in simple language tailored to student proficiency
    - Answer questions with real-world analogies and step-by-step clarity
    - Provide runnable code examples
    - Suggest the next progressive topic to study
    - Call Gemini API if GEMINI_API_KEY is configured, else fallback to deterministic high-quality reasoning
    """

    def __init__(self, db: Session):
        self.db = db
        self.name = "Intelligent AI Tutor Agent"

    def chat(
        self,
        user_id: int,
        subject_id: int,
        message: str,
        topic_id: Optional[int] = None,
        topic_name: Optional[str] = None,
        difficulty_level: str = "Intermediate"
    ) -> Dict[str, Any]:
        subject = self.db.query(Subject).filter(Subject.id == subject_id).first()
        subj_name = subject.name if subject else "General Computer Science"

        # Determine topic and mastery level
        active_topic_name = topic_name or "Core Principles"
        if topic_id:
            top = self.db.query(Topic).filter(Topic.id == topic_id).first()
            if top:
                active_topic_name = top.name
                mastery = self.db.query(TopicMastery).filter(
                    TopicMastery.user_id == user_id,
                    TopicMastery.topic_id == topic_id
                ).first()
                if mastery:
                    difficulty_level = mastery.proficiency_level

        # Record user message in ChatHistory
        user_chat = ChatHistory(
            user_id=user_id,
            subject_id=subject_id,
            topic_id=topic_id,
            role="user",
            content=message,
            difficulty_level=difficulty_level
        )
        self.db.add(user_chat)
        self.db.commit()

        # Try Gemini API if key is present
        api_key = os.environ.get("GEMINI_API_KEY") or settings.GEMINI_API_KEY
        reply_content = None
        code_example = None
        step_by_step = []
        next_topic = None

        if api_key and api_key.strip():
            try:
                from google import genai
                client = genai.Client(api_key=api_key)
                system_prompt = (
                    f"You are the Intelligent AI Tutor Agent for LearnSphere AI. "
                    f"Subject: {subj_name}. Current Topic: {active_topic_name}. "
                    f"Student Proficiency Level: {difficulty_level}. "
                    f"Explain concepts clearly suited for {difficulty_level} students. "
                    f"Structure your response with: 1) clear explanation with analogies, "
                    f"2) numbered step-by-step key takeaways, 3) a brief code example, "
                    f"4) recommended next topic."
                )
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=[system_prompt, f"Student Question: {message}"]
                )
                if response and response.text:
                    reply_content = response.text
            except Exception as e:
                # Graceful fallback to deterministic engine on error/timeout
                reply_content = None

        if not reply_content:
            # Deterministic, rich pedagogical response generator
            if "oop" in active_topic_name.lower() or "object" in message.lower() or "class" in message.lower() or "polymorphism" in message.lower():
                reply_content = (
                    f"### Understanding {active_topic_name} ({difficulty_level} Level)\n\n"
                    f"Think of Object-Oriented Programming (OOP) like a **Blueprint and House construction**:\n"
                    f"- A **Class** is the architectural blueprint defining attributes (walls, rooms) and behaviors (open doors, turn lights on).\n"
                    f"- An **Object** is the actual physical house instantiated from that blueprint.\n\n"
                    f"The 4 pillars of OOP are **Encapsulation** (shielding data), **Inheritance** (reusing code), "
                    f"**Polymorphism** (one interface, multiple behaviors), and **Abstraction** (hiding complexity)."
                )
                step_by_step = [
                    "Class Declaration: Define fields (state) as private for encapsulation.",
                    "Constructor Initialization: Set up valid internal invariants when objects are created.",
                    "Polymorphic Dispatch: Override methods in subclasses to allow flexible dynamic behavior at runtime.",
                    "Interface Separation: Program to interfaces, not concrete implementations."
                ]
                code_example = (
                    "// Java OOP Example: Polymorphism & Encapsulation\n"
                    "abstract class Vehicle {\n"
                    "    private String brand;\n"
                    "    public Vehicle(String brand) { this.brand = brand; }\n"
                    "    public String getBrand() { return brand; }\n"
                    "    public abstract void drive(); // Abstract contract\n"
                    "}\n\n"
                    "class ElectricCar extends Vehicle {\n"
                    "    public ElectricCar(String brand) { super(brand); }\n"
                    "    @Override\n"
                    "    public void drive() {\n"
                    "        System.out.println(getBrand() + \" gliding silently with zero emissions.\");\n"
                    "    }\n"
                    "}\n\n"
                    "public class Main {\n"
                    "    public static void main(String[] args) {\n"
                    "        Vehicle myCar = new ElectricCar(\"Tesla\"); // Polymorphic reference\n"
                    "        myCar.drive();\n"
                    "    }\n"
                    "}"
                )
                next_topic = "Exception Handling & Collections Framework"
            elif "variable" in active_topic_name.lower() or "data type" in active_topic_name.lower():
                reply_content = (
                    f"### Mastering {active_topic_name}\n\n"
                    f"Variables are named memory storage locations holding data values. In strongly typed languages like Java, "
                    f"every variable has an explicit type checked at compile time:\n"
                    f"- **Primitives**: store raw values directly in the stack (e.g., `int`, `double`, `boolean`, `char`).\n"
                    f"- **Reference Types**: store memory addresses pointing to objects on the heap (e.g., `String`, `Scanner`, custom classes)."
                )
                step_by_step = [
                    "Choose appropriate primitive types (e.g., 'long' for high counts, 'double' for currency/measurements).",
                    "Understand implicit vs explicit casting to prevent precision loss.",
                    "Follow Java naming conventions (camelCase for variables, UPPER_SNAKE for constants)."
                ]
                code_example = (
                    "int age = 21;                  // 32-bit primitive integer\n"
                    "double gpa = 3.85;             // 64-bit floating point\n"
                    "final double PI = 3.14159;     // Immutable constant\n"
                    "String student = \"Alex\";      // Reference to String object in pool"
                )
                next_topic = "Control Flow & Loops"
            else:
                reply_content = (
                    f"### Key Concepts: {active_topic_name}\n\n"
                    f"Regarding your question *\"{message}\"*: in {subj_name}, mastering {active_topic_name} requires "
                    f"understanding both the high-level design motivation and the underlying execution model.\n\n"
                    f"Always break problems down into smaller units, verify inputs, and test edge cases."
                )
                step_by_step = [
                    f"Step 1: Understand the core responsibility of {active_topic_name}.",
                    "Step 2: Trace input and output data flows.",
                    "Step 3: Analyze time and space efficiency.",
                    "Step 4: Handle boundary conditions and invalid states."
                ]
                code_example = (
                    f"// Context: {subj_name} - {active_topic_name}\n"
                    "public void executeProcess() {\n"
                    "    // Verify prerequisite state\n"
                    "    if (isReady()) {\n"
                    "        processStep();\n"
                    "    }\n"
                    "}"
                )
                next_topic = "Practice Quiz & Self-Assessment"

        # Record tutor response
        assistant_chat = ChatHistory(
            user_id=user_id,
            subject_id=subject_id,
            topic_id=topic_id,
            role="assistant",
            content=reply_content,
            difficulty_level=difficulty_level
        )
        self.db.add(assistant_chat)
        self.db.commit()

        # Log Tutor Agent activity
        agent_reasoning = f"Adapted explanation for {difficulty_level} level in {active_topic_name}. Provided step-by-step breakdown and code snippet."
        log_agent_action(
            db=self.db,
            user_id=user_id,
            agent_name=self.name,
            action=f"Tutored on {active_topic_name}",
            reasoning=agent_reasoning,
            decision=f"Recommended next topic: {next_topic}",
            state_cycle="Act",
            input_data={"question": message, "proficiency": difficulty_level},
            output_data={"next_topic": next_topic}
        )

        suggested = [
            f"How does {active_topic_name} behave in multi-threaded environments?",
            f"Can you show a common mistake beginners make with {active_topic_name}?",
            "Give me a quick quiz question to test what I just learned."
        ]

        return {
            "reply": reply_content,
            "recommended_next_topic": next_topic,
            "step_by_step_points": step_by_step,
            "code_example": code_example,
            "suggested_questions": suggested,
            "agent_reasoning": agent_reasoning
        }
