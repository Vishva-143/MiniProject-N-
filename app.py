import os
import re
import random
import io
from datetime import datetime

import bcrypt
import mysql.connector
from mysql.connector import errors as mysql_errors
from dotenv import load_dotenv
from flask import (
    Flask,
    abort,
    flash,
    g,
    jsonify,
    redirect,
    render_template,
    request,
    send_file,
    session,
    url_for,
)
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from werkzeug.utils import secure_filename

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "secret123")
UPLOAD_FOLDER = os.path.join(app.root_path, "static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def get_db():
    return mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="SriVishnu@143",
        database="bima",
        port=3306,
    )


def ensure_schema():
    try:
        conn = get_db()
        cur = conn.cursor(buffered=True)
        cur.execute(
            """
            SELECT COUNT(*) FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'announcements' AND COLUMN_NAME = 'file'
            """
        )
        if cur.fetchone()[0] == 0:
            cur.execute("ALTER TABLE announcements ADD COLUMN file VARCHAR(255) NULL")
            conn.commit()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS classes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                class_name VARCHAR(100) NOT NULL
            )
            """
        )
        cur.execute("SELECT COUNT(*) FROM classes")
        if cur.fetchone()[0] == 0:
            for cn in ("MCA Sem 1", "MCA Sem 2", "MBA Sem 1", "MBA Sem 2"):
                cur.execute("INSERT INTO classes (class_name) VALUES (%s)", (cn,))
        cur.execute(
            """
            INSERT IGNORE INTO branches (name) VALUES ('MCA'), ('MBA')
            """
        )
        for sem in range(1, 5):
            cur.execute("INSERT IGNORE INTO semesters (sem_no) VALUES (%s)", (sem,))

        # Add email column if it does not exist in students table
        cur.execute(
            "SELECT COUNT(*) FROM information_schema.COLUMNS "
            "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'students' "
            "AND COLUMN_NAME = 'email'"
        )
        if cur.fetchone()[0] == 0:
            cur.execute("ALTER TABLE students ADD COLUMN email VARCHAR(100) UNIQUE NULL")

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS student_subjects (
                id INT AUTO_INCREMENT PRIMARY KEY,
                student_id VARCHAR(20) NOT NULL,
                subject_id INT NOT NULL,
                UNIQUE KEY uniq_student_subject (student_id, subject_id)
            )
            """
        )
        # Add unique key to marks if not exists
        cur.execute(
            """
            SELECT COUNT(*) FROM information_schema.TABLE_CONSTRAINTS
            WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'marks' AND CONSTRAINT_NAME = 'unique_student_subject'
            """
        )
        if cur.fetchone()[0] == 0:
            cur.execute("ALTER TABLE marks ADD UNIQUE KEY unique_student_subject (student_id, subject_id)")
        conn.commit()
        cur.close()
        conn.close()
    except Exception:
        pass


ensure_schema()


def sync_student_subjects(cur, student_id, branch_id, semester_id):
    """Map student to all subjects for their branch + semester (README student_subjects)."""
    if not branch_id or not semester_id or not student_id:
        return
    cur.execute("DELETE FROM student_subjects WHERE student_id=%s", (student_id,))
    cur.execute(
        """
        INSERT IGNORE INTO student_subjects (student_id, subject_id)
        SELECT %s, s.id FROM subjects s
        WHERE s.branch_id=%s AND s.semester_id=%s
        """,
        (student_id, branch_id, semester_id),
    )


def hash_pw(pw):
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()


def verify_password(stored, plain):
    if not stored:
        return False
    s = stored.strip()
    if s.startswith("$2"):
        try:
            return bcrypt.checkpw(plain.encode(), s.encode())
        except ValueError:
            return False
    return s == plain


def branch_id_by_name(cur, name):
    cur.execute("SELECT id FROM branches WHERE name=%s", (name,))
    row = cur.fetchone()
    if not row:
        return None
    # Handle both dictionary and tuple results
    return row.get("id") if isinstance(row, dict) else row[0]


def semester_id_by_num(cur, sem_no):
    cur.execute("SELECT id FROM semesters WHERE sem_no=%s", (int(sem_no),))
    row = cur.fetchone()
    if not row:
        return None
    # Handle both dictionary and tuple results
    return row.get("id") if isinstance(row, dict) else row[0]


def parse_semester_choice(val):
    if val is None:
        return 1
    m = re.search(r"(\d+)", str(val))
    return int(m.group(1)) if m else 1


def fetch_student_semester_marks(cur, student_id, branch_id, semester_id):
    if not student_id or not branch_id or not semester_id:
        return {"marks": [], "summary": {"total_marks": 0, "percentage": 0}}

    cur.execute(
        """
        SELECT s.id AS subject_id, s.subject_name,
               COALESCE(m.internal_exam_1,0) AS marks1,
               COALESCE(m.internal_exam_2,0) AS marks2,
               COALESCE(m.internal_exam_3,0) AS marks3
        FROM subjects s
        LEFT JOIN marks m ON m.subject_id = s.id AND m.student_id = %s
        WHERE s.branch_id = %s AND s.semester_id = %s
        ORDER BY s.subject_name
        """,
        (student_id, branch_id, semester_id),
    )
    rows = cur.fetchall()

    marks = []
    grand_total = 0
    for r in rows:
        t = int(r["marks1"]) + int(r["marks2"]) + int(r["marks3"])
        grand_total += t
        marks.append(
            {
                "subject_id": r["subject_id"],
                "subject_name": r["subject_name"],
                "marks1": int(r["marks1"]),
                "marks2": int(r["marks2"]),
                "marks3": int(r["marks3"]),
                "total_marks": t,
            }
        )

    n = len(marks) or 1
    max_possible = n * 120
    pct = round((grand_total / max_possible) * 100, 2) if max_possible else 0
    return {"marks": marks, "summary": {"total_marks": grand_total, "percentage": pct}}


def class_label_to_branch_semester(class_name):
    if not class_name:
        return "MCA", 1
    cn = str(class_name)
    branch_name = "MCA" if "MCA" in cn else ("MBA" if "MBA" in cn else "MCA")
    m = re.search(r"Sem\s*(\d+)", cn, re.I)
    sem_no = int(m.group(1)) if m else 1
    return branch_name, sem_no


def fetch_semester_classes(cur):
    cur.execute(
        "SELECT id, class_name FROM classes WHERE class_name LIKE %s ORDER BY id",
        ("% - Semester %",),
    )
    return cur.fetchall()


def save_upload(file_storage, prefix):
    if not file_storage or not file_storage.filename:
        return None
    raw = secure_filename(file_storage.filename)
    if not raw:
        return None
    name = f"{prefix}_{random.randint(10000, 99999)}_{raw}"
    path = os.path.join(UPLOAD_FOLDER, name)
    file_storage.save(path)
    return name


@app.context_processor
def inject_role():
    return {"role": getattr(g, "role", None)}


@app.before_request
def load_user():
    g.role = session.get("role")
    g.user_id = session.get("user_id")


def require_roles(*roles):
    if g.role not in roles:
        return redirect(url_for("login"))
    return None


def require_admin():
    return require_roles("admin")


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        role = request.form.get("role", "admin")
        user_captcha = request.form.get("captcha", "")

        if user_captcha != session.get("captcha"):
            flash("Invalid CAPTCHA")
            return redirect(url_for("login"))

        conn = get_db()
        cur = conn.cursor(buffered=True, dictionary=True)

        if role == "admin":
            cur.execute(
                "SELECT * FROM admin WHERE username=%s", (username,)
            )
            row = cur.fetchone()
            if row and verify_password(row.get("password"), password):
                session["role"] = "admin"
                session["user_id"] = username
                cur.close()
                conn.close()
                return redirect(url_for("admin_dashboard"))
            if username == "admin" and password == "admin":
                session["role"] = "admin"
                session["user_id"] = "admin"
                cur.close()
                conn.close()
                return redirect(url_for("admin_dashboard"))

        elif role == "teacher":
            cur.execute("SELECT * FROM teachers WHERE teacher_id=%s", (username,))
            user = cur.fetchone()
            if user and verify_password(user["password"], password):
                session["role"] = "teacher"
                session["user_id"] = user["teacher_id"]
                cur.close()
                conn.close()
                return redirect(url_for("teacher_dashboard"))

        elif role == "student":
            cur.execute("SELECT * FROM students WHERE student_id=%s", (username,))
            user = cur.fetchone()
            if user and verify_password(user["password"], password):
                session["role"] = "student"
                session["user_id"] = user["student_id"]
                cur.close()
                conn.close()
                return redirect(url_for("student_dashboard"))

        cur.close()
        conn.close()
        flash("Invalid login")

    captcha = str(random.randint(10000, 99999))
    session["captcha"] = captcha
    return render_template("login.html", captcha=captcha)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/dashboard")
