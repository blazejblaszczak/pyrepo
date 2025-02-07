from functools import reduce, partial, lru_cache

# Task 1: Implement Pure Functions for Student Management
def add_student(database, student):
    new_database = database + [student]
    return new_database
  
def delete_student(database, student_id):
    # return everything except for the student_id to be deleted
    return [student for student in database if student['id']!=student_id]
  
# Task 2: Use Filter to find open courses
def find_open_courses(courses):
    '''
    [
    {'course_id': 'CS101', 'name': 'Introduction to Computer Science', 'seats_available': 30, 'students': [1, 2]},
    {'course_id': 'MATH101', 'name': 'Calculus', 'seats_available': 20, 'students': []},
    {'course_id': 'ENG101', 'name': 'English Composition', 'seats_available': 25, 'students': [3, 4]},
    ]
    '''
    return list(filter(lambda course: course['seats_available']>0,courses))
  
def get_grade_letter(points):
    if points > 90:
        return 'A'
    elif points >= 80:
        return 'B'
    elif points >= 70:
        return 'C'
    elif points >= 60:
        return 'D'
    else:
        return 'F'
      
# Task 2b: Use Map to find student grades
def get_grades(grades):
    #return a new list of dictionaries => copy all existing data, also add the letter grade
    return list(map(lambda x: {'student_id':x['student_id'],
                          'course_id':x['course_id'],
                          'points':x['points'],
                          'grade':get_grade_letter(x['points'])},grades))
  
# Task 3: Apply Reduce for Grade Calculation
# Task 6: Apply caching for better performance
@lru_cache(maxsize=10)
def get_student_average(scores,id):
    '''
    [
    {'student_id': 1, 'course_id': 101, 'points': 95},
    {'student_id': 1, 'course_id': 102, 'points': 80}
    ]
    '''
    filtered_scores = [score[2] for score in scores if score[0]==id]
    total_score = reduce(lambda x,y: x+y,filtered_scores)
    return total_score/len(filtered_scores)
  
# Task 4: Employ List Comprehensions for Student Enrollment
def get_enrolled_students(courses, course_id, students):
    '''
    [
    {'id': 1, 'name': 'Alice'},
    {'id': 2, 'name': 'Bob'}
    ]
    '''
    '''
    [
    {'course_id': 'CS101','students': [1, 2], 'name': 'Introduction to Computer Science', 'seats_available': 30, }
    ]
    '''
    return [student for course in courses
             if course['course_id']==course_id
             for student_id in course['students']
             for student in students
             if student['id']==student_id]
  
def add_student_to_course(student_id, course_id, courses, students):
    # Check if student_id and course_id exist
    if student_id not in [student['id'] for student in students]:
        print(f"Error: Student with ID {student_id} does not exist.")
        return False
    if course_id not in [course['course_id'] for course in courses]:
        print(f"Error: Course with ID {course_id} does not exist.")
        return False
    
    # Find the course with the given course_id
    for course in courses:
        if course['course_id'] == course_id:
            # Check if the student is already registered for the course
            if student_id in course['students']:
                print(f"Warning: Student {student_id} already registed for {course_id}.")
                return False
            
            # Check if there are available seats in the course
            if len(course['students']) >= course['seats_available']:
                print(f"Error: Course {course['name']} is full. No available seats.")
                return False
            
            # Add student to the course's list of students
            course['students'].append(student_id)
            print(f"Success: Student {students[student_id]} has been added to course {course['name']}.")
            return True
          
scores = [
    {'student_id': 1, 'course_id': 101, 'points': 95},
    {'student_id': 1, 'course_id': 102, 'points': 80},
    {'student_id': 1, 'course_id': 103, 'points': 70},
    {'student_id': 2, 'course_id': 101, 'points': 75},
    {'student_id': 2, 'course_id': 102, 'points': 85},
    {'student_id': 3, 'course_id': 101, 'points': 85},
    {'student_id': 3, 'course_id': 103, 'points': 90},
    {'student_id': 4, 'course_id': 102, 'points': 65},
    {'student_id': 4, 'course_id': 103, 'points': 80},
    {'student_id': 5, 'course_id': 101, 'points': 55},
    {'student_id': 5, 'course_id': 102, 'points': 60},
    {'student_id': 6, 'course_id': 102, 'points': 95},
    {'student_id': 6, 'course_id': 103, 'points': 70},
    {'student_id': 7, 'course_id': 101, 'points': 85},
    {'student_id': 7, 'course_id': 102, 'points': 90},
]
courses = [
    {'course_id': 'CS101', 'name': 'Introduction to Computer Science', 'seats_available': 30, 'students': [1, 2]},
    {'course_id': 'MATH101', 'name': 'Calculus', 'seats_available': 20, 'students': []},
    {'course_id': 'ENG101', 'name': 'English Composition', 'seats_available': 0, 'students': [3, 4]},
]
students = [
    {'id': 1, 'name': 'Alice'},
    {'id': 2, 'name': 'Bob'},
    {'id': 3, 'name': 'Charlie'},
    {'id': 4, 'name': 'David'}
]

# You can do your testing here
updated_students = add_student(students, {'id':5,'name':'Mary'})
print("Updated students:", updated_students)
students_after_delete = delete_student(students,2)
print("After deleting Bob:",students_after_delete )
open_courses = find_open_courses(courses)
print("Open courses:", open_courses)
scores_with_grades = get_grades(scores)
print("Scores with grades", scores_with_grades)
scores_values = []

for score in scores:
    v = list(score.values())
    scores_values.append((v[0],v[1],v[2]))

scores_tuple = tuple(scores_values) #tuple of tuples
student_1_avg = get_student_average(scores_tuple,1)
print("Student 1 avg:", student_1_avg)
students_in_eng101 = get_enrolled_students(courses, 'ENG101', students)
print("Students in ENG101:", students_in_eng101)

#Task 5 : Apply add_student partially before adding students
partial_add_student = partial(add_student, database = students_after_delete)
students_with_jack = partial_add_student(student = {'id':6,'name':'Jack'})
print("Updated Student List: ",students_with_jack)
