from flask import Flask, render_template, request, redirect, session, flash
import sqlite3
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask import jsonify

app = Flask(__name__)
app.secret_key = "task_secret_key"

# =========================
# DATABASE
# =========================

# =========================
# DATABASE
# =========================

def init_db():

    conn = sqlite3.connect("database.db")

    cursor = conn.cursor()

    # USERS TABLE
    cursor.execute("""

    CREATE TABLE IF NOT EXISTS users (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        username TEXT UNIQUE,

        email TEXT UNIQUE,

        password TEXT,

        avatar TEXT DEFAULT 'https://i.pravatar.cc/150?img=12'

    )

    """)

    # TASKS TABLE
    cursor.execute("""

    CREATE TABLE IF NOT EXISTS tasks (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        task_name TEXT NOT NULL,

        due_date TEXT,

        status TEXT DEFAULT 'Pending',

        priority TEXT DEFAULT 'Medium',

        stage TEXT DEFAULT 'Pending'

    )

    """)

    conn.commit()

    conn.close()


# RUN DATABASE
init_db()
    

    # =========================
# AI PRIORITY FUNCTION
# =========================

# =========================
# AI PRIORITY FUNCTION
# =========================

def generate_priority(task_name):

    task = task_name.lower()

    high_keywords = [

        "urgent",
        "exam",
        "project",
        "submission",
        "hackathon",
        "deadline",
        "important",
        "interview",
        "presentation",
        "meeting",
        "final"

    ]

    medium_keywords = [

        "assignment",
        "study",
        "practice",
        "coding",
        "prepare",
        "work"

    ]

    # HIGH PRIORITY
    for word in high_keywords:

        if word in task:
            return "High"

    # MEDIUM PRIORITY
    for word in medium_keywords:

        if word in task:
            return "Medium"

    # DEFAULT
    return "Low"
    
# =========================
# LOGIN PAGE
# =========================

@app.route('/', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE email=?",
            (email,)
        )

        user = cursor.fetchone()

        conn.close()

        if user and check_password_hash(user[3], password):

            session['user'] = user[1]
            session['email'] = user[2]
            session['avatar'] = user[4]

            return redirect('/dashboard')

        else:

            return "Invalid Email or Password"

    return render_template("login.html")


# =========================
# SIGNUP PAGE
# =========================

@app.route('/signup', methods=['GET', 'POST'])
def signup():

    if request.method == 'POST':

        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # DATABASE CONNECTION
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        # CHECK USER EXISTS
        cursor.execute(
            "SELECT * FROM users WHERE email=?",
            (email,)
        )

        existing_user = cursor.fetchone()

        if existing_user:

            conn.close()
            return "User already exists"

        # HASH PASSWORD
        hashed_password = generate_password_hash(password)

        # INSERT USER
        cursor.execute(
            """

            INSERT INTO users
            (username, email, password)

            VALUES (?, ?, ?)

            """,
            (username, email, hashed_password)
        )

        conn.commit()
        conn.close()

        return redirect('/')

    return render_template('signup.html')
# =========================
# DASHBOARD
# =========================

# =========================
# DASHBOARD
# =========================

# =========================
# DASHBOARD
# =========================

@app.route('/dashboard')
def dashboard():

    if 'user' not in session:
        return redirect('/')

    conn = sqlite3.connect('database.db')

    cursor = conn.cursor()

    # TOTAL TASKS
    cursor.execute(
        "SELECT COUNT(*) FROM tasks"
    )

    total_tasks = cursor.fetchone()[0]

    # COMPLETED TASKS
    cursor.execute(
        "SELECT COUNT(*) FROM tasks WHERE status='Completed'"
    )

    completed_tasks = cursor.fetchone()[0]

    # PENDING TASKS
    cursor.execute(
        "SELECT COUNT(*) FROM tasks WHERE status='Pending'"
    )

    pending_tasks = cursor.fetchone()[0]

    # RECENT TASKS
    cursor.execute(
        """
        SELECT task_name,
        due_date,
        status,
        priority

        FROM tasks

        ORDER BY id DESC

        LIMIT 5
        """
    )

    recent_tasks = cursor.fetchall()

    conn.close()

    return render_template(

        'dashboard.html',

        total_tasks=total_tasks,

        completed_tasks=completed_tasks,

        pending_tasks=pending_tasks,

        recent_tasks=recent_tasks,

        user=session['user']

    )

    # =========================
    # DEADLINE ALERTS
    # =========================

    today = datetime.today().date()

    tomorrow = today + timedelta(days=1)

    overdue_tasks = []

    due_today_tasks = []

    due_tomorrow_tasks = []

    for task in tasks:

        try:

            due_date = datetime.strptime(
                task[2],
                "%Y-%m-%d"
            ).date()

            # IGNORE COMPLETED
            if task[3] == "Completed":
                continue

            if due_date < today:

                overdue_tasks.append(task)

            elif due_date == today:

                due_today_tasks.append(task)

            elif due_date == tomorrow:

                due_tomorrow_tasks.append(task)

        except:
            pass

    conn.close()

    return render_template(

        'dashboard.html',

        tasks=tasks,

        total_tasks=total_tasks,

        completed_tasks=completed_tasks,

        pending_tasks=pending_tasks,

        productivity=productivity,

        overdue_tasks=overdue_tasks,

        due_today_tasks=due_today_tasks,

        due_tomorrow_tasks=due_tomorrow_tasks,

        user=session['user']

    )

