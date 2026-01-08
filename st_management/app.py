from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change in production

DB_NAME = "student_management.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

# Initialize DB
def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            roll_no TEXT UNIQUE NOT NULL,
            age INTEGER,
            grade TEXT
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        name = request.form['name']
        roll_no = request.form['roll_no']
        age = request.form['age']
        grade = request.form['grade']

        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO students (name, roll_no, age, grade) VALUES (?, ?, ?, ?)',
                         (name, roll_no, age, grade))
            conn.commit()
            flash('Student added successfully!', 'success')
        except sqlite3.IntegrityError:
            flash('Error: Roll number already exists!', 'danger')
        finally:
            conn.close()
        return redirect(url_for('view_students'))

    return render_template('add.html')

@app.route('/view')
def view_students():
    conn = get_db_connection()
    students = conn.execute('SELECT * FROM students').fetchall()
    conn.close()
    return render_template('view.html', students=students)

@app.route('/search', methods=['GET', 'POST'])
def search_student():
    student = None
    if request.method == 'POST':
        roll_no = request.form['roll_no']
        conn = get_db_connection()
        student = conn.execute('SELECT * FROM students WHERE roll_no = ?', (roll_no,)).fetchone()
        conn.close()
        if not student:
            flash('Student not found!', 'warning')
    return render_template('search.html', student=student)

@app.route('/update/<roll_no>', methods=['GET', 'POST'])
def update_student(roll_no):
    conn = get_db_connection()
    student = conn.execute('SELECT * FROM students WHERE roll_no = ?', (roll_no,)).fetchone()

    if not student:
        conn.close()
        flash('Student not found!', 'danger')
        return redirect(url_for('view_students'))

    if request.method == 'POST':
        name = request.form['name'] or student['name']
        age = request.form['age'] or student['age']
        grade = request.form['grade'] or student['grade']

        conn.execute('UPDATE students SET name = ?, age = ?, grade = ? WHERE roll_no = ?',
                     (name, age, grade, roll_no))
        conn.commit()
        conn.close()
        flash('Student updated successfully!', 'success')
        return redirect(url_for('view_students'))

    conn.close()
    return render_template('update.html', student=student)

@app.route('/delete/<roll_no>')
def delete_student(roll_no):
    conn = get_db_connection()
    cursor = conn.execute('DELETE FROM students WHERE roll_no = ?', (roll_no,))
    conn.commit()
    if cursor.rowcount > 0:
        flash('Student deleted successfully!', 'success')
    else:
        flash('Student not found!', 'danger')
    conn.close()
    return redirect(url_for('view_students'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)