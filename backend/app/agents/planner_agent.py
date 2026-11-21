import json
import datetime
import urllib.parse
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from ..models import StudyPlan, StudyTask, Subject, Topic, TopicMastery, StudentGoal
from .tools import log_agent_action, calculate_time_allocations

# Verified, trusted learning resource repository across all standard curriculum subjects & topics
TOPIC_LEARNING_RESOURCES = {
    # 1. Java Programming
    "Variables & Data Types": [
        {"title": "Variables and Primitive Data Types", "platform": "Oracle Java Documentation", "resource_type": "Official Documentation", "url": "https://docs.oracle.com/javase/tutorial/java/nutsandbolts/variables.html", "beginner_friendly": True},
        {"title": "Java Data Types & Type Casting", "platform": "W3Schools", "resource_type": "Interactive Tutorial", "url": "https://www.w3schools.com/java/java_data_types.asp", "beginner_friendly": True},
        {"title": "Variables in Java - Declaration and Scope", "platform": "GeeksforGeeks", "resource_type": "Technical Article", "url": "https://www.geeksforgeeks.org/variables-in-java/", "beginner_friendly": False},
        {"title": "Java Data Types (Primitives & Literals)", "platform": "Programiz", "resource_type": "Beginner Guide", "url": "https://www.programiz.com/java-programming/variables-primitive-data-types", "beginner_friendly": True},
        {"title": "Java Primitive Types and Wrappers Deep Dive", "platform": "Baeldung", "resource_type": "Technical Blog", "url": "https://www.baeldung.com/java-primitives", "beginner_friendly": False}
    ],
    "Control Flow & Loops": [
        {"title": "Control Flow Statements Tutorial", "platform": "Oracle Java Documentation", "resource_type": "Official Documentation", "url": "https://docs.oracle.com/javase/tutorial/java/nutsandbolts/flow.html", "beginner_friendly": True},
        {"title": "Java If...Else and Switch Conditionals", "platform": "W3Schools", "resource_type": "Interactive Tutorial", "url": "https://www.w3schools.com/java/java_conditions.asp", "beginner_friendly": True},
        {"title": "Loops in Java (for, while, do-while)", "platform": "GeeksforGeeks", "resource_type": "Technical Article", "url": "https://www.geeksforgeeks.org/loops-in-java/", "beginner_friendly": True},
        {"title": "A Guide to Java Loops and Iteration", "platform": "Baeldung", "resource_type": "Technical Blog", "url": "https://www.baeldung.com/java-loops", "beginner_friendly": False},
        {"title": "Java For-Each Loop and Iterators", "platform": "Programiz", "resource_type": "Tutorial", "url": "https://www.programiz.com/java-programming/enhanced-for-loop", "beginner_friendly": True}
    ],
    "Arrays & Strings": [
        {"title": "Arrays and Multi-Dimensional Structures", "platform": "Oracle Java Documentation", "resource_type": "Official Documentation", "url": "https://docs.oracle.com/javase/tutorial/java/nutsandbolts/arrays.html", "beginner_friendly": True},
        {"title": "Java Arrays Tutorial & Practical Exercises", "platform": "W3Schools", "resource_type": "Interactive Tutorial", "url": "https://www.w3schools.com/java/java_arrays.asp", "beginner_friendly": True},
        {"title": "String Class and Memory Pool in Java", "platform": "GeeksforGeeks", "resource_type": "Technical Article", "url": "https://www.geeksforgeeks.org/string-class-in-java/", "beginner_friendly": True},
        {"title": "Java String Immutability and Performance Guide", "platform": "Baeldung", "resource_type": "Technical Blog", "url": "https://www.baeldung.com/java-string-immutable", "beginner_friendly": False},
        {"title": "StringBuilder and StringBuffer in Java", "platform": "Programiz", "resource_type": "Tutorial", "url": "https://www.programiz.com/java-programming/stringbuilder", "beginner_friendly": False}
    ],
    "Object-Oriented Programming (OOP)": [
        {"title": "Oracle Java Documentation – OOP Concepts", "platform": "Oracle Documentation", "resource_type": "Official Documentation", "url": "https://docs.oracle.com/javase/tutorial/java/concepts/", "beginner_friendly": True},
        {"title": "W3Schools – Java OOP Tutorial & Classes", "platform": "W3Schools", "resource_type": "Interactive Tutorial", "url": "https://www.w3schools.com/java/java_oop.asp", "beginner_friendly": True},
        {"title": "GeeksforGeeks – OOP in Java (Pillars & Real-World Examples)", "platform": "GeeksforGeeks", "resource_type": "Technical Article", "url": "https://www.geeksforgeeks.org/object-oriented-programming-oops-concept-in-java/", "beginner_friendly": True},
        {"title": "Programiz – Java Classes, Objects & Inheritance", "platform": "Programiz", "resource_type": "Beginner Guide", "url": "https://www.programiz.com/java-programming/class-objects", "beginner_friendly": True},
        {"title": "Baeldung – Java OOP Guide and Solid Principles", "platform": "Baeldung", "resource_type": "Technical Blog", "url": "https://www.baeldung.com/java-oop", "beginner_friendly": False}
    ],
    "Exception Handling": [
        {"title": "Lesson: Exceptions in Java", "platform": "Oracle Java Documentation", "resource_type": "Official Documentation", "url": "https://docs.oracle.com/javase/tutorial/essential/exceptions/", "beginner_friendly": True},
        {"title": "Java Try...Catch & Finally Blocks", "platform": "W3Schools", "resource_type": "Interactive Tutorial", "url": "https://www.w3schools.com/java/java_try_catch.asp", "beginner_friendly": True},
        {"title": "Exceptions in Java (Checked vs Unchecked)", "platform": "GeeksforGeeks", "resource_type": "Technical Article", "url": "https://www.geeksforgeeks.org/exceptions-in-java/", "beginner_friendly": True},
        {"title": "Best Practices for Exception Handling in Java", "platform": "Baeldung", "resource_type": "Technical Blog", "url": "https://www.baeldung.com/java-exceptions", "beginner_friendly": False},
        {"title": "Java Custom Exception Handling", "platform": "Programiz", "resource_type": "Tutorial", "url": "https://www.programiz.com/java-programming/user-defined-exception", "beginner_friendly": False}
    ],

    # 2. Python Programming
    "Variables & Core Types": [
        {"title": "An Informal Introduction to Python Data Types", "platform": "Python Official Documentation", "resource_type": "Official Documentation", "url": "https://docs.python.org/3/tutorial/introduction.html", "beginner_friendly": True},
        {"title": "Python Data Types: A Practical Introduction", "platform": "Real Python", "resource_type": "Technical Article", "url": "https://realpython.com/python-data-types/", "beginner_friendly": True},
        {"title": "Python Variables and Type Casting", "platform": "W3Schools", "resource_type": "Interactive Tutorial", "url": "https://www.w3schools.com/python/python_variables.asp", "beginner_friendly": True},
        {"title": "Python Variables, Constants and Literals", "platform": "Programiz", "resource_type": "Beginner Guide", "url": "https://www.programiz.com/python-programming/variables-constants-literals", "beginner_friendly": True}
    ],
    "Lists, Tuples & Dicts": [
        {"title": "Data Structures: Lists, Sets, and Dictionaries", "platform": "Python Official Documentation", "resource_type": "Official Documentation", "url": "https://docs.python.org/3/tutorial/datastructures.html", "beginner_friendly": True},
        {"title": "Python Dictionaries and Hash Maps Explained", "platform": "Real Python", "resource_type": "Technical Article", "url": "https://realpython.com/python-dicts/", "beginner_friendly": False},
        {"title": "Python Lists and Tuples Tutorial", "platform": "W3Schools", "resource_type": "Interactive Tutorial", "url": "https://www.w3schools.com/python/python_lists.asp", "beginner_friendly": True},
        {"title": "Data Structures in Python with Examples", "platform": "GeeksforGeeks", "resource_type": "Technical Article", "url": "https://www.geeksforgeeks.org/python-data-structures/", "beginner_friendly": True}
    ],
    "Functions & Scope": [
        {"title": "Defining Functions in Python", "platform": "Python Official Documentation", "resource_type": "Official Documentation", "url": "https://docs.python.org/3/tutorial/controlflow.html#defining-functions", "beginner_friendly": True},
        {"title": "Defining Your Own Python Function", "platform": "Real Python", "resource_type": "Technical Article", "url": "https://realpython.com/defining-your-own-python-function/", "beginner_friendly": True},
        {"title": "Python Functions and Variable Scope", "platform": "Programiz", "resource_type": "Beginner Guide", "url": "https://www.programiz.com/python-programming/function", "beginner_friendly": True},
        {"title": "Python *args and **kwargs Demystified", "platform": "GeeksforGeeks", "resource_type": "Technical Article", "url": "https://www.geeksforgeeks.org/args-kwargs-python/", "beginner_friendly": False}
    ],
    "OOP in Python": [
        {"title": "Python Classes and Object Model", "platform": "Python Official Documentation", "resource_type": "Official Documentation", "url": "https://docs.python.org/3/tutorial/classes.html", "beginner_friendly": True},
        {"title": "Object-Oriented Programming (OOP) in Python 3", "platform": "Real Python", "resource_type": "Technical Article", "url": "https://realpython.com/python3-object-oriented-programming/", "beginner_friendly": True},
        {"title": "Python OOPs Concepts with Code Snippets", "platform": "GeeksforGeeks", "resource_type": "Technical Article", "url": "https://www.geeksforgeeks.org/python-oops-concepts/", "beginner_friendly": True},
        {"title": "Python Classes, Objects, and Inheritance", "platform": "W3Schools", "resource_type": "Interactive Tutorial", "url": "https://www.w3schools.com/python/python_classes.asp", "beginner_friendly": True}
    ],
    "File I/O & Modules": [
        {"title": "Reading and Writing Files in Python", "platform": "Python Official Documentation", "resource_type": "Official Documentation", "url": "https://docs.python.org/3/tutorial/inputoutput.html#reading-and-writing-files", "beginner_friendly": True},
        {"title": "Working With Files in Python", "platform": "Real Python", "resource_type": "Technical Article", "url": "https://realpython.com/working-with-files-in-python/", "beginner_friendly": True},
        {"title": "Python File Handling and Context Managers", "platform": "Programiz", "resource_type": "Beginner Guide", "url": "https://www.programiz.com/python-programming/file-operation", "beginner_friendly": True}
    ],

    # 3. Data Structures & Algorithms
    "Asymptotic Analysis (Big-O)": [
        {"title": "Analysis of Algorithms: Big-O, Big-Omega, Big-Theta", "platform": "GeeksforGeeks", "resource_type": "Technical Article", "url": "https://www.geeksforgeeks.org/analysis-of-algorithms-set-1-asymptotic-analysis/", "beginner_friendly": True},
        {"title": "Big O Notation Explained for Beginners", "platform": "freeCodeCamp", "resource_type": "Educational Guide", "url": "https://www.freecodecamp.org/news/big-o-notation-why-it-matters-and-why-it-doesnt-1674cfa8a23c/", "beginner_friendly": True},
        {"title": "Asymptotic Analysis and Time Complexity", "platform": "Programiz", "resource_type": "Interactive Tutorial", "url": "https://www.programiz.com/dsa/asymptotic-notations", "beginner_friendly": True}
    ],
    "Stacks & Queues": [
        {"title": "Stack Data Structure: Principles & Code", "platform": "GeeksforGeeks", "resource_type": "Technical Article", "url": "https://www.geeksforgeeks.org/stack-data-structure/", "beginner_friendly": True},
        {"title": "Queue Data Structure and Implementations", "platform": "Programiz", "resource_type": "Interactive Tutorial", "url": "https://www.programiz.com/dsa/queue", "beginner_friendly": True},
        {"title": "Data Structures: Stacks and Queues Tutorial", "platform": "W3Schools", "resource_type": "Interactive Tutorial", "url": "https://www.w3schools.com/dsa/dsa_data_stacks.php", "beginner_friendly": True}
    ],
    "Linked Lists": [
        {"title": "Linked List Data Structure (Singly, Doubly, Circular)", "platform": "GeeksforGeeks", "resource_type": "Technical Article", "url": "https://www.geeksforgeeks.org/data-structures/linked-list/", "beginner_friendly": True},
        {"title": "Linked List Types and Operations with Diagrams", "platform": "Programiz", "resource_type": "Beginner Guide", "url": "https://www.programiz.com/dsa/linked-list", "beginner_friendly": True},
        {"title": "Introduction to Linked Lists with Visual Diagrams", "platform": "freeCodeCamp", "resource_type": "Educational Guide", "url": "https://www.freecodecamp.org/news/introduction-to-linked-lists/", "beginner_friendly": True}
    ],
    "Trees & Binary Search Trees": [
        {"title": "Binary Search Tree Data Structure & Operations", "platform": "GeeksforGeeks", "resource_type": "Technical Article", "url": "https://www.geeksforgeeks.org/binary-search-tree-data-structure/", "beginner_friendly": True},
        {"title": "Tree Traversals (Inorder, Preorder, Postorder)", "platform": "Programiz", "resource_type": "Interactive Tutorial", "url": "https://www.programiz.com/dsa/tree-traversal", "beginner_friendly": True},
        {"title": "Binary Search Tree Interactive Visualizer", "platform": "Visualgo", "resource_type": "Interactive Visualization", "url": "https://visualgo.net/en/bst", "beginner_friendly": True}
    ],
    "Graph Algorithms": [
        {"title": "Graph Data Structure and Algorithms (BFS & DFS)", "platform": "GeeksforGeeks", "resource_type": "Technical Article", "url": "https://www.geeksforgeeks.org/graph-data-structure-and-algorithms/", "beginner_friendly": True},
        {"title": "Breadth-First and Depth-First Search Tutorial", "platform": "Programiz", "resource_type": "Beginner Guide", "url": "https://www.programiz.com/dsa/graph-bfs", "beginner_friendly": True},
        {"title": "Graph Algorithms Crash Course and Dijkstra's Path", "platform": "freeCodeCamp", "resource_type": "Educational Guide", "url": "https://www.freecodecamp.org/news/graph-algorithms-for-technical-interviews/", "beginner_friendly": False}
    ],

    # 4. Database Management Systems
    "Relational Model & ER Diagrams": [
        {"title": "Introduction to DBMS and Entity-Relationship Model", "platform": "GeeksforGeeks", "resource_type": "Technical Article", "url": "https://www.geeksforgeeks.org/introduction-of-dbms-database-management-system-set-1/", "beginner_friendly": True},
        {"title": "DBMS Entity-Relationship Diagrams Tutorial", "platform": "Tutorialspoint", "resource_type": "Tutorial", "url": "https://www.tutorialspoint.com/dbms/er_model_basic_concepts.htm", "beginner_friendly": True},
        {"title": "Relational Database Concepts and Keys", "platform": "W3Schools", "resource_type": "Interactive Tutorial", "url": "https://www.w3schools.com/sql/sql_intro.asp", "beginner_friendly": True}
    ],
    "SQL Queries & Aggregations": [
        {"title": "SQL Tutorial - SELECT, WHERE, GROUP BY, HAVING", "platform": "W3Schools", "resource_type": "Interactive Tutorial", "url": "https://www.w3schools.com/sql/", "beginner_friendly": True},
        {"title": "SQL Aggregate Functions and Grouping", "platform": "GeeksforGeeks", "resource_type": "Technical Article", "url": "https://www.geeksforgeeks.org/sql-aggregate-functions/", "beginner_friendly": True},
        {"title": "SQL Aggregations and Analytical Queries", "platform": "Mode Analytics", "resource_type": "Technical Guide", "url": "https://mode.com/sql-tutorial/sql-aggregate-functions/", "beginner_friendly": False}
    ],
    "Joins & Subqueries": [
        {"title": "SQL Joins Tutorial (INNER, LEFT, RIGHT, FULL OUTER)", "platform": "W3Schools", "resource_type": "Interactive Tutorial", "url": "https://www.w3schools.com/sql/sql_join.asp", "beginner_friendly": True},
        {"title": "SQL Join Types Explained with Venn Diagrams", "platform": "GeeksforGeeks", "resource_type": "Technical Article", "url": "https://www.geeksforgeeks.org/sql-join-set-1-inner-left-right-and-full-joins/", "beginner_friendly": True},
        {"title": "SQL Subqueries and Nested Queries Guide", "platform": "Programiz", "resource_type": "Beginner Guide", "url": "https://www.programiz.com/sql/joins", "beginner_friendly": True}
    ],
    "Normalization (1NF-BCNF)": [
        {"title": "Database Normalization (1NF, 2NF, 3NF, BCNF) Explained", "platform": "GeeksforGeeks", "resource_type": "Technical Article", "url": "https://www.geeksforgeeks.org/database-normalization-introduction/", "beginner_friendly": True},
        {"title": "DBMS Normalization Functional Dependencies", "platform": "Tutorialspoint", "resource_type": "Tutorial", "url": "https://www.tutorialspoint.com/dbms/database_normalization.htm", "beginner_friendly": False},
        {"title": "Database Normalization with Real Table Examples", "platform": "freeCodeCamp", "resource_type": "Educational Guide", "url": "https://www.freecodecamp.org/news/database-normalization-1nf-2nf-3nf-table-examples/", "beginner_friendly": True}
    ],
    "Transactions & Concurrency Control": [
        {"title": "ACID Properties in DBMS and Serializability", "platform": "GeeksforGeeks", "resource_type": "Technical Article", "url": "https://www.geeksforgeeks.org/acid-properties-in-dbms/", "beginner_friendly": True},
        {"title": "DBMS Concurrency Control and Two-Phase Locking", "platform": "Tutorialspoint", "resource_type": "Tutorial", "url": "https://www.tutorialspoint.com/dbms/dbms_concurrency_control.htm", "beginner_friendly": False},
        {"title": "Transactions and Locks in Relational Databases", "platform": "Microsoft Learn", "resource_type": "Official Documentation", "url": "https://learn.microsoft.com/en-us/sql/relational-databases/sql-server-transaction-locking-and-row-versioning-guide", "beginner_friendly": False}
    ],

    # 5. Operating Systems
    "Process Management & Scheduling": [
        {"title": "CPU Scheduling in Operating Systems (Round Robin, FCFS)", "platform": "GeeksforGeeks", "resource_type": "Technical Article", "url": "https://www.geeksforgeeks.org/cpu-scheduling-in-operating-systems/", "beginner_friendly": True},
        {"title": "Operating System Process Scheduling", "platform": "Tutorialspoint", "resource_type": "Tutorial", "url": "https://www.tutorialspoint.com/operating_system/os_process_scheduling.htm", "beginner_friendly": True}
    ],
    "Threads & Concurrency": [
        {"title": "Process Synchronization and Semaphores", "platform": "GeeksforGeeks", "resource_type": "Technical Article", "url": "https://www.geeksforgeeks.org/introduction-of-process-synchronization/", "beginner_friendly": True},
        {"title": "Threads and Synchronization Overview", "platform": "Microsoft Learn", "resource_type": "Official Documentation", "url": "https://learn.microsoft.com/en-us/windows/win32/sync/synchronization", "beginner_friendly": False}
    ],
    "Deadlocks": [
        {"title": "Deadlock in Operating System and Banker's Algorithm", "platform": "GeeksforGeeks", "resource_type": "Technical Article", "url": "https://www.geeksforgeeks.org/introduction-of-deadlock-in-operating-system/", "beginner_friendly": True},
        {"title": "Operating System Deadlock Prevention and Avoidance", "platform": "Tutorialspoint", "resource_type": "Tutorial", "url": "https://www.tutorialspoint.com/operating_system/os_deadlocks.htm", "beginner_friendly": False}
    ],
    "Memory Management & Paging": [
        {"title": "Virtual Memory, Paging, and Page Faults", "platform": "GeeksforGeeks", "resource_type": "Technical Article", "url": "https://www.geeksforgeeks.org/virtual-memory-in-operating-system/", "beginner_friendly": True},
        {"title": "Operating System Memory Management Strategies", "platform": "Tutorialspoint", "resource_type": "Tutorial", "url": "https://www.tutorialspoint.com/operating_system/os_memory_management.htm", "beginner_friendly": False}
    ],
    "File Systems & Disk Scheduling": [
        {"title": "Disk Scheduling Algorithms (SCAN, C-LOOK, SSTF)", "platform": "GeeksforGeeks", "resource_type": "Technical Article", "url": "https://www.geeksforgeeks.org/disk-scheduling-algorithms/", "beginner_friendly": True},
        {"title": "Operating System File Systems and Inodes", "platform": "Tutorialspoint", "resource_type": "Tutorial", "url": "https://www.tutorialspoint.com/operating_system/os_file_system.htm", "beginner_friendly": False}
    ],

    # 6. Computer Networks
    "OSI & TCP/IP Models": [
        {"title": "Layers of OSI Model and Encapsulation", "platform": "GeeksforGeeks", "resource_type": "Technical Article", "url": "https://www.geeksforgeeks.org/layers-of-osi-model/", "beginner_friendly": True},
        {"title": "What is the OSI Model? 7 Layers Explained", "platform": "Cloudflare Learning", "resource_type": "Educational Guide", "url": "https://www.cloudflare.com/learning/ddos/glossary/open-systems-interconnection-model-osi/", "beginner_friendly": True}
    ],
    "IP Addressing & Subnetting": [
        {"title": "Introduction to IP Addressing and Subnetting", "platform": "GeeksforGeeks", "resource_type": "Technical Article", "url": "https://www.geeksforgeeks.org/introduction-to-subnetting/", "beginner_friendly": True},
        {"title": "IP Addressing and Subnetting for New Users", "platform": "Cisco Documentation", "resource_type": "Official Documentation", "url": "https://www.cisco.com/c/en/us/support/docs/ip/routing-information-protocol-rip/13788-3.html", "beginner_friendly": False}
    ],
    "Routing Protocols": [
        {"title": "Routing Protocols (Distance Vector & Link State)", "platform": "GeeksforGeeks", "resource_type": "Technical Article", "url": "https://www.geeksforgeeks.org/routing-protocols-set-1/", "beginner_friendly": True},
        {"title": "Routing Protocol Basics (OSPF, BGP)", "platform": "Cisco Documentation", "resource_type": "Official Documentation", "url": "https://www.cisco.com/c/en/us/support/docs/ip/open-shortest-path-first-ospf/7039-1.html", "beginner_friendly": False}
    ],
    "Transport Layer (TCP vs UDP)": [
        {"title": "Differences Between TCP and UDP Protocols", "platform": "GeeksforGeeks", "resource_type": "Technical Article", "url": "https://www.geeksforgeeks.org/differences-between-tcp-and-udp/", "beginner_friendly": True},
        {"title": "What is TCP/IP and UDP Transmission?", "platform": "Cloudflare Learning", "resource_type": "Educational Guide", "url": "https://www.cloudflare.com/learning/network-layer/what-is-the-network-layer/", "beginner_friendly": True}
    ],
    "Application Protocols & DNS": [
        {"title": "What is DNS and How Does It Resolve Names?", "platform": "Cloudflare Learning", "resource_type": "Educational Guide", "url": "https://www.cloudflare.com/learning/dns/what-is-dns/", "beginner_friendly": True},
        {"title": "An Overview of HTTP and HTTPS Protocols", "platform": "MDN Web Docs", "resource_type": "Official Documentation", "url": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Overview", "beginner_friendly": True}
    ],

    # 7. Machine Learning
    "Supervised Learning: Regression": [
        {"title": "Linear Models and Regression in Scikit-Learn", "platform": "Scikit-Learn Documentation", "resource_type": "Official Documentation", "url": "https://scikit-learn.org/stable/modules/linear_model.html", "beginner_friendly": False},
        {"title": "Linear Regression in Machine Learning", "platform": "GeeksforGeeks", "resource_type": "Technical Article", "url": "https://www.geeksforgeeks.org/ml-linear-regression/", "beginner_friendly": True},
        {"title": "Machine Learning Crash Course: Linear Regression", "platform": "Google Developers", "resource_type": "Interactive Tutorial", "url": "https://developers.google.com/machine-learning/crash-course/linear-regression", "beginner_friendly": True}
    ],
    "Supervised Learning: Classification": [
        {"title": "Classification Algorithms Overview", "platform": "Scikit-Learn Documentation", "resource_type": "Official Documentation", "url": "https://scikit-learn.org/stable/supervised_learning.html", "beginner_friendly": False},
        {"title": "Classification in Machine Learning: Algorithms & Metrics", "platform": "GeeksforGeeks", "resource_type": "Technical Article", "url": "https://www.geeksforgeeks.org/classification-in-machine-learning/", "beginner_friendly": True}
    ],
    "Model Evaluation & Bias-Variance": [
        {"title": "Model Evaluation Metrics: Precision, Recall, ROC-AUC", "platform": "Google Developers", "resource_type": "Official Guide", "url": "https://developers.google.com/machine-learning/crash-course/classification/precision-and-recall", "beginner_friendly": True},
        {"title": "Quantifying Prediction Quality with Metrics", "platform": "Scikit-Learn Documentation", "resource_type": "Official Documentation", "url": "https://scikit-learn.org/stable/modules/model_evaluation.html", "beginner_friendly": False}
    ],
    "Unsupervised Learning & Clustering": [
        {"title": "Clustering with K-Means and Dimensionality Reduction", "platform": "Scikit-Learn Documentation", "resource_type": "Official Documentation", "url": "https://scikit-learn.org/stable/modules/clustering.html", "beginner_friendly": False},
        {"title": "K-Means Clustering Algorithm Explained", "platform": "GeeksforGeeks", "resource_type": "Technical Article", "url": "https://www.geeksforgeeks.org/k-means-clustering-introduction/", "beginner_friendly": True}
    ],
    "Neural Networks & Deep Learning": [
        {"title": "Deep Learning Foundations and Model Building", "platform": "TensorFlow Tutorials", "resource_type": "Official Documentation", "url": "https://www.tensorflow.org/tutorials", "beginner_friendly": False},
        {"title": "Neural Networks Chapter Series with Visual Intuition", "platform": "3Blue1Brown", "resource_type": "Visual Explanation", "url": "https://www.3blue1brown.com/topics/neural-networks", "beginner_friendly": True},
        {"title": "Artificial Neural Networks (ANN) Tutorial", "platform": "GeeksforGeeks", "resource_type": "Technical Article", "url": "https://www.geeksforgeeks.org/artificial-neural-networks-ann/", "beginner_friendly": True}
    ]
}

def recommend_learning_resources(
    subject_name: str,
    topic_name: str,
    proficiency: str = "Intermediate",
    priority: str = "Medium"
) -> List[Dict[str, str]]:
    """
    Intelligently recommends 3-5 verified learning resources for a given topic and subject.
    Adapts based on student proficiency:
    - If Beginner or High Priority (weak topic): Prioritizes beginner-friendly tutorials, 
      interactive walkthroughs, and conceptual step-by-step guides.
    - If Advanced: Surfaces in-depth official documentation, architecture blogs, and design specs.
    """
    # 1. Check exact match in verified repository
    matched_resources = None
    for catalog_topic, res_list in TOPIC_LEARNING_RESOURCES.items():
        if catalog_topic.lower() == topic_name.lower() or catalog_topic.lower() in topic_name.lower() or topic_name.lower() in catalog_topic.lower():
            matched_resources = list(res_list)
            break

    # 2. Dynamic generation for unlisted/custom topics using verified educational domains
    if not matched_resources:
        encoded_query = urllib.parse.quote_plus(f"{subject_name} {topic_name}")
        encoded_topic = urllib.parse.quote_plus(topic_name)
        matched_resources = [
            {
                "title": f"GeeksforGeeks – {topic_name} Tutorial & Practical Examples",
                "platform": "GeeksforGeeks",
                "resource_type": "Technical Article",
                "url": f"https://www.geeksforgeeks.org/search/?q={encoded_query}",
                "beginner_friendly": True
            },
            {
                "title": f"W3Schools / MDN – Learning {topic_name}",
                "platform": "W3Schools / MDN",
                "resource_type": "Interactive Tutorial",
                "url": f"https://developer.mozilla.org/en-US/search?q={encoded_topic}",
                "beginner_friendly": True
            },
            {
                "title": f"freeCodeCamp – {topic_name} Conceptual Walkthrough",
                "platform": "freeCodeCamp",
                "resource_type": "Educational Guide",
                "url": f"https://www.freecodecamp.org/news/search/?query={encoded_topic}",
                "beginner_friendly": True
            },
            {
                "title": f"DevDocs Official Specification – {topic_name}",
                "platform": "DevDocs",
                "resource_type": "Official Documentation",
                "url": f"https://devdocs.io/#q={encoded_topic}",
                "beginner_friendly": False
            }
        ]

    # 3. Adaptive sorting based on student proficiency & weak priority
    is_weak = (proficiency == "Beginner" or priority == "High")
    
    if is_weak:
        # Prioritize beginner-friendly tutorials at the top
        matched_resources.sort(key=lambda r: 0 if r.get("beginner_friendly", False) else 1)
    else:
        # Balanced or advanced priority
        matched_resources.sort(key=lambda r: 0 if r.get("resource_type") == "Official Documentation" else 1)

    # Return top 3 to 5 resources formatted cleanly
    selected = matched_resources[:5] if len(matched_resources) >= 5 else matched_resources[:4]
    
    return [
        {
            "title": r["title"],
            "platform": r["platform"],
            "resource_type": r["resource_type"],
            "url": r["url"]
        }
        for r in selected
    ]


class PersonalizedStudyPlannerAgent:
    """
    Agent 2: Personalized Study Planner Agent
    Responsibilities:
    - Receive assessment results and topic mastery
    - Analyze weak topics, goals, and available study hours
    - Generate daily and weekly study schedules
    - Prioritize difficult/weak topics with increased time allocation
    - Automatically recommend curated 3-5 learning resources per task
    - Automatically revise study plans after new assessments or progress triggers
    - Enforce human-in-the-loop approval before major changes
    """

    def __init__(self, db: Session):
        self.db = db
        self.name = "Personalized Study Planner Agent"

    def create_or_update_plan(
        self,
        user_id: int,
        subject_id: int,
        available_hours: float = 2.0,
        weak_topics: Optional[List[str]] = None,
        learning_goal: Optional[str] = None,
        is_adaptive_revision: bool = False,
        require_approval: bool = False
    ) -> Dict[str, Any]:
        subject = self.db.query(Subject).filter(Subject.id == subject_id).first()
        if not subject:
            raise ValueError(f"Subject {subject_id} not found")

        topics = self.db.query(Topic).filter(Topic.subject_id == subject_id).order_by(Topic.order_index).all()
        
        # Query existing topic masteries for this student
        masteries = self.db.query(TopicMastery).filter(
            TopicMastery.user_id == user_id,
            TopicMastery.topic_id.in_([t.id for t in topics])
        ).all()
        mastery_map = {m.topic_id: m.proficiency_level for m in masteries}

        topics_data = []
        for t in topics:
            # If explicit weak topics were passed from assessment, treat them as Beginner
            prof = "Beginner" if (weak_topics and t.name in weak_topics) else mastery_map.get(t.id, "Intermediate")
            topics_data.append({
                "id": t.id,
                "name": t.name,
                "proficiency": prof,
                "difficulty": t.difficulty_level,
                "key_concepts": t.key_concepts
            })

        allocations = calculate_time_allocations(available_hours, topics_data)

        # Build daily tasks across Monday to Saturday
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        tasks_payload = []
        
        # Sort topics so high priority (weakest) come first
        sorted_allocations = sorted(
            allocations,
            key=lambda x: (0 if x["priority"] == "High" else (1 if x["priority"] == "Medium" else 2))
        )

        for idx, alloc in enumerate(sorted_allocations):
            day = days[idx % len(days)]
            topic_name = alloc["topic_name"]
            priority = alloc["priority"]
            proficiency = alloc.get("proficiency", "Intermediate")

            # Recommend 3-5 learning resources tailored to this topic & proficiency
            recommended_resources = recommend_learning_resources(
                subject_name=subject.name,
                topic_name=topic_name,
                proficiency=proficiency,
                priority=priority
            )

            if priority == "High":
                title = f"Deep Dive & Intensive Practice: {topic_name}"
                desc = f"Priority topic identified with knowledge gaps. Focus on fundamental mental models, step-by-step problem sets, and code walkthroughs. ({alloc['estimated_minutes']} mins)"
            elif priority == "Medium":
                title = f"Core Study & Exercises: {topic_name}"
                desc = f"Standard reinforcement of key concepts and practice questions. ({alloc['estimated_minutes']} mins)"
            else:
                title = f"Quick Review & Mastery Verification: {topic_name}"
                desc = f"Brief refresher session and advanced quiz to preserve mastery. ({alloc['estimated_minutes']} mins)"

            tasks_payload.append({
                "topic_id": alloc["topic_id"],
                "topic_name": topic_name,
                "title": title,
                "description": desc,
                "day_of_week": day,
                "estimated_minutes": alloc["estimated_minutes"],
                "priority": priority,
                "resources": recommended_resources
            })

        weekly_objectives = [
            f"Overcome identified weaknesses in {[a['topic_name'] for a in sorted_allocations if a['priority'] == 'High'] or ['foundational principles']}",
            f"Achieve consistent >= 80% quiz score on all {subject.name} modules",
            f"Dedicate {available_hours} hours daily with prioritized time allocations",
            "Complete end-of-week comprehensive milestone practice"
        ]

        # Check existing active study plan
        existing_plan = self.db.query(StudyPlan).filter(
            StudyPlan.user_id == user_id,
            StudyPlan.subject_id == subject_id,
            StudyPlan.is_active == True
        ).first()

        if is_adaptive_revision and require_approval and existing_plan:
            # Place in pending revision for human approval
            pending_data = {
                "weekly_objectives": weekly_objectives,
                "focus_topics": [a["topic_name"] for a in sorted_allocations if a["priority"] == "High"],
                "tasks": tasks_payload,
                "available_hours": available_hours,
                "reason": "Adaptive feedback detected persistent weakness. Human approval requested before updating live schedule."
            }
            existing_plan.pending_revision_json = json.dumps(pending_data)
            existing_plan.status = "Pending_Approval"
            self.db.commit()

            log_agent_action(
                db=self.db,
                user_id=user_id,
                agent_name=self.name,
                action=f"Proposed Adaptive Plan Revision for {subject.name}",
                reasoning="Progress agent identified gaps. Drafted revised timetable with recommended learning resources. Awaiting human approval before applying changes.",
                decision="Human approval required",
                state_cycle="Plan",
                input_data={"weak_topics": weak_topics, "available_hours": available_hours},
                output_data={"pending_revision": pending_data}
            )

            return {
                "plan_id": existing_plan.id,
                "status": "Pending_Approval",
                "message": "Study plan revision proposed. Awaiting student approval.",
                "pending_revision": pending_data
            }

        if existing_plan:
            # Update existing plan
            existing_plan.title = f"Adaptive Learning Schedule - {subject.name}"
            existing_plan.weekly_objectives = json.dumps(weekly_objectives)
            existing_plan.focus_topics = json.dumps([a["topic_name"] for a in sorted_allocations if a["priority"] == "High"])
            existing_plan.available_hours = available_hours
            existing_plan.adaptation_count += 1
            existing_plan.status = "Active"
            existing_plan.pending_revision_json = None
            existing_plan.updated_at = datetime.datetime.utcnow()

            # Remove previous incomplete tasks and insert revised tasks
            self.db.query(StudyTask).filter(
                StudyTask.study_plan_id == existing_plan.id,
                StudyTask.is_completed == False
            ).delete()

            plan = existing_plan
        else:
            plan = StudyPlan(
                user_id=user_id,
                subject_id=subject_id,
                title=f"Personalized Master Plan: {subject.name}",
                weekly_objectives=json.dumps(weekly_objectives),
                focus_topics=json.dumps([a["topic_name"] for a in sorted_allocations if a["priority"] == "High"]),
                available_hours=available_hours,
                is_active=True,
                status="Active",
                adaptation_count=0
            )
            self.db.add(plan)
            self.db.flush()

        # Add tasks with attached learning resources
        created_tasks = []
        for tp in tasks_payload:
            task = StudyTask(
                study_plan_id=plan.id,
                topic_id=tp["topic_id"],
                title=tp["title"],
                description=tp["description"],
                day_of_week=tp["day_of_week"],
                estimated_minutes=tp["estimated_minutes"],
                priority=tp["priority"],
                is_completed=False,
                learning_resources_json=json.dumps(tp.get("resources", []))
            )
            self.db.add(task)
            self.db.flush()
            created_tasks.append({
                "id": task.id,
                "topic_id": task.topic_id,
                "topic_name": tp["topic_name"],
                "title": task.title,
                "description": task.description,
                "day_of_week": task.day_of_week,
                "estimated_minutes": task.estimated_minutes,
                "priority": task.priority,
                "is_completed": False,
                "resources": tp.get("resources", [])
            })

        self.db.commit()

        # Log agent planning action
        log_agent_action(
            db=self.db,
            user_id=user_id,
            agent_name=self.name,
            action=f"{'Revised' if is_adaptive_revision else 'Generated'} Study Plan for {subject.name}",
            reasoning=f"Allocated {available_hours} hours daily with dynamic weighting and attached 3-5 curated learning resources per task. Formulated {len(created_tasks)} tasks.",
            decision=f"Activated personalized timetable for {subject.name}. Priority focus on: {', '.join([a['topic_name'] for a in sorted_allocations if a['priority'] == 'High']) or 'General Mastery'}.",
            state_cycle="Plan",
            input_data={"available_hours": available_hours, "weak_topics": weak_topics},
            output_data={"plan_id": plan.id, "tasks_count": len(created_tasks)}
        )

        return {
            "plan_id": plan.id,
            "status": "Active",
            "title": plan.title,
            "weekly_objectives": weekly_objectives,
            "focus_topics": [a["topic_name"] for a in sorted_allocations if a["priority"] == "High"],
            "tasks": created_tasks
        }

    def approve_pending_plan(self, user_id: int, plan_id: int, approved: bool) -> Dict[str, Any]:
        """Human-in-the-loop approval endpoint for proposed study plan revisions."""
        plan = self.db.query(StudyPlan).filter(
            StudyPlan.id == plan_id,
            StudyPlan.user_id == user_id
        ).first()

        if not plan:
            raise ValueError(f"Study plan {plan_id} not found")

        if not approved:
            plan.status = "Active"
            plan.pending_revision_json = None
            self.db.commit()

            log_agent_action(
                db=self.db,
                user_id=user_id,
                agent_name=self.name,
                action="Human Decision: Rejected Plan Revision",
                reasoning="Student opted to retain current schedule without adopting agent's proposed adjustments.",
                decision="Preserved active schedule unchanged",
                state_cycle="Adapt"
            )
            return {"status": "Rejected", "message": "Proposed revision was rejected; existing plan remains active."}

        # Apply pending revision
        if plan.pending_revision_json:
            pending = json.loads(plan.pending_revision_json)
            plan.weekly_objectives = json.dumps(pending.get("weekly_objectives", []))
            plan.focus_topics = json.dumps(pending.get("focus_topics", []))
            plan.adaptation_count += 1
            plan.status = "Active"
            plan.pending_revision_json = None
            plan.updated_at = datetime.datetime.utcnow()

            # Replace uncompleted tasks with newly approved tasks
            self.db.query(StudyTask).filter(
                StudyTask.study_plan_id == plan.id,
                StudyTask.is_completed == False
            ).delete()

            for tp in pending.get("tasks", []):
                t = StudyTask(
                    study_plan_id=plan.id,
                    topic_id=tp.get("topic_id"),
                    title=tp.get("title"),
                    description=tp.get("description"),
                    day_of_week=tp.get("day_of_week", "Monday"),
                    estimated_minutes=tp.get("estimated_minutes", 30),
                    priority=tp.get("priority", "Medium"),
                    is_completed=False,
                    learning_resources_json=json.dumps(tp.get("resources", []))
                )
                self.db.add(t)

            self.db.commit()

            log_agent_action(
                db=self.db,
                user_id=user_id,
                agent_name=self.name,
                action="Human Decision: Approved Plan Revision",
                reasoning="Student approved the agent's proposed timetable adaptation. Live study schedule updated with tailored learning resources.",
                decision="Applied new adaptive priorities",
                state_cycle="Adapt"
            )

        return {"status": "Approved", "message": "Adaptive study plan successfully approved and activated!"}