def dashboard_redirect():
    if g.role == "admin":
        return redirect(url_for("admin_dashboard"))
    if g.role == "teacher":
        return redirect(url_for("teacher_dashboard"))
    if g.role == "student":
        return redirect(url_for("student_dashboard"))
    return redirect(url_for("login"))


@app.route("/admin_dashboard")
def admin_dashboard():
    redir = require_admin()
    if redir:
        return redir

    conn = get_db()
    cur = conn.cursor(buffered=True, dictionary=True)

    cur.execute("SELECT COUNT(*) as total FROM students")
    total = cur.fetchone()["total"]

    cur.execute(
        """
        SELECT ROUND(AVG((internal_exam_1+internal_exam_2+internal_exam_3)/120*100),2) as avg
        FROM marks
        """
    )
    row = cur.fetchone()
    avg_marks = float(row["avg"] or 0)

    cur.execute(
        """
        SELECT s.name,
               ROUND(COALESCE(SUM(m.internal_exam_1 + m.internal_exam_2 + m.internal_exam_3),0) / 120 * 100, 2) AS percentage
        FROM students s
        LEFT JOIN marks m ON m.student_id = s.student_id
        GROUP BY s.student_id, s.name
        ORDER BY percentage DESC
        LIMIT 1
        """
    )
    top = cur.fetchone()
    topper = top["name"] if top else None

    cur.execute(
        """
        SELECT s.name,
               ROUND(COALESCE(SUM(m.internal_exam_1 + m.internal_exam_2 + m.internal_exam_3),0) / 120 * 100, 2) AS pct
        FROM students s
        LEFT JOIN marks m ON m.student_id = s.student_id
        GROUP BY s.student_id, s.name
        ORDER BY pct DESC
        LIMIT 15
        """
    )
    chart_rows = cur.fetchall()
    names = [r["name"] for r in chart_rows]
    marks = [float(r["pct"] or 0) for r in chart_rows]

    cur.execute(
        """
        SELECT cls, COUNT(*) AS cnt, ROUND(AVG(percentage),2) AS avgp
        FROM (
            SELECT s.student_id,
                   CONCAT(COALESCE(s.branch,''), ' Sem ', COALESCE(s.semester,0)) AS cls,
                   ROUND(COALESCE(SUM(m.internal_exam_1 + m.internal_exam_2 + m.internal_exam_3),0) / 120 * 100, 2) AS percentage
            FROM students s
            LEFT JOIN marks m ON m.student_id = s.student_id
            GROUP BY s.student_id, s.branch, s.semester
        ) AS sub
        GROUP BY cls
        ORDER BY cls
        """
    )
    cls = cur.fetchall()
    class_names = [r["cls"] for r in cls]
    class_counts = [r["cnt"] for r in cls]
    class_avg = [float(r["avgp"] or 0) for r in cls]

    cur.close()
    conn.close()

    return render_template(
        "admin_dashboard.html",
        total=total,
        avg=avg_marks,
        topper=topper,
        names=names,
        marks=marks,
        class_names=class_names,
        class_counts=class_counts,
        class_avg=class_avg,
    )


@app.route("/students")
def students():
    redir = require_roles("admin", "teacher")
    if redir:
        return redir

    conn = get_db()
    cur = conn.cursor(buffered=True, dictionary=True)
    classes = fetch_semester_classes(cur)

    selected_class_id = request.args.get("class_id", type=int)
    selected_class_name = None
    if selected_class_id:
        for cls in classes:
            if cls["id"] == selected_class_id:
                selected_class_name = cls["class_name"]
                break

    if selected_class_id:
        cur.execute(
            "SELECT s.*, c.class_name FROM students s LEFT JOIN classes c ON s.class_id = c.id WHERE s.class_id=%s ORDER BY s.student_id",
            (selected_class_id,),
        )
    else:
        cur.execute(
            "SELECT s.*, c.class_name FROM students s LEFT JOIN classes c ON s.class_id = c.id ORDER BY s.student_id"
        )

    rows = cur.fetchall()
    for s in rows:
        p = s.get("percentage")
        s["percentage"] = float(p) if p is not None else 0.0

    cur.close()
    conn.close()
    return render_template(
        "students.html",
        students=rows,
        classes=classes,
        selected_class_id=selected_class_id,
        selected_class_name=selected_class_name,
    )


@app.route("/teachers")
def teachers():
    if not g.role:
        return redirect(url_for("login"))
    conn = get_db()
    cur = conn.cursor(buffered=True, dictionary=True)
    cur.execute(
        """
        SELECT t.teacher_id, t.teacher_code, t.name, t.password, t.gender, t.dob,
               t.branch, t.subjects, t.phone, t.email, t.photo,
               COALESCE(GROUP_CONCAT(s.subject_name ORDER BY sem.sem_no, s.subject_name SEPARATOR ', '), '') AS subject_names
        FROM teachers t
        LEFT JOIN teacher_subjects ts ON ts.teacher_id = t.teacher_id
        LEFT JOIN subjects s ON ts.subject_id = s.id
        LEFT JOIN semesters sem ON s.semester_id = sem.id
        GROUP BY t.teacher_id, t.teacher_code, t.name, t.password,
                 t.gender, t.dob, t.branch, t.subjects, t.phone, t.email, t.photo
        ORDER BY t.teacher_id
        """
    )
    data = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("teachers.html", teachers=data)


@app.route("/register_student", methods=["GET", "POST"])
def register_student():
    if request.method == "POST":
        conn = get_db()
        cur = conn.cursor(buffered=True, dictionary=True)
        try:
            sem_no = parse_semester_choice(request.form.get("semester"))
            branch_name = request.form.get("branch", "MCA")
            bid = branch_id_by_name(cur, branch_name)
            sid_sem = semester_id_by_num(cur, sem_no)
            photo = save_upload(request.files.get("photo"), "stu")

            if bid is None or sid_sem is None:
                flash("Invalid branch or semester selected.", "error")
                cur.close()
                conn.close()
                return render_template("register_student.html")

            dob_raw = request.form.get("date_of_birth") or request.form.get("dob")
            try:
                dob = (
                    datetime.strptime(dob_raw, "%Y-%m-%d").date() if dob_raw else None
                )
            except ValueError:
                dob = None

            sid = request.form["student_id"].strip()
            cur.execute(
                """
                INSERT INTO students (
                    student_id, name, password, gender, dob, branch, semester,
                    branch_id, semester_id, mobile, father_mobile, photo, email
                )
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """,
                (
                    sid,
                    request.form["full_name"].strip(),
                    hash_pw(request.form["password"]),
                    request.form.get("gender"),
                    dob,
                    branch_name,
                    sem_no,
                    bid,
                    sid_sem,
                    request.form.get("mobile_number"),
                    request.form.get("father_mobile_number"),
                    photo,
                    request.form.get("email"),
                ),
            )

            selected_subjects = request.form.getlist("subjects") or request.form.getlist("subjects[]")
            selected_subjects = [s for s in selected_subjects if str(s).strip()]
            if selected_subjects:
                for subject_id in selected_subjects:
                    try:
                        cur.execute(
                            "INSERT INTO student_subjects (student_id, subject_id) VALUES (%s, %s)",
                            (sid, int(subject_id)),
                        )
                    except mysql_errors.Error:
                        pass
            else:
                # Fallback: assign all subjects for the selected branch and semester
                sync_student_subjects(cur, sid, bid, sid_sem)
            
            conn.commit()
        except mysql_errors.IntegrityError:
            conn.rollback()
            flash("Student ID already exists.", "error")
            cur.close()
            conn.close()
            return render_template("register_student.html")
        except mysql_errors.Error as e:
            conn.rollback()
            flash(f"Registration failed: {e}", "error")
            cur.close()
            conn.close()
            return render_template("register_student.html")
        cur.close()
        conn.close()
        return redirect(url_for("students"))

    return render_template("register_student.html")