# =========================
# TASKS PAGE
# =========================

# =========================
# TASKS PAGE
# =========================

@app.route('/tasks')
def tasks():

    if 'user' not in session:
        return redirect('/')

    search = request.args.get('search', '')

    status = request.args.get('status', '')

    priority = request.args.get('priority', '')

    conn = sqlite3.connect('database.db')

    cursor = conn.cursor()

    query = "SELECT * FROM tasks WHERE 1=1"

    params = []

    # SEARCH
    if search:

        query += " AND task_name LIKE ?"

        params.append(f"%{search}%")

    # STATUS FILTER
    if status:

        query += " AND status=?"

        params.append(status)

    # PRIORITY FILTER
    if priority:

        query += " AND priority=?"

        params.append(priority)

    cursor.execute(query, params)

    tasks = cursor.fetchall()

    conn.close()

    return render_template(

        'tasks.html',

        tasks=tasks,

        search=search,

        status=status,

        priority=priority

    )

    # =========================
    # DEADLINE ALERTS
    # =========================

    today = datetime.today().date()

    tomorrow = today + timedelta(days=1)

    overdue_tasks = []

    due_today_tasks = []

    due_tomorrow_tasks = []

    for task in tasks:

        try:

            due_date = datetime.strptime(
                task[2],
                "%Y-%m-%d"
            ).date()

            # SKIP COMPLETED
            if task[3] == "Completed":
                continue

            if due_date < today:

                overdue_tasks.append(task)

            elif due_date == today:

                due_today_tasks.append(task)

            elif due_date == tomorrow:

                due_tomorrow_tasks.append(task)

        except:
            pass

    conn.close()

    return render_template(

    'dashboard.html',

    total_tasks=total_tasks,

    completed_tasks=completed_tasks,

    pending_tasks=pending_tasks,

    productivity=productivity,

    tasks=tasks,

    user=session['user'],

    overdue_tasks=overdue_tasks,

    due_today_tasks=due_today_tasks,

    due_tomorrow_tasks=due_tomorrow_tasks

)

# =========================
# ADD TASK
# =========================

@app.route('/add_task', methods=['GET', 'POST'])
def add_task():

    if request.method == 'POST':

        task = request.form['task']

        due_date = request.form['due_date']

        # AI PRIORITY
        priority = generate_priority(task)

        conn = sqlite3.connect('database.db')

        cursor = conn.cursor()

        cursor.execute(

            """

            INSERT INTO tasks
            (task_name, due_date, status, priority, stage)

            VALUES (?, ?, ?, ?, ?)

            """,

            (
                task,
                due_date,
                'Pending',
                priority,
                'Pending'
            )

        )

        conn.commit()

        conn.close()
        flash("Task Added Successfully", "success")
        return redirect('/tasks')

    return render_template('add_task.html')

# =========================
# EDIT TASK
# =========================

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):

    if 'user' not in session:
        return redirect('/')

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    if request.method == 'POST':

        task_name = request.form['task']
        due_date = request.form['due_date']
        status = request.form['status']

        cursor.execute(

            """
            UPDATE tasks

            SET task_name=?,
                due_date=?,
                status=?

            WHERE id=?
            """,

            (task_name, due_date, status, id)

        )

        conn.commit()
        conn.close()
        flash("Task Updated Successfully", "info")
        return redirect('/tasks')

    cursor.execute(
        "SELECT * FROM tasks WHERE id=?",
        (id,)
    )

    task = cursor.fetchone()

    conn.close()

    return render_template(
        'edit_task.html',
        task=task
    )

# =========================
# COMPLETE TASK
# =========================

# COMPLETE TASK

@app.route('/complete/<int:id>')
def complete(id):

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute(

        "UPDATE tasks SET status=? WHERE id=?",

        ("Completed", id)

    )

    conn.commit()
    conn.close()
    flash("Task Completed Successfully", "success")
    return redirect('/tasks')



# =========================
# UPDATE TASK STAGE
# =========================

