from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)

app.secret_key = "employee_management_secret_key"

DATABASE = "users.db"


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# =========================================================
# CREATE DATABASE
# =========================================================

def create_database():

    conn = get_db()
    cursor = conn.cursor()

    # -----------------------------------------------------
    # USERS TABLE
    # -----------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fullname TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # -----------------------------------------------------
    # EMPLOYEES TABLE
    # -----------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fullname TEXT NOT NULL,
            username TEXT UNIQUE,
            password TEXT,
            email TEXT,
            phone TEXT,
            department TEXT,
            salary TEXT,
            joining_date TEXT,
            address TEXT
        )
    """)

    conn.commit()
    conn.close()


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    return render_template("home.html")


# =========================================================
# REGISTER
# =========================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    error = ""

    if request.method == "POST":

        fullname = request.form["fullname"]
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        cursor = conn.cursor()

        try:

            # Save user in users table
            cursor.execute("""
                INSERT INTO users
                (fullname, username, password)
                VALUES (?, ?, ?)
            """, (
                fullname,
                username,
                password
            ))

            # Automatically create employee record
            cursor.execute("""
                INSERT INTO employees
                (fullname, username, password)
                VALUES (?, ?, ?)
            """, (
                fullname,
                username,
                password
            ))

            conn.commit()

        except sqlite3.IntegrityError:

            conn.close()

            return render_template(
                "registerdemo.html",
                error="Username already exists!"
            )

        conn.close()

        return redirect("/login")

    return render_template(
        "registerdemo.html",
        error=error
    )


# =========================================================
# LOGIN
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    error = ""

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT *
            FROM users
            WHERE username = ?
            AND password = ?
        """, (
            username,
            password
        ))

        user = cursor.fetchone()

        conn.close()

        if user:

            # Store login information
            session["fullname"] = user["fullname"]
            session["username"] = user["username"]

            return redirect("/")

        else:

            error = "Username or password incorrect!"

    return render_template(
        "login.html",
        error=error
    )
# =========================================
# ADD EMPLOYEE PAGE
# =========================================

@app.route("/add-employee", methods=["GET"])
def add_employee_page():

    return render_template("add-employee.html")


# =========================================
# ADD EMPLOYEE
# =========================================

@app.route("/add-employee", methods=["POST"])
def add_employee():

    name = request.form.get("name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    department = request.form.get("department")
    salary = request.form.get("salary")
    joining_date = request.form.get("joining_date")
    address = request.form.get("address")

    print("=================================")
    print("ADDING EMPLOYEE")
    print("Name:", name)
    print("Email:", email)
    print("Phone:", phone)
    print("Department:", department)
    print("Salary:", salary)
    print("Joining Date:", joining_date)
    print("Address:", address)
    print("=================================")

    connection = sqlite3.connect("users.db")

    cursor = connection.cursor()

    try:

        cursor.execute("""
            INSERT INTO employees
            (
                name,
                email,
                phone,
                department,
                salary,
                joining_date,
                address
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            name,
            email,
            phone,
            department,
            salary,
            joining_date,
            address
        ))

        connection.commit()

        print("Employee inserted successfully!")
        print("New Employee ID:", cursor.lastrowid)

    except sqlite3.Error as error:

        connection.rollback()

        print("Database Error:", error)

        connection.close()

        return f"""
        <h2>Error adding employee</h2>

        <p>{error}</p>

        <br>

        <a href="/add-employee">
            Go Back
        </a>
        """

    connection.close()

    return redirect("/employees")


# =========================================
# EMPLOYEES LIST
# =========================================

@app.route("/employees")
def employees():

    connection = get_database_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM employees
        ORDER BY id DESC
    """)

    employees = cursor.fetchall()

    connection.close()

    return render_template(
        "employees.html",
        employees=employees
    )

# =========================================================
# EMPLOYEE LIST
# =========================================================

@app.route("/employee")
def employee():

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM employees
        ORDER BY id DESC
    """)

    employees = cursor.fetchall()

    conn.close()

    return render_template(
        "employee.html",
        employees=employees
    )


# =========================================================
# SEARCH EMPLOYEE
# =========================================================

@app.route("/search")
def search():

    keyword = request.args.get("keyword", "").strip()

    employees = []

    if keyword:

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT *
            FROM employees
            WHERE fullname LIKE ?
               OR username LIKE ?
               OR email LIKE ?
               OR department LIKE ?
        """, (
            "%" + keyword + "%",
            "%" + keyword + "%",
            "%" + keyword + "%",
            "%" + keyword + "%"
        ))

        employees = cursor.fetchall()

        conn.close()

    return render_template(
        "search.html",
        employees=employees,
        keyword=keyword
    )


# =========================================================
# DELETE EMPLOYEE
# =========================================================

@app.route("/delete_employee/<int:id>")
def delete_employee(id):

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM employees
        WHERE id = ?
    """, (id,))

    conn.commit()
    conn.close()

    return redirect("/employee")


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    create_database()

    app.run(debug=True)

    # =========================================
# EDIT EMPLOYEE - DISPLAY FORM
# =========================================

@app.route("/edit-employee/<int:id>")
def edit_employee_page(id):

    connection = get_database_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM employees
        WHERE id = ?
    """, (id,))

    employee = cursor.fetchone()

    connection.close()

    if employee is None:

        return """
        <h2>Employee not found!</h2>

        <br>

        <a href="/employees">
            Back to Employees
        </a>
        """

    return render_template(
        "edit-employee.html",
        employee=employee
    )
    

