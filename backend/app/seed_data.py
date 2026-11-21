import json
from sqlalchemy.orm import Session
from .models import User, Subject, Topic, StudentGoal, AgentActivityLog, TopicMastery
from .auth import hash_password

INITIAL_SUBJECTS = [
    {
        "name": "Java Programming",
        "code": "CS-JAVA",
        "description": "Comprehensive object-oriented programming with Java: syntax, OOP principles, collections, and robust exception handling.",
        "icon": "Coffee",
        "topics": [
            {"name": "Variables & Data Types", "order_index": 1, "difficulty_level": "Easy", "key_concepts": "primitives, references, type casting, scope"},
            {"name": "Control Flow & Loops", "order_index": 2, "difficulty_level": "Easy", "key_concepts": "if-else, switch, while, for-each, break/continue"},
            {"name": "Arrays & Strings", "order_index": 3, "difficulty_level": "Medium", "key_concepts": "array declaration, multi-dimensional, String immutability, StringBuilder"},
            {"name": "Object-Oriented Programming (OOP)", "order_index": 4, "difficulty_level": "Hard", "key_concepts": "classes, inheritance, polymorphism, encapsulation, interfaces, abstract classes"},
            {"name": "Exception Handling", "order_index": 5, "difficulty_level": "Medium", "key_concepts": "try-catch-finally, checked vs unchecked, throw, custom exceptions"}
        ]
    },
    {
        "name": "Python Programming",
        "code": "CS-PY",
        "description": "Dynamic, high-level programming language known for readability, rapid prototyping, and scientific computing.",
        "icon": "Code",
        "topics": [
            {"name": "Variables & Core Types", "order_index": 1, "difficulty_level": "Easy", "key_concepts": "integers, strings, booleans, casting"},
            {"name": "Lists, Tuples & Dicts", "order_index": 2, "difficulty_level": "Easy", "key_concepts": "indexing, slicing, dictionary comprehension"},
            {"name": "Functions & Scope", "order_index": 3, "difficulty_level": "Medium", "key_concepts": "def, args, kwargs, lambdas, scope"},
            {"name": "OOP in Python", "order_index": 4, "difficulty_level": "Medium", "key_concepts": "dunder methods, classes, inheritance"},
            {"name": "File I/O & Modules", "order_index": 5, "difficulty_level": "Hard", "key_concepts": "context managers, imports, virtual environments"}
        ]
    },
    {
        "name": "Data Structures & Algorithms",
        "code": "CS-DSA",
        "description": "Fundamental computational structures, complexity analysis, trees, graphs, and algorithmic problem-solving.",
        "icon": "Network",
        "topics": [
            {"name": "Asymptotic Analysis (Big-O)", "order_index": 1, "difficulty_level": "Easy", "key_concepts": "time complexity, space complexity, upper bounds"},
            {"name": "Stacks & Queues", "order_index": 2, "difficulty_level": "Easy", "key_concepts": "LIFO, FIFO, priority queue, monotonic stack"},
            {"name": "Linked Lists", "order_index": 3, "difficulty_level": "Medium", "key_concepts": "singly, doubly, cycle detection"},
            {"name": "Trees & Binary Search Trees", "order_index": 4, "difficulty_level": "Hard", "key_concepts": "traversals, height, AVL, balancing"},
            {"name": "Graph Algorithms", "order_index": 5, "difficulty_level": "Hard", "key_concepts": "BFS, DFS, Dijkstra, topological sort"}
        ]
    },
    {
        "name": "Database Management Systems",
        "code": "CS-DBMS",
        "description": "Relational models, relational algebra, SQL optimization, normalization, indexing, and ACID transactions.",
        "icon": "Database",
        "topics": [
            {"name": "Relational Model & ER Diagrams", "order_index": 1, "difficulty_level": "Easy", "key_concepts": "entities, relations, foreign keys"},
            {"name": "SQL Queries & Aggregations", "order_index": 2, "difficulty_level": "Easy", "key_concepts": "SELECT, GROUP BY, HAVING, subqueries"},
            {"name": "Joins & Subqueries", "order_index": 3, "difficulty_level": "Medium", "key_concepts": "INNER, LEFT, RIGHT, FULL OUTER, correlated subqueries"},
            {"name": "Normalization (1NF-BCNF)", "order_index": 4, "difficulty_level": "Hard", "key_concepts": "functional dependencies, lossless join, BCNF"},
            {"name": "Transactions & Concurrency Control", "order_index": 5, "difficulty_level": "Hard", "key_concepts": "ACID, 2PL, serializability, deadlocks"}
        ]
    },
    {
        "name": "Operating Systems",
        "code": "CS-OS",
        "description": "Process scheduling, thread synchronization, memory virtualization, paging, and file management systems.",
        "icon": "Cpu",
        "topics": [
            {"name": "Process Management & Scheduling", "order_index": 1, "difficulty_level": "Easy", "key_concepts": "PCB, Round Robin, priority scheduling"},
            {"name": "Threads & Concurrency", "order_index": 2, "difficulty_level": "Medium", "key_concepts": "mutex, semaphores, race conditions"},
            {"name": "Deadlocks", "order_index": 3, "difficulty_level": "Medium", "key_concepts": "prevention, avoidance, Banker's algorithm"},
            {"name": "Memory Management & Paging", "order_index": 4, "difficulty_level": "Hard", "key_concepts": "virtual memory, page faults, TLB"},
            {"name": "File Systems & Disk Scheduling", "order_index": 5, "difficulty_level": "Medium", "key_concepts": "inodes, FAT, SCAN, C-LOOK"}
        ]
    },
    {
        "name": "Computer Networks",
        "code": "CS-CN",
        "description": "OSI and TCP/IP protocol stacks, IP routing, TCP flow control, subnetting, and network security basics.",
        "icon": "Radio",
        "topics": [
            {"name": "OSI & TCP/IP Models", "order_index": 1, "difficulty_level": "Easy", "key_concepts": "layers, encapsulation, protocols"},
            {"name": "IP Addressing & Subnetting", "order_index": 2, "difficulty_level": "Medium", "key_concepts": "IPv4, CIDR, subnet masks"},
            {"name": "Routing Protocols", "order_index": 3, "difficulty_level": "Hard", "key_concepts": "Distance Vector, Link State, OSPF, BGP"},
            {"name": "Transport Layer (TCP vs UDP)", "order_index": 4, "difficulty_level": "Medium", "key_concepts": "three-way handshake, flow control, congestion"},
            {"name": "Application Protocols & DNS", "order_index": 5, "difficulty_level": "Easy", "key_concepts": "HTTP/HTTPS, DNS resolution, DHCP"}
        ]
    },
    {
        "name": "Machine Learning",
        "code": "CS-ML",
        "description": "Statistical learning, regression, classification, clustering, neural networks, and model evaluation metrics.",
        "icon": "Brain",
        "topics": [
            {"name": "Supervised Learning: Regression", "order_index": 1, "difficulty_level": "Easy", "key_concepts": "linear regression, loss functions, gradient descent"},
            {"name": "Supervised Learning: Classification", "order_index": 2, "difficulty_level": "Medium", "key_concepts": "logistic regression, decision trees, SVM"},
            {"name": "Model Evaluation & Bias-Variance", "order_index": 3, "difficulty_level": "Medium", "key_concepts": "precision, recall, F1, ROC-AUC, overfitting"},
            {"name": "Unsupervised Learning & Clustering", "order_index": 4, "difficulty_level": "Medium", "key_concepts": "K-Means, PCA, dimensionality reduction"},
            {"name": "Neural Networks & Deep Learning", "order_index": 5, "difficulty_level": "Hard", "key_concepts": "perceptrons, backpropagation, activation functions"}
        ]
    }
]

