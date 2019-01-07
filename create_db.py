import sqlite3
import os
import sys
import atexit

# checks if the the classes data base is already exists.
DBExist = os.path.isfile("classes.db")

# connects to classes.db, creates it if it doesn't exists.
db = sqlite3.connect("classes.db")

# cursor to read data from the data base.
data_cursor = db.cursor()


def close_data_base():
    db.commit()
    data_cursor.close()
    db.close()


# finally - closing the cursor and database
atexit.register(close_data_base)


def create_db():
    data_cursor.execute("CREATE TABLE IF NOT EXISTS courses (id INTEGER PRIMARY KEY, course_name TEXT NOT NULL, student TEXT NOT NULL, number_of_students INTEGER NOT NULL, class_id INTEGER REFERENCES classrooms(id), course_length INTEGER NOT NULL)")
    data_cursor.execute("CREATE TABLE IF NOT EXISTS students (grade TEXT PRIMARY KEY, count INTEGER NOT NULL)")
    data_cursor.execute("CREATE TABLE IF NOT EXISTS classrooms (id INTEGER PRIMARY KEY, location TEXT NOT NULL, current_course_id INTEGER NOT NULL, current_course_time_left INTEGER NOT NULL)")


def inserting_initial_data(config_file):
    with open(config_file, 'r') as config:
        lines = config.read()
    for line in lines.split('\n'):
        line = line.strip()
        parameters = line.split(",")
        if (("S" in parameters) or ("R" in parameters) or ("C" in parameters)):
            first_letter = line[0]
            if first_letter == "S":
                # inserting to students table
                grade = parameters[1].strip()
                count = parameters[2].strip()
                data_cursor.execute("INSERT INTO students (grade, count) VALUES (?, ?)", [grade, count])

            elif first_letter == "R":
                # inserting to classrooms table
                id = parameters[1].strip()
                location = parameters[2].strip()
                current_course_id = 0
                current_course_time_left = 0
                data_cursor.execute("INSERT INTO classrooms (id, location, current_course_id, current_course_time_left) VALUES (?, ?, ?, ?)", [id, location, current_course_id, current_course_time_left])

            elif first_letter == "C":
                # inserting to courses table
                id = parameters[1].strip()
                course_name = parameters[2].strip()
                student = parameters[3].strip()
                number_of_students = parameters[4].strip()
                class_id = parameters[5].strip()
                course_length = parameters[6].strip()
                data_cursor.execute("INSERT INTO courses (id, course_name, student, number_of_students, class_id, course_length) VALUES (?, ?, ?, ?, ?, ?)", [id, course_name, student, number_of_students, class_id, course_length])


def print_tables():
    # courses:
    print("courses")
    data_cursor.execute("SELECT * FROM courses")
    for row in data_cursor:
        print(row)
    #classrooms:
    print("classrooms")
    data_cursor.execute("SELECT * FROM classrooms")
    for row in data_cursor:
        print(row)

    #students:
    print("students")
    data_cursor.execute("SELECT * FROM students")
    for row in data_cursor:
        print(row)


if __name__ == '__main__':
    if not DBExist:
        create_db()
        inserting_initial_data(sys.argv[1])
        print_tables()
