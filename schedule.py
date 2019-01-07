import os
import sqlite3

# region Special Indexes

# region Courses Indexes

COURSE_ID_INDEX = 0
COURSE_NAME_INDEX = 1
COURSE_STUDENT_INDEX = 2
COURSE_NUMBER_OF_STUDENTS_INDEX = 3
COURSE_CLASS_ID_INDEX = 4
COURSE_LENGTH_INDEX = 5
# endregion Courses Indexes


# region Students Indexes

STUDENTS_GRADE_INDEX = 0
STUDENTS_COUNT_INDEX = 1
# endregion Students Indexes

# region Classrooms Indexes
CLASSROOM_ID_INDEX = 0
CLASSROOM_LOCATION_INDEX = 1
CLASSROOM_C_C_ID_INDEX = 2
CLASSROOM_C_C_TIME_INDEX = 3
# endregion Classrooms Indexes

# endregion Special Indexes


# region Queries

# region Courses Queries
Q_SELECT_ALL_FROM_COURSES = "SELECT * FROM courses"
Q_GET_NEXT_COURSE_BY_CLASS = "SELECT * FROM courses WHERE class_id = ? LIMIT 1;"
Q_GET_COURSE_NAME_BY_ID = "SELECT course_name FROM courses WHERE id = ?"
Q_GET_COURSE_BY_ID = "SELECT * FROM courses WHERE  id = ?"
Q_DELETE_COURSE_BY_ID = "DELETE FROM courses WHERE id = ?"
Q_CHECK_NUMBER_OF_COURSES = "SELECT COUNT(*) FROM courses"
# endregion Courses Queries

# region Classrooms Queries

Q_SELECT_ALL_FROM_CLASSROOMS = "SELECT * FROM classrooms"
Q_UPDATE_COURSE_NAME_AND_TIME_IN_CLASSROOM = "UPDATE classrooms SET current_course_id = ?, current_course_time_left = ? WHERE id = ?"
Q_UPDATE_TIME_IN_CLASSROOM = "UPDATE classrooms SET current_course_time_left = ? WHERE id = ?"
# endregion Classrooms Queries

# region Students Queries

Q_CHECK_STUDENT_COUNT = "SELECT count FROM students WHERE grade = ?"
Q_UPDATE_STUDENTS_COUNT = "UPDATE students SET count = ? WHERE grade = ?"
Q_SELECT_ALL_FROM_STUDENTS = "SELECT * FROM students"
# endregion Students Queries

# endregion Queries


# region Global Variables
DBExist = os.path.isfile("classes.db")
db = sqlite3.connect("classes.db")
# cursors to collect data from the database
data_cursor = db.cursor()
classroom_cursor = db.cursor()
course_cursor = db.cursor()
student_cursor = db.cursor()
# iteration counter fo the main loop of the schedule main
iteration_number = 0
# endregion Global Variables


def print_tables():
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
    course_cursor.execute(Q_CHECK_NUMBER_OF_COURSES)
    output = course_cursor.fetchone()[0]
    return output


def new_course_into_classroom(course, classroom):
    # getting the needed information from the given classroom and course
    course_id = course[COURSE_ID_INDEX]
    course_length = course[COURSE_LENGTH_INDEX]
    course_name = course[COURSE_NAME_INDEX]
    classroom_id = classroom[CLASSROOM_ID_INDEX]
    classroom_location = classroom[CLASSROOM_LOCATION_INDEX]

    classroom_cursor.execute(Q_UPDATE_COURSE_NAME_AND_TIME_IN_CLASSROOM, [course_id, course_length, classroom_id])
    # todo check if schedule is with d or without
    print("({}) {}: {} is schedule to start".format(iteration_number, classroom_location, course_name))
    # updating the number of student after the new class has begun
    student_type = course[COURSE_STUDENT_INDEX]
    amount_of_students = course[COURSE_NUMBER_OF_STUDENTS_INDEX]
    updated_amount_of_students = student_cursor.execute(Q_CHECK_STUDENT_COUNT, [student_type]).fetchone()[0] - amount_of_students
    student_cursor.execute(Q_UPDATE_STUDENTS_COUNT, [updated_amount_of_students, student_type])


# def print_occupied():
#    course_name = course_cursor.execute(Q_GET_COURSE_NAME_BY_ID,
#                                        [current_classroom[CLASSROOM_C_C_ID_INDEX]]).fetchone()[COURSE_NAME_INDEX]
#    print("({}) {}: occupied by {}".format(iteration_number, current_classroom[CLASSROOM_LOCATION_INDEX], course_name))


def assign_class_if_possible(classroom):
    current_classroom_id = classroom[CLASSROOM_ID_INDEX]
    course_cursor.execute(Q_GET_NEXT_COURSE_BY_CLASS, [current_classroom_id])
    course_to_assign = course_cursor.fetchone()
    if course_to_assign is not None:
        # if there are still courses waiting for this classroom --> inserting the next course in

        new_course_into_classroom(course_to_assign, classroom)


def check_occupied_classroom(classroom):
    current_classroom_id = classroom[CLASSROOM_ID_INDEX]
    current_course = course_cursor.execute(Q_GET_COURSE_BY_ID, [classroom[CLASSROOM_C_C_ID_INDEX]]).fetchone()
    current_time = classroom[CLASSROOM_C_C_TIME_INDEX] - 1
    classroom_cursor.execute(Q_UPDATE_TIME_IN_CLASSROOM, [current_time, current_classroom_id])

    if current_time == 0:
        # the course ended
        print("({}) {}: {} is done".format(iteration_number, classroom[CLASSROOM_LOCATION_INDEX], current_course[COURSE_NAME_INDEX]))
        course_cursor.execute(Q_DELETE_COURSE_BY_ID, [current_course[COURSE_ID_INDEX]])
        classroom_cursor.execute(Q_UPDATE_COURSE_NAME_AND_TIME_IN_CLASSROOM, [0, 0, current_classroom_id])
        assign_class_if_possible(classroom)
        # course_cursor.execute(Q_GET_NEXT_COURSE_BY_CLASS, [current_classroom_id])
        # if course_cursor.rowcount > 0:
        #     # if there are still courses waiting for this classroom --> inserting the next course in
        #     current_course = course_cursor.fetchone()
        #     new_course_into_classroom(current_course, current_classroom)
        # else:
        #     classroom_cursor.execute(Q_UPDATE_COURSE_NAME_AND_TIME_IN_CLASSROOM, [0, 0, current_classroom_id])

    else:
        print("({}) {}: occupied by {}".format(iteration_number, current_classroom[CLASSROOM_LOCATION_INDEX], current_course[COURSE_NAME_INDEX]))


if __name__ == '__main__':

    number_of_courses = updating_number_of_courses()
    if number_of_courses == 0:
        # if there are no courses print current status
        # todo what if db doesn't exists?
        print_tables()
    else:
        while DBExist and number_of_courses > 0:
            # still have courses that are not finished
            for current_classroom in data_cursor.execute(Q_SELECT_ALL_FROM_CLASSROOMS):
                # for each classroom in the classrooms table
                if current_classroom[CLASSROOM_C_C_TIME_INDEX] == 0:
                    # if this class is free --> assign a course if possible
                    assign_class_if_possible(current_classroom)

                else:
                    # this class is occupied
                    check_occupied_classroom(current_classroom)

            print_tables()
            iteration_number += 1
            number_of_courses = updating_number_of_courses()