# Diagnostic questions pre-crafted for immediate high-quality assessment
DIAGNOSTIC_QUESTIONS = {
    "Java Programming": [
        {
            "topic": "Variables & Data Types",
            "question": "What is the default initial value of an uninitialized instance boolean variable in Java?",
            "options": ["A) true", "B) false", "C) null", "D) 0"],
            "correct": "B",
            "explanation": "In Java, instance boolean variables default to false when uninitialized."
        },
        {
            "topic": "Control Flow & Loops",
            "question": "Which of the following statements about Java's enhanced for loop (for-each) is TRUE?",
            "options": [
                "A) It allows modifying the array element while iterating",
                "B) It works with any object implementing Iterable",
                "C) It provides direct access to the iteration index",
                "D) It can only be used with primitive arrays"
            ],
            "correct": "B",
            "explanation": "The enhanced for loop works on arrays and any class that implements java.lang.Iterable."
        },
        {
            "topic": "Arrays & Strings",
            "question": "Why are String objects immutable in Java?",
            "options": [
                "A) To save disk memory during runtime compilation",
                "B) For security, thread safety, and string pool caching",
                "C) Because JVM cannot dynamically resize character buffers",
                "D) To enforce single-threaded access to char arrays"
            ],
            "correct": "B",
            "explanation": "String immutability enables the String Constant Pool, ensures thread safety without synchronization, and prevents tampering in sensitive contexts like network connections."
        },
        {
            "topic": "Object-Oriented Programming (OOP)",
            "question": "In Java, if class Child extends Parent, and both declare a static method 'void display()', what occurs when calling Child.display()?",
            "options": [
                "A) Runtime polymorphism overrides the parent method",
                "B) Method hiding occurs; static methods cannot be overridden polymorphically",
                "C) A compilation error occurs because static methods cannot share names",
                "D) The JVM randomly invokes one based on thread priority"
            ],
            "correct": "B",
            "explanation": "In Java, static methods are bonded at compile-time (method hiding), not overridden dynamically at runtime."
        },
        {
            "topic": "Exception Handling",
            "question": "Which block in a Java try-catch-finally construct will ALWAYS execute unless System.exit() is invoked?",
            "options": [
                "A) catch block",
                "B) try block",
                "C) finally block",
                "D) finalize block"
            ],
            "correct": "C",
            "explanation": "The finally block executes whether an exception is thrown or caught, unless the JVM terminates abruptly via System.exit()."
        }
    ]
}

