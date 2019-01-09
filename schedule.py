import os
import sqlite3

# region Special Indexes

# region Courses Indexes
"""
The following titles-to-indexes belongs to the 'Courses' table in the 'schedule.db' database.  
"""
COURSE_ID_INDEX = 0
COURSE_NAME_INDEX = 1
COURSE_STUDENT_INDEX = 2
COURSE_NUMBER_OF_STUDENTS_INDEX = 3
COURSE_CLASS_ID_INDEX = 4
COURSE_LENGTH_INDEX = 5
# endregion Courses Indexes

# region Students Indexes
"""
The following titles-to-indexes belongs to the 'Students' table in the 'schedule.db' database.
"""
STUDENTS_GRADE_INDEX = 0
STUDENTS_COUNT_INDEX = 1
# endregion Students Indexes

# region Classrooms Indexes
"""
The following titles-to-indexes belongs to the 'Classrooms' table in the 'schedule.db' database.
"""
CLASSROOM_ID_INDEX = 0
CLASSROOM_LOCATION_INDEX = 1
CLASSROOM_C_C_ID_INDEX = 2
CLASSROOM_C_C_TIME_INDEX = 3
# endregion Classrooms Indexes

# endregion Special Indexes


# region Queries

# region Courses Queries
"""
Queries to be used on the 'Courses' table in the 'schedule.db' database 
"""
Q_SELECT_ALL_FROM_COURSES = "SELECT * FROM courses"
Q_GET_NEXT_COURSE_BY_CLASS = "SELECT * FROM courses WHERE class_id = ? LIMIT 1;"
Q_GET_COURSE_NAME_BY_ID = "SELECT course_name FROM courses WHERE id = ?"
Q_GET_COURSE_BY_ID = "SELECT * FROM courses WHERE  id = ?"
Q_DELETE_COURSE_BY_ID = "DELETE FROM courses WHERE id = ?"
Q_CHECK_NUMBER_OF_COURSES = "SELECT COUNT(*) FROM courses"
# endregion Courses Queries

# region Classrooms Queries
"""
Queries to be used on the 'Classrooms' table in the 'schedule.db' database 
"""
Q_SELECT_ALL_FROM_CLASSROOMS = "SELECT * FROM classrooms"
Q_UPDATE_COURSE_NAME_AND_TIME_IN_CLASSROOM = "UPDATE classrooms SET current_course_id = ?, current_course_time_left = ? WHERE id = ?"
Q_UPDATE_TIME_IN_CLASSROOM = "UPDATE classrooms SET current_course_time_left = ? WHERE id = ?"
# endregion Classrooms Queries

# region Students Queries
"""
Queries to be used on the 'Students' table in the 'schedule.db' database 
"""
Q_CHECK_STUDENT_COUNT = "SELECT count FROM students WHERE grade = ?"
Q_UPDATE_STUDENTS_COUNT = "UPDATE students SET count = ? WHERE grade = ?"
Q_SELECT_ALL_FROM_STUDENTS = "SELECT * FROM students"
# endregion Students Queries

