import streamlit as st
import mysql.connector
from mysql.connector import Error
import pandas as pd
# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="CollegeDB Dashboard",
    page_icon="🎓",
    layout="wide"
)

# ---------------- DATABASE CONNECTION ----------------
def db_connect():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",
            database="collegedb"
        )
    except Error as e:
        st.error(e)
        return None

# ---------------- FIXED COURSES ----------------
FIXED_COURSES = [
    "AIPA",
    "COMPUTER APPLICATION",
    "BCA",
    "MCA",
    "BSC",
    "MSC"
]

# ---------------- INITIALIZE DATABASE ----------------
def initialize_database():
    con = db_connect()
    cur = con.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS students(
            student_id INT AUTO_INCREMENT PRIMARY KEY,
            student_name VARCHAR(100)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS courses(
            course_id INT AUTO_INCREMENT PRIMARY KEY,
            course_name VARCHAR(100) UNIQUE
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS enrollments(
            enrollment_id INT AUTO_INCREMENT PRIMARY KEY,
            student_id INT,
            course_id INT,
            marks INT,
            backlog VARCHAR(5),
            FOREIGN KEY(student_id) REFERENCES students(student_id) ON DELETE CASCADE,
            FOREIGN KEY(course_id) REFERENCES courses(course_id) ON DELETE CASCADE
        )
    """)

    con.commit()

    cur.execute("SELECT course_name FROM courses")
    existing = [c[0] for c in cur.fetchall()]

    for course in FIXED_COURSES:
        if course not in existing:
            cur.execute(
                "INSERT INTO courses(course_name) VALUES(%s)",
                (course,)
            )

    con.commit()
    con.close()

initialize_database()

# ---------------- HOME PAGE (COLORFUL, NO HTML/CSS) ----------------
def home_page():
    st.title("🎓 CollegeDB Student Performance Dashboard")
    st.caption("Python • Streamlit • MySQL")

    st.success("🎉 Welcome to the CollegeDB System")
    st.info("This system manages students, courses, enrollments and performance reports.")
    st.warning("👉 Use the sidebar menu to navigate the application.")

    st.divider()

    con = db_connect()
    cur = con.cursor()

    cur.execute("SELECT COUNT(*) FROM students")
    students = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(*) FROM courses
        WHERE course_name IN ('AIPA','COMPUTER APPLICATION','BCA','MCA','BSC','MSC')
    """)
    courses = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM enrollments")
    enrollments = cur.fetchone()[0]

    con.close()

    st.subheader("📊 Dashboard Overview")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.success(f"👩‍🎓 TOTAL STUDENTS\n\n{students}")

    with col2:
        st.info(f"📚 TOTAL COURSES\n\n{courses}")

    with col3:
        st.warning(f"📝 TOTAL ENROLLMENTS\n\n{enrollments}")

    st.divider()

    st.subheader("🎨 Available Courses")
    st.success("AIPA")
    st.info("COMPUTER APPLICATION")
    st.warning("BCA")
    st.success("MCA")
    st.info("BSC")
    st.warning("MSC")

    st.divider()

    st.subheader("🚀 System Status")
    st.progress(100)
    st.success("System is running successfully ✅")

# ---------------- STUDENT FUNCTIONS ----------------
def add_student(name):
    con = db_connect()
    cur = con.cursor()
    cur.execute("INSERT INTO students(student_name) VALUES(%s)", (name,))
    con.commit()
    sid = cur.lastrowid
    con.close()
    return sid

def get_students():
    con = db_connect()
    cur = con.cursor()
    cur.execute("SELECT * FROM students")
    data = cur.fetchall()
    con.close()
    return data

def delete_student(sid):
    con = db_connect()
    cur = con.cursor()

    # First delete enrollments
    cur.execute("DELETE FROM enrollments WHERE student_id=%s", (sid,))

    # Then delete student
    cur.execute("DELETE FROM students WHERE student_id=%s", (sid,))

    con.commit()
    con.close()


# ---------------- COURSE FUNCTIONS ----------------
def get_courses():
    con = db_connect()
    cur = con.cursor()
    cur.execute("""
        SELECT * FROM courses
        WHERE course_name IN ('AIPA','COMPUTER APPLICATION','BCA','MCA','BSC','MSC')
    """)
    data = cur.fetchall()
    con.close()
    return data

# ---------------- ENROLLMENT FUNCTIONS ----------------
def add_enrollment(sid, cid, marks, backlog):
    con = db_connect()
    cur = con.cursor()
    cur.execute("""
        INSERT INTO enrollments(student_id, course_id, marks, backlog)
        VALUES(%s,%s,%s,%s)
    """, (sid, cid, marks, backlog))
    con.commit()
    con.close()

def get_enrollments():
    con = db_connect()
    cur = con.cursor()
    cur.execute("""
        SELECT e.enrollment_id,
               s.student_name,
               c.course_name,
               e.marks,
               e.backlog
        FROM enrollments e
        JOIN students s ON e.student_id=s.student_id
        JOIN courses c ON e.course_id=c.course_id
    """)
    data = cur.fetchall()
    con.close()
    return data

def update_marks(eid, marks):
    con = db_connect()
    cur = con.cursor()
    cur.execute(
        "UPDATE enrollments SET marks=%s WHERE enrollment_id=%s",
        (marks, eid)
    )
    con.commit()
    con.close()
# ---------------- SIDEBAR ----------------
menu = st.sidebar.selectbox(
    "Navigation",
    [
        "Home",
        "Add Student",
        "View Records",
        "Update Marks",
        "Delete Student",
        "Reports",
        "Course-wise Enrollment Count",
        "Top Scorer"
    ]
)

# ---------------- MENU LOGIC ----------------
if menu == "Home":
    home_page()

elif menu == "Add Student":
    st.subheader("👩‍🎓Add Student")
    name = st.text_input("Student Name")
    course = st.selectbox("Course", FIXED_COURSES)
    marks = st.slider("Marks", 0, 100)
    backlog = st.radio("Backlog", ["No", "Yes"])

    if st.button("Save"):
        if name:
            sid = add_student(name)
            courses = get_courses()
            cid = next(c[0] for c in courses if c[1] == course)
            add_enrollment(sid, cid, marks, backlog)
            st.success("Student added successfully")
        else:
            st.warning("Enter student name")

elif menu == "View Records":
    st.subheader("📝Enrollment Records")
    data = get_enrollments()

    df = pd.DataFrame(
    data,
    columns=[
        "Enrollment ID",
        "Student Name",
        "Course Name",
        "Marks",
        "Backlog"
    ]
)

    st.dataframe(df, use_container_width=True)


elif menu == "Update Marks":
    st.subheader("✏️Update Marks")

    records = get_enrollments()

    if records:
        # Create placeholder
        options = ["Select"] + records

        selected = st.selectbox(
            "Select Enrollment",
            options,
            format_func=lambda x: x if x == "Select" else f"{x[1]} - {x[2]} (Marks: {x[3]})"
        )

        # Only show slider after valid selection
        if selected != "Select":
            marks = st.slider("New Marks", 0, 100)

            if st.button("Update Marks"):
                update_marks(selected[0], marks)
                st.success("Marks updated successfully")
        else:
            st.info("Please select an enrollment to update marks")

    else:
        st.warning("No enrollment records found")

elif menu == "Delete Student":
    st.subheader("❌Delete Student")

    students = get_students()

    if students:
        options = ["Select"] + students

        selected = st.selectbox(
            "Select Student",
            options,
            format_func=lambda x: x if x == "Select" else x[1]
        )

        if selected != "Select":
            if st.button("Delete Student"):
                delete_student(selected[0])
                st.success("Student deleted successfully")
        else:
            st.info("Please select a student to delete")
    else:
        st.warning("No students found")

elif menu == "Reports":
    con = db_connect()
    cur = con.cursor()
    st.subheader("⚠️Students with Backlogs")

    cur.execute("""
        SELECT s.student_name, c.course_name
        FROM enrollments e
        JOIN students s ON e.student_id=s.student_id
        JOIN courses c ON e.course_id=c.course_id
        WHERE e.backlog='Yes'
    """)
    rows = cur.fetchall()

    df = pd.DataFrame(
        rows,
    columns=[
        "Student Name",
        "Course Name"
    ]
    )

    st.dataframe(df, use_container_width=True)

    con.close()

elif menu == "Course-wise Enrollment Count":
    st.header("📚 Course-wise Enrollment Count")
    con = db_connect()
    cur = con.cursor()
    cur.execute("""
        SELECT c.course_name, COUNT(e.student_id)
        FROM courses c
        LEFT JOIN enrollments e ON c.course_id=e.course_id
        GROUP BY c.course_name
    """)
    rows = cur.fetchall()

    df = pd.DataFrame(
    rows,
    columns=[
        "Course Name",
        "Total Enrollments"
    ]
)

    st.dataframe(df, use_container_width=True)

    con.close()

elif menu == "Top Scorer":
    st.header("🏆 Top Scorer in Each Course")
    con = db_connect()
    cur = con.cursor()
    cur.execute("""
        SELECT c.course_name, s.student_name, e.marks
        FROM enrollments e
        JOIN students s ON e.student_id=s.student_id
        JOIN courses c ON e.course_id=c.course_id
        WHERE (e.course_id, e.marks) IN (
            SELECT course_id, MAX(marks)
            FROM enrollments
            GROUP BY course_id
        )
    """)
    rows = cur.fetchall()

    df = pd.DataFrame(
    rows,
    columns=[
        "Course Name",
        "Top Scorer",
        "Marks"
    ]
)

    st.dataframe(df, use_container_width=True)

    con.close()