def seed_database(db: Session):
    """Seed initial subjects, topics, and default student demo profile."""
    # Check if subjects exist
    existing_count = db.query(Subject).count()
    if existing_count == 0:
        for subj_data in INITIAL_SUBJECTS:
            subject = Subject(
                name=subj_data["name"],
                code=subj_data["code"],
                description=subj_data["description"],
                icon=subj_data["icon"],
                is_custom=False
            )
            db.add(subject)
            db.flush()

            for t_data in subj_data["topics"]:
                topic = Topic(
                    subject_id=subject.id,
                    name=t_data["name"],
                    order_index=t_data["order_index"],
                    difficulty_level=t_data["difficulty_level"],
                    key_concepts=t_data["key_concepts"]
                )
                db.add(topic)
        db.commit()

    # Seed Demo Student user if not present
    demo_user = db.query(User).filter(User.email == "demo@learnsphere.ai").first()
    if not demo_user:
        demo_user = User(
            email="demo@learnsphere.ai",
            full_name="Alex Rivera",
            hashed_password=hash_password("password123"),
            avatar_color="#6366F1"
        )
        db.add(demo_user)
        db.commit()
        db.refresh(demo_user)

        # Seed initial goal for demo user
        java_subject = db.query(Subject).filter(Subject.name == "Java Programming").first()
        if java_subject:
            goal = StudentGoal(
                user_id=demo_user.id,
                subject_id=java_subject.id,
                target_grade="A",
                available_hours_per_day=2.5,
                preferred_learning_style="Interactive & Practical",
                academic_focus="Master Object-Oriented Design and achieve excellence in Semester Exam"
            )
            db.add(goal)

            # Pre-seed initial agent log illustrating startup
            init_log = AgentActivityLog(
                user_id=demo_user.id,
                agent_name="System Orchestrator",
                action="Initialize Multi-Agent Context",
                reasoning="Initialized agentic student profile for Alex Rivera. Ready to observe baseline capabilities.",
                decision="Ready for diagnostic assessment in Java Programming",
                state_cycle="Observe",
                input_data_json=json.dumps({"subject": "Java Programming", "goal": "A"}),
                output_data_json=json.dumps({"status": "Active", "agents": ["Assessment", "Planner", "Tutor", "Quiz", "Progress"]})
            )
            db.add(init_log)
            db.commit()