@app.route("/register_teacher", methods=["GET", "POST"])
def register_teacher():
    if request.method == "POST":
        conn = get_db()
        cur = conn.cursor(buffered=True, dictionary=True)
        phone = re.sub(r"\D", "", request.form.get("phone", ""))
        teacher_id = request.form.get("teacher_id", "").strip()
        if not teacher_id:
            teacher_id = "T" + (phone[-4:] if len(phone) >= 4 else str(random.randint(1000, 9999)))
        cur.execute("SELECT 1 FROM teachers WHERE teacher_id=%s", (teacher_id,))
        if cur.fetchone():
            flash("Teacher ID already exists. Please choose a different ID.", "error")
            cur.close()
            conn.close()
            return render_template("register_teacher.html")

        code = teacher_id
        photo = save_upload(request.files.get("photo"), "tch")
        dob_raw = request.form.get("dob")
        try:
            tdob = datetime.strptime(dob_raw, "%Y-%m-%d").date() if dob_raw else None
        except ValueError:
            tdob = None

        gender = request.form.get("gender", "")
        if gender == "M":
            gender = "Male"
        elif gender == "F":
            gender = "Female"

        subs = request.form.getlist("subjects")
        sub_label = ",".join(subs) if subs else ""
        pw_hash = hash_pw(request.form["password"])
        name_clean = request.form["name"].strip()

        insert_vals = (
            teacher_id,
            code,
            name_clean,
            pw_hash,
            gender,
            tdob,
            request.form["branch"],
            sub_label,
            phone or None,
            request.form.get("email"),
            photo,
        )
        try:
            cur.execute(
                """
                INSERT INTO teachers (
                    teacher_id, teacher_code, name, password, gender, dob, branch,
                    subjects, phone, email, photo
                )
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """,
                insert_vals,
            )
        except mysql_errors.Error as err:
            if getattr(err, "errno", None) == 1054 and "teacher_code" in str(err):
                cur.execute(
                    """
                    INSERT INTO teachers (
                        teacher_id, name, password, gender, dob, branch,
                        subjects, phone, email, photo
                    )
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    """,
                    (
                        teacher_id,
                        name_clean,
                        pw_hash,
                        gender,
                        tdob,
                        request.form["branch"],
                        sub_label,
                        phone or None,
                        request.form.get("email"),
                        photo,
                    ),
                )
            else:
                conn.rollback()
                cur.close()
                conn.close()
                flash(f"Could not register teacher: {err}", "error")
                return render_template("register_teacher.html")
        try:
            for sub in subs:
                if str(sub).isdigit():
                    cur.execute(
                        "INSERT IGNORE INTO teacher_subjects (teacher_id, subject_id) VALUES (%s,%s)",
                        (teacher_id, int(sub)),
                    )
            conn.commit()
        except mysql_errors.Error as err:
            conn.rollback()
            cur.close()
            conn.close()
            flash(f"Could not save teacher: {err}", "error")
            return render_template("register_teacher.html")
        cur.close()
        conn.close()
        flash("Teacher registered successfully", "success")
        return redirect(url_for("teachers"))

    return render_template("register_teacher.html")


@app.route("/teacher_dashboard")
def teacher_dashboard():
    redir = require_roles("teacher")
    if redir:
        return redir

    conn = get_db()
    cur = conn.cursor(buffered=True, dictionary=True)

    cur.execute(
        "SELECT teacher_id, name, gender, dob, branch, phone, photo, email "
        "FROM teachers WHERE teacher_id=%s",
        (g.user_id,),
    )
    teacher = cur.fetchone()

    subjects = []
    subject_stats = {}
    total_students = set()
    total_marks = 0
    total_entries = 0
    total_pass = 0
    total_fail = 0

    if teacher:
        cur.execute(
            "SELECT s.id AS subject_id, s.subject_name, b.name AS branch_name, sem.sem_no "
            "FROM teacher_subjects ts "
            "JOIN subjects s ON ts.subject_id = s.id "
            "JOIN branches b ON s.branch_id = b.id "
            "JOIN semesters sem ON s.semester_id = sem.id "
            "WHERE ts.teacher_id=%s "
            "ORDER BY s.subject_name",
            (g.user_id,),
        )
        subjects = cur.fetchall()

    if subjects:
        for subj in subjects:
            subject_stats[subj["subject_id"]] = {
                "subject_id": subj["subject_id"],
                "subject_name": subj["subject_name"],
                "branch_name": subj["branch_name"],
                "semester": subj["sem_no"],
                "students": [],
                "topper": None,
                "average": 0.0,
                "total_marks": 0,
                "count": 0,
            }

        cur.execute(
            "SELECT s.id AS subject_id, st.student_id, st.name AS student_name, "
            "COALESCE(m.internal_exam_1, 0) + COALESCE(m.internal_exam_2, 0) + COALESCE(m.internal_exam_3, 0) AS marks "
            "FROM teacher_subjects ts "
            "JOIN subjects s ON ts.subject_id = s.id "
            "JOIN students st ON st.branch_id = s.branch_id AND st.semester_id = s.semester_id "
            "LEFT JOIN marks m ON m.subject_id = s.id AND m.student_id = st.student_id "
            "WHERE ts.teacher_id=%s "
            "ORDER BY s.subject_name, st.name",
            (g.user_id,),
        )
        rows = cur.fetchall()

        for row in rows:
            sid = row["subject_id"]
            stats = subject_stats.get(sid)
            if not stats:
                continue

            marks = int(row["marks"] or 0)
            status = "Pass" if marks >= 40 else "Fail"
            stats["students"].append(
                {
                    "student_id": row["student_id"],
                    "student_name": row["student_name"],
                    "marks": marks,
                    "status": status,
                }
            )
            stats["total_marks"] += marks
            stats["count"] += 1

            total_marks += marks
            total_entries += 1
            total_students.add(row["student_id"])
            if status == "Pass":
                total_pass += 1
            else:
                total_fail += 1

            if stats["topper"] is None or marks > stats["topper"]["marks"]:
                stats["topper"] = {
                    "student_name": row["student_name"],
                    "marks": marks,
                }

        for stats in subject_stats.values():
            stats["average"] = round(
                (stats["total_marks"] / stats["count"])
                if stats["count"] > 0
                else 0,
                2,
            )

    overall_average = round((total_marks / total_entries) if total_entries else 0, 2)
    pass_rate = round((total_pass / total_entries * 100), 2) if total_entries else 0
    fail_rate = round((total_fail / total_entries * 100), 2) if total_entries else 0

    subject_list = list(subject_stats.values())

    cur.close()
    conn.close()

    return render_template(
        "teacher_dashboard.html",
        teacher=teacher,
        subjects=subject_list,
        subject_count=len(subject_list),
        student_count=len(total_students),
        overall_average=overall_average,
        pass_rate=pass_rate,
        fail_rate=fail_rate,
    )


@app.route("/student_dashboard")
def student_dashboard():
    redir = require_roles("student")
    if redir:
        return redir

    conn = get_db()
    cur = conn.cursor(buffered=True, dictionary=True)
    cur.execute("SELECT * FROM students WHERE student_id=%s", (g.user_id,))
    student = cur.fetchone()
    cur.execute(
        """
        SELECT s.subject_name, m.internal_exam_1, m.internal_exam_2, m.internal_exam_3
        FROM marks m JOIN subjects s ON m.subject_id = s.id
        WHERE m.student_id=%s
        """,
        (g.user_id,),
    )
    marks = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("student_dashboard.html", student=student, marks=marks)