@app.route('/update_stage/<int:id>/<stage>')
def update_stage(id, stage):

    conn = sqlite3.connect('database.db')

    cursor = conn.cursor()

    # UPDATE STAGE
    cursor.execute(

        "UPDATE tasks SET stage=? WHERE id=?",

        (stage, id)

    )

    # AUTO UPDATE STATUS
    if stage == "Completed":

        cursor.execute(

            "UPDATE tasks SET status='Completed' WHERE id=?",

            (id,)

        )

    elif stage == "Pending":

        cursor.execute(

            "UPDATE tasks SET status='Pending' WHERE id=?",

            (id,)

        )

    else:

        cursor.execute(

            "UPDATE tasks SET status='In Progress' WHERE id=?",

            (id,)

        )

    conn.commit()

    conn.close()

    return "Success"


# =========================
# COMPLETED TASKS
# =========================

@app.route('/completed')
def completed():

    if 'user' not in session:
        return redirect('/')

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM tasks WHERE status='Completed'"
    )

    tasks = cursor.fetchall()

    conn.close()

    return render_template(
        'completed.html',
        tasks=tasks
    )


# =========================
# KANBAN BOARD
# =========================

@app.route('/kanban')
def kanban():

    # LOGIN PROTECTION
    if 'user' not in session:
        return redirect('/')

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # PENDING TASKS
    cursor.execute(
        "SELECT * FROM tasks WHERE stage='Pending'"
    )

    pending_tasks = cursor.fetchall()

    # IN PROGRESS TASKS
    cursor.execute(
        "SELECT * FROM tasks WHERE stage='In Progress'"
    )

    progress_tasks = cursor.fetchall()

    # COMPLETED TASKS
    cursor.execute(
        "SELECT * FROM tasks WHERE stage='Completed'"
    )

    completed_tasks = cursor.fetchall()

    conn.close()

    return render_template(

        'kanban.html',

        pending_tasks=pending_tasks,

        progress_tasks=progress_tasks,

        completed_tasks=completed_tasks

    )


# =========================
# CALENDAR
# =========================

@app.route('/calendar')
def calendar():

    if 'user' not in session:
        return redirect('/')

    return render_template('calendar.html')


@app.route('/calendar-data')
def calendar_data():

    conn = sqlite3.connect('database.db')

    cursor = conn.cursor()

    cursor.execute("""

        SELECT task_name, due_date, priority

        FROM tasks

    """)

    tasks = cursor.fetchall()

    conn.close()

    events = []

    for task in tasks:

        task_name = task[0]
        due_date = task[1]
        priority = task[2]

        color = "#7b2cff"

        if priority == "High":

            color = "#ff3b30"

        elif priority == "Medium":

            color = "#ff9800"

        elif priority == "Low":

            color = "#2ecc71"

        events.append({

            "title": task_name,

            "start": due_date,

            "color": color

        })

    return jsonify(events)
# =========================
# REPORTS
# =========================

@app.route('/reports')
def reports():

    if 'user' not in session:
        return redirect('/')

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM tasks"
    )

    total_tasks = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM tasks WHERE status='Completed'"
    )

    completed_tasks = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM tasks WHERE status='Pending'"
    )

    pending_tasks = cursor.fetchone()[0]

    conn.close()

    productivity = 0

    if total_tasks > 0:

        productivity = int(
            (completed_tasks / total_tasks) * 100
        )

    return render_template(

        'reports.html',

        total_tasks=total_tasks,

        completed_tasks=completed_tasks,

        pending_tasks=pending_tasks,

        productivity=productivity

    )


# =========================
# PROFILE
# =========================

# =========================
# PROFILE
# =========================

@app.route('/profile')
def profile():

    if 'user' not in session:
        return redirect('/')

    user_name = session.get('user')

    avatar = session.get('avatar')

    email = session.get('email')

    return render_template(

        'profile.html',

        user_name=user_name,

        avatar=avatar,

        email=email

    )


    # =========================
# CHANGE AVATAR
# =========================

@app.route('/change_avatar', methods=['POST'])
def change_avatar():

    avatar = request.form['avatar']

    conn = sqlite3.connect('database.db')

    cursor = conn.cursor()

    cursor.execute(

        "UPDATE users SET avatar=? WHERE email=?",

        (
            avatar,
            session['email']
        )

    )

    conn.commit()
    conn.close()

    session['avatar'] = avatar

    return redirect('/profile')
# =========================
# DELETE TASK
# =========================

@app.route('/delete/<int:id>')
def delete_task(id):

    if 'user' not in session:
        return redirect('/')

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM tasks WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()
    flash("Task Deleted", "danger")
    return redirect('/tasks')

# =========================
# LOGOUT
# =========================

@app.route('/logout')
def logout():

    session.clear()

    return redirect('/')

# =========================
# RUN APP
# =========================

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)