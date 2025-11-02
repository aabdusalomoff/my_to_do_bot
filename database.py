import sqlite3

def create_table():
    conn = sqlite3.connect("todo.db")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            task TEXT,
            category TEXT DEFAULT 'Без категории',
            is_done BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def add_task(user_id, task, category="Без категории"):
    conn = sqlite3.connect("todo.db")
    conn.execute(
        "INSERT INTO tasks (user_id, task, category) VALUES (?, ?, ?)",
        (user_id, task, category)
    )
    conn.commit()
    conn.close()

def get_tasks(user_id):
    conn = sqlite3.connect("todo.db")
    tasks = conn.execute(
        "SELECT id, task, category, is_done, created_at FROM tasks WHERE user_id=?",
        (user_id,)
    ).fetchall()
    conn.close()
    return tasks

def get_tasks_by_category(user_id, category):
    conn = sqlite3.connect("todo.db")
    tasks = conn.execute(
        "SELECT id, task, category, is_done, created_at FROM tasks WHERE user_id=? AND category=?",
        (user_id, category)
    ).fetchall()
    conn.close()
    return tasks

def get_task_by_id(task_id):
    conn = sqlite3.connect("todo.db")
    task = conn.execute(
        "SELECT id, task, category, is_done, created_at FROM tasks WHERE id=?",
        (task_id,)
    ).fetchone()
    conn.close()
    return task

def mark_done(task_id):
    conn = sqlite3.connect("todo.db")
    conn.execute("UPDATE tasks SET is_done=1 WHERE id=?", (task_id,))
    conn.commit()
    conn.close()

def delete_task(task_id):
    conn = sqlite3.connect("todo.db")
    conn.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    conn.commit()
    conn.close()

def clear_tasks(user_id):
    conn = sqlite3.connect("todo.db")
    conn.execute("DELETE FROM tasks WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()
