import sqlite3
import os
import sys

# checks if the the classes data base is already exists.
DBExist = os.path.isfile("classes.db")

# connects to classes.db, creates it if it doesn't exists.
db = sqlite3.connect("classes.db")

# cursor to read data from the data base.
data_cursor = db.cursor()

def create_db():
    db.execute("CREATE TABLE IF NOT EXISTS courses (id INTEGER PRIMARY KEY, course_name TEXT NOT NULL, student TEXT NOT NULL, number_of_students INTEGER NOT NULL, class_id INTEGER REFERENCES classrooms(id), course_length INTEGER NOT NULL")
    db.execute("CREATE TABLE IF NOT EXISTS students (grade TEXT PRIMARY KEY, count INTEGER NOT NULL")
    db.execute("CREATE TABLE IF NOT EXISTS classrooms (id INTEGER PRIMARY KEY, location TEXT NOT NULL, current_course_id INTEGER NOT NULL, current_course_time_left INTEGER NOT NULL")

def inserting_initial_data(config_file):
    with open(config_file, 'r') as config:
        lines = config.read()
    for line in lines:
        line = line.strip()
        parameters = line.split(",")
        first_letter = parameters[0]
        if first_letter == "S":
            # inserting to student table
            grade = parameters[1].strip()
            count = parameters[2].strip()
            db.execute("INSERT INTO students (grade, count) VALUES (?, ?)", [grade, count])

        elif first_letter == "R":
            # inserting to classrooms table
            id = parameters[1].strip()
            location = parameters[2].strip()
            current_course_id = parameters[3].strip()
            current_course_time_left = parameters[4].strip()
            db.execute("INSERT INTO classrooms (id, location, current_course_id, current_course_time_left) VALUES (?, ?, ?, ?)", [id, location, current_course_id, current_course_time_left])

        elif first_letter == "C":
            # inserting to courses table
            id = parameters[1].strip()
            course_name = parameters[2].strip()
            student = parameters[3].strip()
            number_of_students = parameters[4].strip()
            class_id = parameters[5].strip()
            course_length = parameters[6].strip()
            db.execute("INSERT INTO courses (id, course_name, student, number_of_students, class_id, course_length) VALUES (?, ?, ?, ?, ?, ?)", [id, course_name, student, number_of_students, class_id, course_length])

if __name__ == '__main__':
    if not DBExist:
        create_db()
        inserting_initial_data(sys.argv[0])