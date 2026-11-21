"""
LearnSphere AI - Database Inspection Utility
Run this script to inspect all tables and records in learnsphere.db
Usage:
    cd backend
    .\venv\Scripts\python inspect_db.py
"""
import sqlite3
import json
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "learnsphere.db")

def inspect():
    if not os.path.exists(DB_PATH):
        print(f"Error: Database file not found at {DB_PATH}")
        return

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    print("=" * 60)
    print("      LearnSphere AI - SQLite Database Inspection")
    print("=" * 60)
    print(f"Database File: {DB_PATH}\n")

    # 1. List all tables
    tables = [t[0] for t in cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()]
    print(f"Tables Found ({len(tables)}):")
    for t in tables:
        count = cur.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        print(f"  - {t:<25} ({count} rows)")
    print("-" * 60)

    # 2. Users
    print("\n[1] Users (users):")
    users = cur.execute("SELECT id, email, full_name, is_active FROM users").fetchall()
    for u in users:
        print(f"  ID: {u[0]} | Email: {u[1]:<25} | Name: {u[2]:<15} | Active: {u[3]}")

    # 3. Subjects & Topics
    print("\n[2] Subjects (subjects):")
    subjects = cur.execute("SELECT id, name, code, is_custom FROM subjects").fetchall()
    for s in subjects:
        t_count = cur.execute("SELECT COUNT(*) FROM topics WHERE subject_id=?", (s[0],)).fetchone()[0]
        print(f"  ID: {s[0]} | {s[1]:<30} | Code: {s[2]:<10} | Topics: {t_count}")

    # 4. Study Plans & Tasks with AI Learning Resources
    print("\n[3] Active Study Plans & Tasks (study_plans & study_tasks):")
    plans = cur.execute("SELECT id, user_id, subject_id, title, status, adaptation_count FROM study_plans").fetchall()
    for p in plans:
        print(f"  Plan ID: {p[0]} | Title: {p[3]} | Status: {p[4]} | Adaptations: {p[5]}")
        tasks = cur.execute("""
            SELECT id, title, day_of_week, estimated_minutes, priority, is_completed, learning_resources_json 
            FROM study_tasks WHERE study_plan_id=?
        """, (p[0],)).fetchall()
        for t in tasks:
            done = "[X]" if t[5] else "[ ]"
            resources = []
            try:
                if t[6]:
                    resources = json.loads(t[6])
            except Exception:
                pass
            print(f"    {done} Task #{t[0]} [{t[2]}] {t[1]} ({t[3]} min, {t[4]} Priority)")
            print(f"       -> AI Recommended Resources: {len(resources)} resources attached")
            for r in resources[:2]:
                print(f"          * [{r.get('platform')}] {r.get('title')} ({r.get('resource_type')})")
            if len(resources) > 2:
                print(f"          * ... and {len(resources) - 2} more")

    # 5. Topic Mastery
    print("\n[4] Student Topic Mastery (topic_mastery):")
    mastery = cur.execute("""
        SELECT tm.id, t.name, tm.proficiency_level, tm.score_percentage, tm.attempts_count 
        FROM topic_mastery tm JOIN topics t ON tm.topic_id = t.id
    """).fetchall()
    if mastery:
        for m in mastery:
            print(f"  Topic: {m[1]:<35} | Level: {m[2]:<12} | Score: {m[3]}% | Attempts: {m[4]}")
    else:
        print("  (No topic mastery records yet - take a diagnostic test or quiz)")

    # 6. Recent Agent Activity Logs
    print("\n[5] Recent Multi-Agent Activity Logs (agent_activity_logs):")
    logs = cur.execute("""
        SELECT id, agent_name, action, state_cycle, timestamp 
        FROM agent_activity_logs ORDER BY id DESC LIMIT 5
    """).fetchall()
    if logs:
        for l in logs:
            print(f"  Log #{l[0]:<3} | [{l[3]:<8}] {l[1]:<35} | {l[2]}")
    else:
        print("  (No logs recorded yet)")

    print("\n" + "=" * 60)
    print("Database inspection complete!")
    print("=" * 60)
    con.close()

if __name__ == "__main__":
    inspect()