@app.route("/teacher/<teacher_id>")
def teacher_profile(teacher_id):
    redir = require_roles("admin", "teacher", "student")
    if redir:
        return redir

    conn = get_db()
    cur = conn.cursor(buffered=True, dictionary=True)
    cur.execute("SELECT * FROM teachers WHERE teacher_id=%s", (teacher_id,))
    teacher = cur.fetchone()
    if not teacher:
        cur.close()
        conn.close()
        abort(404)

    cur.execute(
        "SELECT s.subject_name FROM teacher_subjects ts "
        "JOIN subjects s ON ts.subject_id = s.id "
        "WHERE ts.teacher_id=%s "
        "ORDER BY s.semester_id, s.subject_name",
        (teacher_id,),
    )
    subject_rows = cur.fetchall()
    teacher["subject_names"] = ", ".join([row["subject_name"] for row in subject_rows]) if subject_rows else teacher.get("subjects", "")

    cur.close()
    conn.close()
    return render_template("teacher_details.html", teacher=teacher)


@app.route("/get_subjects_by_branch/<branch>")
def get_subjects_by_branch(branch):
    conn = get_db()
    cur = conn.cursor(buffered=True, dictionary=True)
    branch_id = branch_id_by_name(cur, branch)
    if not branch_id:
        cur.close()
        conn.close()
        return jsonify([])

    cur.execute(
        "SELECT s.id, s.subject_name, sem.sem_no AS semester "
        "FROM subjects s "
        "JOIN semesters sem ON s.semester_id = sem.id "
        "WHERE s.branch_id=%s "
        "ORDER BY sem.sem_no, s.subject_name",
        (branch_id,),
    )
    subjects = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(subjects)


@app.route("/student/<student_id>")
def student_profile(student_id):
    if not g.role:
        return redirect(url_for("login"))
    if g.role == "student" and g.user_id != student_id:
        abort(403)

    conn = get_db()
    cur = conn.cursor(buffered=True, dictionary=True)
    cur.execute(
        "SELECT s.*, c.class_name FROM students s LEFT JOIN classes c ON s.class_id = c.id WHERE s.student_id=%s",
        (student_id,),
    )
    student = cur.fetchone()
    if not student:
        cur.close()
        conn.close()
        abort(404)

    branch_name = ""
    if student.get("branch_id"):
        cur.execute("SELECT name FROM branches WHERE id=%s", (student["branch_id"],))
        br = cur.fetchone()
        if br:
            branch_name = br["name"]
    if not branch_name:
        branch_name = student.get("branch") or ""

    cur.execute("SELECT id, sem_no FROM semesters ORDER BY sem_no")
    semesters = cur.fetchall()

    current_semester_id = student.get("semester_id")
    current_semester_no = student.get("semester")
    if not current_semester_id and current_semester_no is not None:
        try:
            current_semester_id = semester_id_by_num(cur, current_semester_no)
        except Exception:
            current_semester_id = None

    if current_semester_id and not current_semester_no:
        cur.execute("SELECT sem_no FROM semesters WHERE id=%s", (current_semester_id,))
        sem_row = cur.fetchone()
        current_semester_no = sem_row["sem_no"] if sem_row else None

    previous_semester_id = None
    previous_semester_no = None
    try:
        sem_no_val = int(current_semester_no) if current_semester_no is not None else None
    except (TypeError, ValueError):
        sem_no_val = None

    if sem_no_val and sem_no_val > 1:
        previous_semester_no = sem_no_val - 1
        previous_semester_id = semester_id_by_num(cur, previous_semester_no)

    cur.close()
    conn.close()

    return render_template(
        "student_details.html",
        student=student,
        branch_name=branch_name,
        semesters=semesters,
        role=g.role,
        current_semester_id=current_semester_id,
        current_semester_no=current_semester_no,
        previous_semester_id=previous_semester_id,
        previous_semester_no=previous_semester_no,
    )


@app.route("/get_marks/<student_id>")
def get_marks(student_id):
    if not g.role:
        return jsonify({"error": "auth"}), 401
    if g.role == "student" and g.user_id != student_id:
        return jsonify({"error": "forbidden"}), 403

    semester_id = request.args.get("semester_id", type=int)
    if not semester_id:
        return jsonify({"marks": [], "summary": {"total_marks": 0, "percentage": 0}})

    conn = get_db()
    cur = conn.cursor(buffered=True, dictionary=True)
    cur.execute("SELECT * FROM students WHERE student_id=%s", (student_id,))
    stu = cur.fetchone()
    if not stu:
        cur.close()
        conn.close()
        return jsonify({"error": "not found"}), 404

    bid = stu.get("branch_id")
    if not bid and stu.get("branch"):
        cur.execute(
            "SELECT id FROM branches WHERE name=%s LIMIT 1", (stu["branch"],)
        )
        br = cur.fetchone()
        if br:
            bid = br["id"]
    if not bid:
        cur.close()
        conn.close()
        return jsonify(
            {"marks": [], "summary": {"total_marks": 0, "percentage": 0}}
        )

    cur.execute(
        """
        SELECT s.id AS subject_id, s.subject_name,
               COALESCE(m.internal_exam_1,0) AS marks1,
               COALESCE(m.internal_exam_2,0) AS marks2,
               COALESCE(m.internal_exam_3,0) AS marks3
        FROM subjects s
        LEFT JOIN marks m ON m.subject_id = s.id AND m.student_id = %s
        WHERE s.branch_id = %s AND s.semester_id = %s
        ORDER BY s.subject_name
        """,
        (student_id, bid, semester_id),
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()

    out = []
    grand = 0
    for r in rows:
        t = int(r["marks1"]) + int(r["marks2"]) + int(r["marks3"])
        grand += t
        out.append(
            {
                "subject_id": r["subject_id"],
                "subject_name": r["subject_name"],
                "marks1": int(r["marks1"]),
                "marks2": int(r["marks2"]),
                "marks3": int(r["marks3"]),
                "total_marks": t,
            }
        )
    n = len(out) or 1
    max_possible = n * 120
    pct = round((grand / max_possible) * 100, 2) if max_possible else 0
    return jsonify(
        {"marks": out, "summary": {"total_marks": grand, "percentage": pct}}
    )


@app.route("/update_marks", methods=["POST"])
def update_marks():
    if g.role not in ("admin", "teacher"):
        return jsonify({"success": False, "error": "forbidden"}), 403
    data = request.get_json(silent=True) or {}
    return _save_marks_json(data)


def _clamp_internal_mark(v):
    try:
        n = int(v)
    except (TypeError, ValueError):
        n = 0
    return max(0, min(40, n))


def _save_marks_json(data):
    sid = (data.get("student_id") or "").strip()
    try:
        sub_id = int(data.get("subject_id"))
    except (TypeError, ValueError):
        return jsonify({"success": False, "error": "missing fields"}), 400
    m1 = _clamp_internal_mark(data.get("marks1", data.get("internal_exam_1", 0)))
    m2 = _clamp_internal_mark(data.get("marks2", data.get("internal_exam_2", 0)))
    m3 = _clamp_internal_mark(data.get("marks3", data.get("internal_exam_3", 0)))
    if not sid or not sub_id:
        return jsonify({"success": False, "error": "missing fields"}), 400

    # Security check: if teacher, verify subject is assigned
    if g.role == "teacher":
        teacher_id = g.user_id
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "SELECT 1 FROM teacher_subjects WHERE teacher_id = %s AND subject_id = %s",
            (teacher_id, sub_id)
        )
        if not cur.fetchone():
            cur.close()
            conn.close()
            return jsonify({"success": False, "error": "not authorized for this subject"}), 403
        cur.close()
        conn.close()

    conn = get_db()
    cur = conn.cursor(buffered=True)
    cur.execute(
        """
        INSERT INTO marks (student_id, subject_id, internal_exam_1, internal_exam_2, internal_exam_3)
        VALUES (%s,%s,%s,%s,%s)
        ON DUPLICATE KEY UPDATE
        internal_exam_1=%s, internal_exam_2=%s, internal_exam_3=%s
        """,
        (sid, sub_id, m1, m2, m3, m1, m2, m3),
    )
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"success": True})