# endregion Queries


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
database cursor to iterate over general queries from the 'schedule.db' database.
"""
data_cursor = db.cursor()
"""
database cursor to iterate over queries that are related to the 'classrooms' table,
from the 'schedule.db' database.
"""
classroom_cursor = db.cursor()
"""
database cursor to iterate over queries that are related to the 'courses' table,
from the 'schedule.db' database.
"""
course_cursor = db.cursor()
"""
database cursor to iterate over queries that are related to the 'students' table,
from the 'schedule.db' database.
"""
student_cursor = db.cursor()
"""
integer number to represents the number of iterations that went so far.
"""
iteration_number = 0
# endregion Global Variables


def print_tables():
    """
    Prints all the rows of the available tables in the "schedule.db" database.
    :return: None
    """
    # courses:
    print("courses")
    course_cursor.execute(Q_SELECT_ALL_FROM_COURSES)
    for row in course_cursor:
        print(row)
    # classrooms:
    print("classrooms")
    classroom_cursor.execute(Q_SELECT_ALL_FROM_CLASSROOMS)
    for row in classroom_cursor:
        print(row)

    # students:
    print("students")
    student_cursor.execute(Q_SELECT_ALL_FROM_STUDENTS)
    for row in student_cursor:
        print(row)


def updating_number_of_courses():
    """
    Checks the courses table in the 'schedule.db' database what is the current number of pending or running courses.
    :return:                Integer number represents the number of courses
                            that are currently still in the 'schedule.db' database
    """
    course_cursor.execute(Q_CHECK_NUMBER_OF_COURSES)
    output = course_cursor.fetchone()[0]
    return output


def new_course_into_classroom(course, classroom):
    """
    Updates a given class to to now contain a given course the schedule database.
    :param course:                  Tuple represent all the details of a course
                                    (row from the "courses" table in the "schedule.db" database).
    :param classroom:               Tuple represents a classroom.
                                    (row from the "classrooms" table in the "schedule.db" database).
    :return: None
    """
    # getting the needed information from the given classroom and course
    course_id = course[COURSE_ID_INDEX]
    course_length = course[COURSE_LENGTH_INDEX]
    course_name = course[COURSE_NAME_INDEX]
    classroom_id = classroom[CLASSROOM_ID_INDEX]
    classroom_location = classroom[CLASSROOM_LOCATION_INDEX]
    # executing the update query
    classroom_cursor.execute(Q_UPDATE_COURSE_NAME_AND_TIME_IN_CLASSROOM, [course_id, course_length, classroom_id])
    print("({}) {}: {} is schedule to start".format(iteration_number, classroom_location, course_name))
    # updating the number of student after the new class has begun
    student_type = course[COURSE_STUDENT_INDEX]
    amount_of_students = course[COURSE_NUMBER_OF_STUDENTS_INDEX]
    updated_amount_of_students = student_cursor.execute(Q_CHECK_STUDENT_COUNT, [student_type]).fetchone()[0] - amount_of_students
    if updated_amount_of_students < 0:
        # if the number of available student is smaller the the capacity of the course -->
        # update to zero (enter all available students)
        updated_amount_of_students = 0
    student_cursor.execute(Q_UPDATE_STUDENTS_COUNT, [updated_amount_of_students, student_type])


def assign_class_if_possible(classroom):
    """
    Assign a given classroom to a pending course to start, and update the values in the 'schedule.db' data base accordingly.
    If there are no pending courses to the given class room, will update the values of time left and course_id to '0'.
    :param classroom:               Tuple represents all the details of a specific classroom.
                                    (row in the 'classrooms' table in the  'schedule.db' database.
    :return: None.
    """
    current_classroom_id = classroom[CLASSROOM_ID_INDEX]
    # getting the next matching pending course to this class.
    course_cursor.execute(Q_GET_NEXT_COURSE_BY_CLASS, [current_classroom_id])
    course_to_assign = course_cursor.fetchone()
    if course_to_assign is not None:
        # if there are still courses waiting for this classroom --> inserting the next course in
        new_course_into_classroom(course_to_assign, classroom)
        # otherwise --> update nothing.


def check_occupied_classroom(classroom):
    """
    Check and updates the current status of a given classroom.
    if a course is ending --> will try to assign a pending course to start in this class.
    else --> will reduce 1 from the time left in the course in the given class.
    :param classroom:               Tuple represents all the details of a specific classroom to check.
                                    (row in the 'classrooms' table in the  'schedule.db' database.

    :return: None.
    """
    current_classroom_id = classroom[CLASSROOM_ID_INDEX]
    # getting the current course that is in this class from the database.
    current_course = course_cursor.execute(Q_GET_COURSE_BY_ID, [classroom[CLASSROOM_C_C_ID_INDEX]]).fetchone()
    current_time = classroom[CLASSROOM_C_C_TIME_INDEX] - 1
    # updating the new time left in the class
    classroom_cursor.execute(Q_UPDATE_TIME_IN_CLASSROOM, [current_time, current_classroom_id])

    if current_time == 0:
        # the course ended --> printing message, and trying to find the next matching pending course.
        print("({}) {}: {} is done".format(iteration_number, classroom[CLASSROOM_LOCATION_INDEX], current_course[COURSE_NAME_INDEX]))
        # delete the course that was over from the database.
        course_cursor.execute(Q_DELETE_COURSE_BY_ID, [current_course[COURSE_ID_INDEX]])
        # update the current classroom to be empty --> updating time left and course_id to 0
        classroom_cursor.execute(Q_UPDATE_COURSE_NAME_AND_TIME_IN_CLASSROOM, [0, 0, current_classroom_id])
        assign_class_if_possible(classroom)
    else:
        # if the course is not finished yet --> print occupied message
        print("({}) {}: occupied by {}".format(iteration_number, classroom[CLASSROOM_LOCATION_INDEX], current_course[COURSE_NAME_INDEX]))


def close_data_base():
    """
    Committing the changes to the 'schedule.db' database,
    closing the schedule.db cursors, and than closing the connection.
    :return: None
    """
    db.commit()
    data_cursor.close()
    course_cursor.close()
    student_cursor.close()
    classroom_cursor.close()
    db.close()


def main():
    """
    main function of the 'schedule.py' module.
    :return: None
    """
    global iteration_number
    if DBExist:
        # only if the database 'schedule.db' exists
        number_of_courses = updating_number_of_courses()
        if number_of_courses == 0:
            # if there are no courses in the database --> print current status
            print_tables()
        else:
            while DBExist and number_of_courses > 0:
                # while there are still courses that are not finished
                for current_classroom in data_cursor.execute(Q_SELECT_ALL_FROM_CLASSROOMS):
                    # for each classroom in the classrooms table
                    if current_classroom[CLASSROOM_C_C_TIME_INDEX] == 0:
                        # if this class is free --> assign a course if possible
                        assign_class_if_possible(current_classroom)
                    else:
                        # this class is occupied
                        check_occupied_classroom(current_classroom)
                # printing the current status of the table,increase the iteration number,
                # and checking the current number of courses
                print_tables()
                iteration_number += 1
                number_of_courses = updating_number_of_courses()
            close_data_base()


if __name__ == '__main__':
    main()

