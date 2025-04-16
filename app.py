from flask import Flask, render_template, request, redirect, jsonify, Response
import sqlite3
import os
import csv
from io import StringIO

app = Flask(__name__)
DB_FILE = 'students.db'

# ✅ Create DB table if it doesn't exist
def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER NOT NULL,
                course TEXT NOT NULL
            )
        ''')
        conn.commit()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    name = request.form['name']
    age = int(request.form['age'])
    course = request.form['course']

    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("INSERT INTO students (name, age, course) VALUES (?, ?, ?)", (name, age, course))
        conn.commit()

    return redirect('/students')

@app.route('/students')
def view_students():
    search = request.args.get('search', '').strip()

    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        if search:
            c.execute("""
                SELECT id, name, age, course FROM students 
                WHERE name LIKE ? OR course LIKE ?
            """, (f'%{search}%', f'%{search}%'))
        else:
            c.execute("SELECT id, name, age, course FROM students")

        students = [dict(id=row[0], name=row[1], age=row[2], course=row[3]) for row in c.fetchall()]

    return render_template('students.html', students=students, search=search)

@app.route('/delete/<int:id>', methods=['POST'])
def delete_student(id):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("DELETE FROM students WHERE id = ?", (id,))
        conn.commit()
    return redirect('/students')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()

        if request.method == 'POST':
            name = request.form['name']
            age = int(request.form['age'])
            course = request.form['course']
            c.execute("UPDATE students SET name=?, age=?, course=? WHERE id=?", (name, age, course, id))
            conn.commit()
            return redirect('/students')

        c.execute("SELECT name, age, course FROM students WHERE id=?", (id,))
        row = c.fetchone()
        if row:
            student = {'id': id, 'name': row[0], 'age': row[1], 'course': row[2]}
            return render_template('edit.html', student=student)
        else:
            return "Student not found", 404

@app.route('/api/students')
def api_students():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("SELECT name, age, course FROM students")
        students = [{'name': row[0], 'age': row[1], 'course': row[2]} for row in c.fetchall()]
    return jsonify(students)

@app.route('/export')
def export_students():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("SELECT name, age, course FROM students")
        students = c.fetchall()

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['Name', 'Age', 'Course'])
    for student in students:
        writer.writerow(student)

    output.seek(0)
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=students.csv"}
    )

@app.route('/dashboard')
def dashboard():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("SELECT course, COUNT(*) FROM students GROUP BY course")
        data = c.fetchall()

    labels = [row[0] for row in data]
    counts = [row[1] for row in data]

    return render_template('dashboard.html', labels=labels, counts=counts)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
# This script initializes the database and starts the Flask server.