@app.route("/teacher_subjects/<teacher_id>")
def teacher_subjects(teacher_id):
    if g.role not in ("admin", "teacher", "student"):
        return jsonify({"subjects": []})
    if g.role == "teacher" and g.user_id != teacher_id:
        return jsonify({"subjects": []})

    conn = get_db()
    cur = conn.cursor(buffered=True, dictionary=True)
    cur.execute(
        """
        SELECT s.id, s.subject_name
        FROM teacher_subjects ts
        JOIN subjects s ON ts.subject_id = s.id
        WHERE ts.teacher_id=%s
        ORDER BY s.subject_name
        """,
        (teacher_id,),
    )
    subs = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify({"subjects": subs})


@app.route("/get_students_for_subject/<int:subject_id>")
def get_students_for_subject(subject_id):
    conn = get_db()
    cur = conn.cursor(buffered=True, dictionary=True)
    cur.execute(
        """
        SELECT s.student_id, s.name
        FROM students s
        JOIN subjects sub ON s.branch_id = sub.branch_id AND s.semester_id = sub.semester_id
        WHERE sub.id=%s
        ORDER BY s.student_id
        """,
        (subject_id,),
    )
    students = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify({"students": students})


@app.route("/get_subjects/<branch>/<semester>")
def get_subjects_branch_semester(branch, semester):
    """README API: subjects for branch + semester (1–4 or 'Semester 1')."""
    sem_no = parse_semester_choice(semester)
    conn = get_db()
    cur = conn.cursor(buffered=True, dictionary=True)
    cur.execute(
        """
        SELECT s.id, s.subject_name, s.subject_name AS name
        FROM subjects s
        INNER JOIN branches b ON s.branch_id = b.id
        INNER JOIN semesters sem ON s.semester_id = sem.id
        WHERE b.name = %s AND sem.sem_no = %s
        ORDER BY s.subject_name
        """,
        (branch, sem_no),
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(rows)





@app.route("/add_marks", methods=["GET", "POST"])
def add_marks():
    if request.method == "GET":
        redir = require_roles("teacher", "admin")
        if redir:
            return redir
        teacher_id = request.args.get('as_teacher') or g.user_id
        conn = get_db()
        cur = conn.cursor(dictionary=True)
        cur.execute(
            """
            SELECT s.id, s.subject_name
            FROM subjects s
            JOIN teacher_subjects ts ON s.id = ts.subject_id
            WHERE ts.teacher_id = %s
            ORDER BY s.subject_name
            """,
            (teacher_id,)
        )
        subjects = cur.fetchall()
        cur.close()
        conn.close()
        return render_template("add_marks.html", subjects=subjects)

    if g.role not in ("teacher", "admin"):
        return jsonify({"success": False, "error": "forbidden"}), 403
    data = request.get_json(silent=True) or {}
    if "internal_exam_1" in data and "marks1" not in data:
        data["marks1"] = data.get("internal_exam_1", 0)
        data["marks2"] = data.get("internal_exam_2", 0)
        data["marks3"] = data.get("internal_exam_3", 0)
    return _save_marks_json(data)


@app.route("/update/<student_id>", methods=["GET", "POST"])
def update_student_route(student_id):
    redir = require_admin()
    if redir:
        return redir

    conn = get_db()
    cur = conn.cursor(buffered=True, dictionary=True)
    cur.execute(
        """
        SELECT student_id, name, branch, semester, branch_id, semester_id,
               class_id, mobile, father_mobile, email
        FROM students WHERE student_id=%s
        """,
        (student_id,),
    )
    student = cur.fetchone()
    if not student:
        cur.close()
        conn.close()
        abort(404)

    classes = fetch_semester_classes(cur)
    cur.execute("SELECT name FROM branches ORDER BY name")
    branches = [row["name"] for row in cur.fetchall()]

    if request.method == "POST":
        branch_name = request.form.get("branch", student["branch"])
        sem_no = parse_semester_choice(request.form.get("semester", student["semester"]))
        bid = branch_id_by_name(cur, branch_name)
        sid_sem = semester_id_by_num(cur, sem_no)

        if bid is None or sid_sem is None:
            flash("Invalid branch or semester selected.", "error")
            cur.close()
            conn.close()
            return render_template(
                "update_student.html",
                student=student,
                classes=classes,
                branches=branches,
            )

        cur.execute(
            """
            UPDATE students SET name=%s, branch=%s, semester=%s,
                                 branch_id=%s, semester_id=%s,
                                 class_id=%s, mobile=%s, father_mobile=%s, email=%s
            WHERE student_id=%s
            """,
            (
                request.form.get("name", student["name"]).strip(),
                branch_name,
                sem_no,
                bid,
                sid_sem,
                request.form.get("class_id") or student.get("class_id"),
                request.form.get("mobile", student.get("mobile")),
                request.form.get("father_mobile", student.get("father_mobile")),
                request.form.get("email", student.get("email")),
                student_id,
            ),
        )
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for("students"))

    cur.close()
    conn.close()
    return render_template(
        "update_student.html",
        student=student,
        classes=classes,
        branches=branches,
    )


@app.route("/delete/<student_id>")
def delete_student(student_id):
    redir = require_admin()
    if redir:
        return redir
    conn = get_db()
    cur = conn.cursor(buffered=True)
    cur.execute("DELETE FROM marks WHERE student_id=%s", (student_id,))
    cur.execute("DELETE FROM students WHERE student_id=%s", (student_id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for("students"))


@app.route("/upgrade_semester_search", methods=["GET", "POST"])
def upgrade_semester_search():
    redir = require_roles("admin", "teacher")
    if redir:
        return redir

    students = []
    search_query = ""
    
    if request.method == "POST":
        search_query = request.form.get("student_search", "").strip()
        if search_query:
            conn = get_db()
            cur = conn.cursor(buffered=True, dictionary=True)
            cur.execute(
                "SELECT student_id, name, branch, semester FROM students WHERE student_id LIKE %s OR name LIKE %s ORDER BY student_id LIMIT 20",
                (f"%{search_query}%", f"%{search_query}%")
            )
            students = cur.fetchall()
            cur.close()
            conn.close()
            if not students:
                flash("No students found. Please enter a valid Student ID or Name.", "info")

    return render_template("upgrade_semester_search.html", students=students, search_query=search_query)


@app.route("/upgrade_semester/<student_id>", methods=["GET", "POST"])
def upgrade_semester(student_id):
    redir = require_roles("admin", "teacher")
    if redir:
        return redir

    conn = get_db()
    cur = conn.cursor(buffered=True, dictionary=True)
    cur.execute("SELECT * FROM students WHERE student_id=%s", (student_id,))
    student = cur.fetchone()
    if not student:
        cur.close()
        conn.close()
        abort(404)

    if request.method == "POST":
        new_sem = int(request.form.get("new_semester", student.get("semester", 1)))
        if new_sem > 0 and new_sem <= 4:
            sid_sem = semester_id_by_num(cur, new_sem)
            cur.execute(
                "UPDATE students SET semester=%s, semester_id=%s WHERE student_id=%s",
                (new_sem, sid_sem, student_id),
            )
            sync_student_subjects(
                cur, student_id, student.get("branch_id"), sid_sem
            )
            conn.commit()
            cur.close()
            conn.close()
            flash(f"✅ {student['name']} upgraded to Semester {new_sem}", "success")
            return redirect(url_for("students"))

    cur.close()
    conn.close()
    current_sem_val = student.get("semester", 1)
    try:
        current_sem_val = int(current_sem_val) if current_sem_val else 1
    except (ValueError, TypeError):
        current_sem_val = 1
    return render_template(
        "upgrade_semester.html", student=student, current_sem=current_sem_val
    )


@app.route("/update_teacher/<teacher_id>", methods=["GET", "POST"])
def update_teacher(teacher_id):
    redir = require_admin()
    if redir:
        return redir

    conn = get_db()
    cur = conn.cursor(buffered=True, dictionary=True)
    cur.execute("SELECT * FROM teachers WHERE teacher_id=%s", (teacher_id,))
    teacher = cur.fetchone()
    if not teacher:
        cur.close()
        conn.close()
        abort(404)

    cur.execute(
        "SELECT subject_id FROM teacher_subjects WHERE teacher_id=%s",
        (teacher_id,),
    )
    selected_subject_ids = [row["subject_id"] for row in cur.fetchall()]

    branch_id = None
    if teacher.get("branch"):
        branch_id = branch_id_by_name(cur, teacher["branch"])

    available_subjects = []
    if branch_id:
        cur.execute(
            "SELECT s.id, s.subject_name, sem.sem_no AS semester "
            "FROM subjects s "
            "JOIN semesters sem ON s.semester_id = sem.id "
            "WHERE s.branch_id=%s "
            "ORDER BY sem.sem_no, s.subject_name",
            (branch_id,),
        )
        available_subjects = cur.fetchall()

    if request.method == "POST":
        pw = request.form.get("password", "").strip()
        photo = save_upload(request.files.get("photo"), "tch")
        gender = request.form.get("gender", teacher.get("gender"))

        selected_ids = []
        for sub in request.form.getlist("subjects"):
            try:
                selected_ids.append(int(sub))
            except (TypeError, ValueError):
                continue
        subject_label = ",".join(str(sub_id) for sub_id in selected_ids)

        cur.execute(
            """
            UPDATE teachers SET name=%s, gender=%s, dob=%s, branch=%s, subjects=%s, phone=%s
            WHERE teacher_id=%s
            """,
            (
                request.form.get("name"),
                gender,
                request.form.get("dob"),
                request.form.get("branch"),
                subject_label,
                request.form.get("phone"),
                teacher_id,
            ),
        )
        cur.execute("DELETE FROM teacher_subjects WHERE teacher_id=%s", (teacher_id,))
        for sub_id in selected_ids:
            cur.execute(
                "INSERT IGNORE INTO teacher_subjects (teacher_id, subject_id) VALUES (%s,%s)",
                (teacher_id, sub_id),
            )
        if pw:
            cur.execute(
                "UPDATE teachers SET password=%s WHERE teacher_id=%s",
                (hash_pw(pw), teacher_id),
            )
        if photo:
            cur.execute(
                "UPDATE teachers SET photo=%s WHERE teacher_id=%s", (photo, teacher_id)
            )
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for("teacher_profile", teacher_id=teacher_id))

    cur.close()
    conn.close()
    return render_template(
        "update_teacher.html",
        teacher=teacher,
        available_subjects=available_subjects,
        selected_subject_ids=selected_subject_ids,
    )


