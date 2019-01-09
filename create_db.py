import sqlite3
import os
import sys
import atexit

# region Global Variables
"""
boolean to check whether the database exists or not.
"""
DBExist = os.path.isfile("schedule.db")

"""
The sqlite database that is connected to "schedule.db" database.
"""
db = sqlite3.connect("schedule.db")

"""
database cursor to iterate over and execute general queries from the 'schedule.db' database.
"""
data_cursor = db.cursor()
# endregion Global Variables


def close_data_base():
    """
    Committing the changes to the 'schedule.db' database,
    closing the schedule.db cursor, and than closing the connection.
    :return: None
    """
    db.commit()
    data_cursor.close()
    db.close()


# finally - closing the cursor and database
atexit.register(close_data_base)


def create_db():
    """
    Creating three tables in the 'schedule.db' database:
        Courses --> hold information about running and pending courses.
        Students
    :return:None.
    """
    data_cursor.execute("CREATE TABLE IF NOT EXISTS courses (id INTEGER PRIMARY KEY, course_name TEXT NOT NULL, student TEXT NOT NULL, number_of_students INTEGER NOT NULL, class_id INTEGER REFERENCES classrooms(id), course_length INTEGER NOT NULL)")
    data_cursor.execute("CREATE TABLE IF NOT EXISTS students (grade TEXT PRIMARY KEY, count INTEGER NOT NULL)")
    data_cursor.execute("CREATE TABLE IF NOT EXISTS classrooms (id INTEGER PRIMARY KEY, location TEXT NOT NULL, current_course_id INTEGER NOT NULL, current_course_time_left INTEGER NOT NULL)")


def inserting_initial_data(config_file):
    """
    inserting initial data in the tables of 'schedule.db' database from the given config file.
    :param config_file:             path to the config text file.
    :return: None.
    """
    with open(config_file, 'r') as config:
        lines = config.read()
    for line in lines.split('\n'):
        line = line.strip()
        parameters = line.split(",")
        if ("S" in parameters) or ("R" in parameters) or ("C" in parameters):
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
    """
    Prints all the rows of the available tables  in the "schedule.db" database.
    :return: None.
    """
    # courses:
    print("courses")
    data_cursor.execute("SELECT * FROM courses")
    for row in data_cursor:
        print(row)
    # classrooms:
    print("classrooms")
    data_cursor.execute("SELECT * FROM classrooms")
    for row in data_cursor:
        print(row)
    # students:
    print("students")
    data_cursor.execute("SELECT * FROM students")
    for row in data_cursor:
        print(row)


def main():
    """
    main function of the 'create_db.py' file.
    :return: None.
    """
    if not DBExist:
        create_db()
        inserting_initial_data(sys.argv[1])
        print_tables()


if __name__ == '__main__':
    main()