@app.route("/delete_teacher/<teacher_id>")
def delete_teacher(teacher_id):
    redir = require_admin()
    if redir:
        return redir
    conn = get_db()
    cur = conn.cursor(buffered=True)
    cur.execute("DELETE FROM teacher_subjects WHERE teacher_id=%s", (teacher_id,))
    cur.execute("DELETE FROM teachers WHERE teacher_id=%s", (teacher_id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for("teachers"))


def _pdf_student_report(student_id):
    conn = get_db()
    cur = conn.cursor(buffered=True, dictionary=True)
    cur.execute(
        "SELECT s.*, c.class_name FROM students s LEFT JOIN classes c ON s.class_id = c.id WHERE s.student_id=%s",
        (student_id,),
    )
    stu = cur.fetchone()
    cur.execute(
        """
        SELECT s.subject_name, COALESCE(m.internal_exam_1, 0) AS internal_exam_1,
               COALESCE(m.internal_exam_2, 0) AS internal_exam_2,
               COALESCE(m.internal_exam_3, 0) AS internal_exam_3
        FROM subjects s
        LEFT JOIN marks m ON m.subject_id = s.id AND m.student_id = %s
        WHERE s.branch_id = %s AND s.semester_id = %s
        ORDER BY s.subject_name
        """,
        (student_id, stu.get("branch_id"), stu.get("semester_id")),
    )
    mk = cur.fetchall()
    cur.close()
    conn.close()

    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    y = 760
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, "Student Report")
    y -= 28
    c.setFont("Helvetica", 11)
    if stu:
        lines = [
            f"ID: {stu.get('student_id','')}",
            f"Name: {stu.get('name','')}",
            f"Branch: {stu.get('branch','')}",
            f"Semester: {stu.get('semester','')}",
            f"Class: {stu.get('class_name','')}",
            f"Gender: {stu.get('gender','')}",
            f"DOB: {stu.get('dob','')}",
            f"Mobile: {stu.get('mobile','')}",
            f"Father Mobile: {stu.get('father_mobile','')}",
            f"Email: {stu.get('email','')}",
        ]
        for line in lines:
            c.drawString(50, y, line)
            y -= 14
            if y < 80:
                c.showPage()
                y = 760
    y -= 10
    c.drawString(50, y, "Subjects & Marks")
    y -= 20

    total_marks = 0
    subject_count = 0
    for r in mk:
        if y < 90:
            c.showPage()
            y = 760
        m1 = int(r.get("internal_exam_1", 0))
        m2 = int(r.get("internal_exam_2", 0))
        m3 = int(r.get("internal_exam_3", 0))
        subj_total = m1 + m2 + m3
        total_marks += subj_total
        subject_count += 1
        line = f"{r['subject_name']}: I1={m1}  I2={m2}  I3={m3}  Total={subj_total}"
        c.drawString(50, y, line)
        y -= 14

    max_total = subject_count * 75
    percentage = round((total_marks / max_total) * 100, 2) if max_total else 0
    y -= 16
    if y < 90:
        c.showPage()
        y = 760
    c.drawString(50, y, f"Total Marks: {total_marks}")
    y -= 14
    c.drawString(50, y, f"Percentage: {percentage}%")
    y -= 14
    c.save()
    buf.seek(0)
    return buf


@app.route("/report/<student_id>")
@app.route("/report_pdf/<student_id>")
def report_pdf(student_id):
    if not g.role:
        return redirect(url_for("login"))
    if g.role == "student" and g.user_id != student_id:
        abort(403)
    buf = _pdf_student_report(student_id)
    return send_file(
        buf,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"report_{student_id}.pdf",
    )


@app.route("/teacher_report/<teacher_id>")
def teacher_report(teacher_id):
    if not g.role:
        return redirect(url_for("login"))
    if g.role == "teacher" and g.user_id != teacher_id:
        abort(403)

    conn = get_db()
    cur = conn.cursor(buffered=True, dictionary=True)
    cur.execute("SELECT * FROM teachers WHERE teacher_id=%s", (teacher_id,))
    t = cur.fetchone()
    cur.close()
    conn.close()

    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    y = 750
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Teacher Profile")
    y -= 24
    c.setFont("Helvetica", 11)
    if t:
        for label, key in [
            ("ID", "teacher_id"),
            ("Name", "name"),
            ("Branch", "branch"),
            ("Phone", "phone"),
            ("Subjects", "subjects"),
        ]:
            c.drawString(50, y, f"{label}: {t.get(key) or ''}")
            y -= 16
    c.save()
    buf.seek(0)
    return send_file(
        buf,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"teacher_{teacher_id}.pdf",
    )


@app.route("/announcements", methods=["GET", "POST"])
def announcements():
    if not g.role:
        return redirect(url_for("login"))

    conn = get_db()
    cur = conn.cursor(buffered=True, dictionary=True)

    if request.method == "POST" and g.role in ("admin", "teacher"):
        msg = request.form.get("message", "")
        aud = request.form.get("target_audience", "all")
        who = g.user_id or g.role
        fns = None
        if request.files.get("file") and request.files["file"].filename:
            fns = save_upload(request.files["file"], "ann")
        cur.execute(
            """
            INSERT INTO announcements (message, file, target_audience, created_by)
            VALUES (%s,%s,%s,%s)
            """,
            (msg, fns, aud, str(who)),
        )
        conn.commit()

    cur.execute(
        "SELECT id, message, file, target_audience, created_by FROM announcements ORDER BY id DESC"
    )
    raw = cur.fetchall()
    cur.close()
    conn.close()

    data = []
    for r in raw:
        aud = (r.get("target_audience") or "all").lower()
        if g.role == "admin":
            data.append(r)
            continue
        if aud == "all":
            data.append(r)
            continue
        if g.role == "teacher" and aud in ("teachers", "teacher"):
            data.append(r)
            continue
        if g.role == "student" and aud in ("students", "student"):
            data.append(r)
            continue

    return render_template("announcements.html", data=data)


@app.route("/edit_announcement/<int:aid>", methods=["GET", "POST"])
def edit_announcement(aid):
    redir = require_admin()
    if redir:
        return redir

    conn = get_db()
    cur = conn.cursor(buffered=True, dictionary=True)
    cur.execute("SELECT id, message FROM announcements WHERE id=%s", (aid,))
    a = cur.fetchone()
    if not a:
        cur.close()
        conn.close()
        abort(404)

    if request.method == "POST":
        cur.execute(
            "UPDATE announcements SET message=%s WHERE id=%s",
            (request.form.get("message"), aid),
        )
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for("announcements"))

    cur.close()
    conn.close()
    return render_template("edit_announcement.html", a=a)


@app.route("/delete_announcement/<int:aid>")
def delete_announcement(aid):
    redir = require_admin()
    if redir:
        return redir
    conn = get_db()
    cur = conn.cursor(buffered=True)
    cur.execute("DELETE FROM announcements WHERE id=%s", (aid,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for("announcements"))


@app.route("/analytics")
def analytics():
    if not g.role:
        return redirect(url_for("login"))

    conn = get_db()
    cur = conn.cursor(buffered=True, dictionary=True)
    classes = fetch_semester_classes(cur)

    selected_class_id = request.args.get("class_id", type=int)
    selected_class_name = None
    if selected_class_id:
        for cls in classes:
            if cls["id"] == selected_class_id:
                selected_class_name = cls["class_name"]
                break

    filter_clause = ""
    params = []
    teacher = None
    teacher_stats = None
    if g.role == "teacher":
        cur.execute(
            "SELECT t.*, "
            "(SELECT GROUP_CONCAT(s.subject_name ORDER BY s.subject_name) "
            " FROM teacher_subjects ts JOIN subjects s ON ts.subject_id = s.id "
            " WHERE ts.teacher_id = t.teacher_id) AS subjects "
            "FROM teachers t WHERE t.teacher_id=%s",
            (g.user_id,),
        )
        teacher = cur.fetchone()
        branch_filter = "WHERE s.branch=%s"
        params = [teacher.get("branch") if teacher else ""]
        filter_clause = branch_filter if teacher else ""

    elif g.role == "admin" and selected_class_id:
        filter_clause = "WHERE s.class_id=%s"
        params = [selected_class_id]

    cur.execute(
        "SELECT s.name, COALESCE(ROUND(SUM(m.internal_exam_1 + m.internal_exam_2 + m.internal_exam_3) / 120 * 100, 2), 0) AS pct, "
        "COALESCE(c.class_name, CONCAT(s.branch, ' Sem ', s.semester)) AS class_name "
        "FROM students s "
        "LEFT JOIN classes c ON s.class_id=c.id "
        "LEFT JOIN marks m ON m.student_id = s.student_id "
        + filter_clause
        + " GROUP BY s.student_id, s.name, c.class_name, s.branch, s.semester ORDER BY pct DESC LIMIT 1",
        params,
    )
    top = cur.fetchone()
    topper = top["name"] if top else "N/A"

    cur.execute(
        "SELECT ROUND(AVG(pct),2) AS a FROM ("
        "SELECT COALESCE(ROUND(SUM(m.internal_exam_1 + m.internal_exam_2 + m.internal_exam_3) / 120 * 100, 2), 0) AS pct "
        "FROM students s "
        "LEFT JOIN marks m ON m.student_id = s.student_id "
        + filter_clause
        + " GROUP BY s.student_id) AS stats",
        params,
    )
    avg = float((cur.fetchone() or {}).get("a") or 0)

    cur.execute(
        "SELECT s.student_id, s.name, COALESCE(ROUND(SUM(m.internal_exam_1 + m.internal_exam_2 + m.internal_exam_3) / 120 * 100, 2), 0) AS pct, "
        "COALESCE(c.class_name, CONCAT(s.branch, ' Sem ', s.semester)) AS class_name "
        "FROM students s LEFT JOIN classes c ON s.class_id=c.id "
        "LEFT JOIN marks m ON m.student_id = s.student_id "
        + filter_clause
        + " GROUP BY s.student_id, s.name, c.class_name, s.branch, s.semester",
        params,
    )
    studs = cur.fetchall()
    results = []
    grade_counts = {"A": 0, "B": 0, "C": 0, "D": 0, "F": 0}
    weak_students = []
    for s in studs:
        cur_pct = float(s["pct"] or 0)
        predicted = min(100.0, round(cur_pct * 1.03, 1))
        grade = (
            "A"
            if cur_pct >= 90
            else "B"
            if cur_pct >= 80
            else "C"
            if cur_pct >= 70
            else "D"
            if cur_pct >= 60
            else "F"
        )
        status = "Pass" if cur_pct >= 40 else "Fail"
        improvement = round(predicted - cur_pct, 1)
        results.append(
            {
                "name": s["name"],
                "class_name": s["class_name"],
                "current": round(cur_pct, 1),
                "predicted": predicted,
                "weak": "Lowest score subject" if status == "Fail" else "—",
                "grade": grade,
                "status": status,
                "improvement": improvement,
            }
        )
        grade_counts[grade] += 1
        if status == "Fail":
            weak_students.append({"name": s["name"], "pct": cur_pct})

    student_count = len(results)
    weak_count = len(weak_students)
    pass_rate = round((student_count - weak_count) / student_count * 100, 2) if student_count else 0
    fail_rate = round(weak_count / student_count * 100, 2) if student_count else 0

    if g.role == "teacher" and teacher:
        cur.execute(
            "SELECT DISTINCT st.student_id, st.name, st.branch, sem.sem_no "
            "FROM teacher_subjects ts "
            "JOIN subjects s ON ts.subject_id = s.id "
            "JOIN students st ON st.branch_id = s.branch_id AND st.semester_id = s.semester_id "
            "LEFT JOIN semesters sem ON st.semester_id = sem.id "
            "WHERE ts.teacher_id=%s ORDER BY st.name",
            (g.user_id,),
        )
        teacher_students = cur.fetchall()
        teacher_stats = {
            "teacher": teacher,
            "students": teacher_students,
            "avg": avg,
            "pass_rate": pass_rate,
            "fail_rate": fail_rate,
            "student_count": len(teacher_students),
            "subjects": teacher.get("subjects"),
            "grade_counts": grade_counts,
        }
    else:
        teacher_stats = None

    cur.close()
    conn.close()
    return render_template(
        "analytics.html",
        topper=topper,
        avg=round(avg, 2),
        results=results,
        classes=classes,
        selected_class_id=selected_class_id,
        selected_class_name=selected_class_name,
        teacher_stats=teacher_stats,
        student_count=student_count,
        weak_count=weak_count,
        pass_rate=pass_rate,
        fail_rate=fail_rate,
        grade_counts=grade_counts,
    )


@app.route("/assistant", methods=["GET", "POST"])
def assistant():
    if not g.role:
        return redirect(url_for("login"))

    answer = None
    q = request.args.get("q")
    conn = get_db()
    cur = conn.cursor(buffered=True, dictionary=True)

    if q == "topper":
        cur.execute(
            "SELECT name, percentage FROM students ORDER BY percentage DESC LIMIT 1"
        )
        r = cur.fetchone()
        answer = f"Topper: {r['name']} ({r['percentage']}%)" if r else "No data."
    elif q == "average":
        cur.execute("SELECT AVG(percentage) AS a FROM students")
        r = cur.fetchone()
        answer = f"Class average: {round(float(r['a'] or 0), 2)}%"
    elif q == "weak":
        cur.execute(
            "SELECT name, percentage FROM students WHERE percentage < 60 ORDER BY percentage"
        )
        rows = cur.fetchall()
        answer = (
            ", ".join(f"{x['name']} ({x['percentage']}%)" for x in rows)
            if rows
            else "No weak students found."
        )

    if request.method == "POST":
        question = (request.form.get("question") or "").lower()
        if "topper" in question:
            cur.execute(
                "SELECT name, percentage FROM students ORDER BY percentage DESC LIMIT 1"
            )
            r = cur.fetchone()
            answer = f"Topper: {r['name']} ({r['percentage']}%)" if r else "No data."
        elif "average" in question or "mean" in question:
            cur.execute("SELECT AVG(percentage) AS a FROM students")
            r = cur.fetchone()
            answer = f"Average percentage: {round(float(r['a'] or 0), 2)}%"
        else:
            answer = "Try asking about topper, average, or weak students."

    cur.close()
    conn.close()
    return render_template("assistant.html", answer=answer)


def _otp_send(phone, purpose):
    code = f"{random.randint(100000, 999999)}"
    session["otp_phone"] = phone
    session["otp_code"] = code
    session["otp_purpose"] = purpose
    session["otp_verified"] = False
    app.logger.info("OTP for %s: %s", phone, code)


@app.route("/student_forgot_password")
@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        phone = re.sub(r"\D", "", request.form.get("phone", ""))
        conn = get_db()
        cur = conn.cursor(buffered=True, dictionary=True)
        cur.execute("SELECT student_id FROM students WHERE mobile=%s", (phone,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if not row:
            flash("Phone number not registered", "error")
            return render_template("forgot_password.html")
        session["reset_student_id"] = row["student_id"]
        _otp_send(phone, "student")
        flash("OTP sent (check server log for demo OTP)", "success")
        return redirect(url_for("verify_otp"))
    return render_template("forgot_password.html")


@app.route("/verify_otp", methods=["GET", "POST"])
def verify_otp():
    if request.method == "GET" and (
        not session.get("otp_code") or session.get("otp_purpose") != "student"
    ):
        return redirect(url_for("forgot_password"))
    if request.method == "POST":
        if request.form.get("otp") == session.get("otp_code"):
            session["otp_verified"] = True
            return redirect(url_for("reset_password"))
        flash("Invalid OTP", "error")
    return render_template("otp_verify.html")


@app.route("/reset_password", methods=["GET", "POST"])
def reset_password():
    if not session.get("otp_verified"):
        return redirect(url_for("forgot_password"))
    if request.method == "POST":
        p1 = request.form.get("new_password", "")
        p2 = request.form.get("confirm_password", "")
        if p1 != p2 or len(p1) < 6:
            flash("Passwords must match (min 6 chars)", "error")
            return render_template("reset_password.html")
        sid = session.get("reset_student_id")
        if not sid:
            flash("Session expired", "error")
            return redirect(url_for("forgot_password"))
        conn = get_db()
        cur = conn.cursor(buffered=True)
        cur.execute(
            "UPDATE students SET password=%s WHERE student_id=%s", (hash_pw(p1), sid)
        )
        conn.commit()
        cur.close()
        conn.close()
        session.pop("otp_verified", None)
        session.pop("otp_code", None)
        session.pop("reset_student_id", None)
        flash("Password updated. Please login.", "success")
        return redirect(url_for("login"))
    return render_template("reset_password.html")


@app.route("/teacher_forgot_password", methods=["GET", "POST"])
def teacher_forgot_password():
    if request.method == "POST":
        phone = re.sub(r"\D", "", request.form.get("phone", ""))
        conn = get_db()
        cur = conn.cursor(buffered=True, dictionary=True)
        cur.execute("SELECT teacher_id FROM teachers WHERE phone=%s", (phone,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if not row:
            flash("Phone number not registered", "error")
            return render_template("teacher_forgot_password.html")
        session["reset_teacher_id"] = row["teacher_id"]
        _otp_send(phone, "teacher")
        flash("OTP sent (check server log for demo OTP)", "success")
        return redirect(url_for("teacher_verify_otp"))
    return render_template("teacher_forgot_password.html")


@app.route("/teacher_verify_otp", methods=["GET", "POST"])
def teacher_verify_otp():
    if request.method == "GET" and (
        not session.get("otp_code") or session.get("otp_purpose") != "teacher"
    ):
        return redirect(url_for("teacher_forgot_password"))
    if request.method == "POST":
        if request.form.get("otp") == session.get("otp_code"):
            session["otp_verified_teacher"] = True
            return redirect(url_for("teacher_reset_password"))
        flash("Invalid OTP", "error")
    return render_template("teacher_verify_otp.html")


@app.route("/teacher_reset_password", methods=["GET", "POST"])
def teacher_reset_password():
    if not session.get("otp_verified_teacher"):
        return redirect(url_for("teacher_forgot_password"))
    if request.method == "POST":
        p1 = request.form.get("new_password", "")
        p2 = request.form.get("confirm_password", "")
        if p1 != p2 or len(p1) < 6:
            flash("Passwords must match (min 6 chars)", "error")
            return render_template("teacher_reset_password.html")
        tid = session.get("reset_teacher_id")
        if not tid:
            flash("Session expired", "error")
            return redirect(url_for("teacher_forgot_password"))
        conn = get_db()
        cur = conn.cursor(buffered=True)
        cur.execute(
            "UPDATE teachers SET password=%s WHERE teacher_id=%s", (hash_pw(p1), tid)
        )
        conn.commit()
        cur.close()
        conn.close()
        session.pop("otp_verified_teacher", None)
        session.pop("otp_code", None)
        session.pop("reset_teacher_id", None)
        flash("Password updated. Please login.", "success")
        return redirect(url_for("login"))
    return render_template("teacher_reset_password.html")


@app.route("/add_student", methods=["GET", "POST"])
def add_student():
    redir = require_admin()
    if redir:
        return redir
    error = None
    conn = get_db()
    cur = conn.cursor(buffered=True)
    classes = fetch_semester_classes(cur)
    if request.method == "POST":
        roll = request.form.get("rollno", "").strip()
        name = request.form.get("name", "").strip()
        try:
            cid = int(request.form.get("class_id"))
        except (TypeError, ValueError):
            cid = None
        eng = int(request.form.get("english", 0) or 0)
        math = int(request.form.get("mathematics", 0) or 0)
        phy = int(request.form.get("physics", 0) or 0)
        chem = int(request.form.get("chemistry", 0) or 0)
        cs = int(request.form.get("computer_science", 0) or 0)
        total = eng + math + phy + chem + cs
        pct = round((total / 500.0) * 100, 2) if total else 0.0
        cur.execute("SELECT class_name FROM classes WHERE id=%s", (cid,))
        crow = cur.fetchone()
        if not roll or not name or not crow:
            error = "Fill all required fields."
        else:
            bn, sn = class_label_to_branch_semester(crow[0])
            bid = branch_id_by_name(cur, bn)
            sid_sem = semester_id_by_num(cur, sn)
            try:
                cur.execute(
                    """
                    INSERT INTO students (
                        student_id, name, password, branch, semester, branch_id, semester_id,
                        english, mathematics, physics, chemistry, computer_science, total, percentage
                    ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    """,
                    (
                        roll,
                        name,
                        hash_pw("changeme"),
                        bn,
                        sn,
                        bid,
                        sid_sem,
                        eng,
                        math,
                        phy,
                        chem,
                        cs,
                        total,
                        pct,
                    ),
                )
                sync_student_subjects(cur, roll, bid, sid_sem)
                conn.commit()
                cur.close()
                conn.close()
                return redirect(url_for("students"))
            except mysql_errors.IntegrityError:
                conn.rollback()
                error = "Roll number / student ID already exists."
            except mysql_errors.Error as e:
                conn.rollback()
                error = str(e)
    cur.close()
    conn.close()
    return render_template("add_student.html", classes=classes, error=error)


@app.route("/view_students")
def view_students():
    redir = require_admin()
    if redir:
        return redir
    return redirect(url_for("students"))


if __name__ == "__main__":
    app.run(debug=True)
