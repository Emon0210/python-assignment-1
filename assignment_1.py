

# Student Management System (CLI-based) with OOP and JSON save/load.


import json
from typing import Dict, List

class Person:
    def __init__(self, name: str, age: int, address: str):
        self.name = name
        self.age = age
        self.address = address

    def display_person_info(self):
        print(f"Name: {self.name}")
        print(f"Age: {self.age}")
        print(f"Address: {self.address}")

    def to_dict(self):
        return {"name": self.name, "age": self.age, "address": self.address}

    @classmethod
    def from_dict(cls, data):
        return cls(data["name"], data["age"], data["address"])

class Student(Person):
    def __init__(self, name: str, age: int, address: str, student_id: str):
        super().__init__(name, age, address)
        self.student_id = student_id
        self.grades: Dict[str, str] = {}   # course_code -> grade
        self.courses: List[str] = []       # list of course_codes

    def add_grade(self, course_code: str, grade: str):
        if course_code not in self.courses:
            raise ValueError(f"Student {self.student_id} is not enrolled in course {course_code}.")
        self.grades[course_code] = grade

    def enroll_course(self, course_code: str):
        if course_code in self.courses:
            raise ValueError(f"Student {self.student_id} already enrolled in {course_code}.")
        self.courses.append(course_code)

    def display_student_info(self):
        print("Student Information:")
        self.display_person_info()
        print(f"ID: {self.student_id}")
        print("Enrolled Courses:", ", ".join(self.courses) if self.courses else "None")
        print("Grades:", self.grades if self.grades else "{}")

    def to_dict(self):
        base = super().to_dict()
        base.update({
            "student_id": self.student_id,
            "grades": self.grades,
            "courses": self.courses
        })
        return base

    @classmethod
    def from_dict(cls, data):
        s = cls(data["name"], data["age"], data["address"], data["student_id"])
        s.grades = data.get("grades", {})
        s.courses = data.get("courses", [])
        return s

class Course:
    def __init__(self, course_name: str, course_code: str, instructor: str):
        self.course_name = course_name
        self.course_code = course_code
        self.instructor = instructor
        self.students: List[str] = []   # store student_ids

    def add_student(self, student_id: str):
        if student_id in self.students:
            raise ValueError(f"Student {student_id} already enrolled in {self.course_code}.")
        self.students.append(student_id)

    def display_course_info(self, students_lookup: Dict[str, Student] = None):
        print("Course Information:")
        print(f"Course Name: {self.course_name}")
        print(f"Code: {self.course_code}")
        print(f"Instructor: {self.instructor}")
        if students_lookup:
            names = [students_lookup[sid].name for sid in self.students if sid in students_lookup]
            print("Enrolled Students:", ", ".join(names) if names else "None")
        else:
            print("Enrolled Students:", ", ".join(self.students) if self.students else "None")

    def to_dict(self):
        return {
            "course_name": self.course_name,
            "course_code": self.course_code,
            "instructor": self.instructor,
            "students": self.students
        }

    @classmethod
    def from_dict(cls, data):
        c = cls(data["course_name"], data["course_code"], data["instructor"])
        c.students = data.get("students", [])
        return c

class StudentManagementSystem:
    def __init__(self):
        # dictionaries keyed by student_id and course_code
        self.students: Dict[str, Student] = {}
        self.courses: Dict[str, Course] = {}

    # --- student operations ---
    def add_student(self, name: str, age: int, address: str, student_id: str):
        if student_id in self.students:
            raise ValueError(f"Student ID {student_id} already exists.")
        self.students[student_id] = Student(name, age, address, student_id)

    def get_student(self, student_id: str) -> Student:
        if student_id not in self.students:
            raise KeyError(f"Student ID {student_id} not found.")
        return self.students[student_id]

    # --- course operations ---
    def add_course(self, course_name: str, course_code: str, instructor: str):
        if course_code in self.courses:
            raise ValueError(f"Course code {course_code} already exists.")
        self.courses[course_code] = Course(course_name, course_code, instructor)

    def get_course(self, course_code: str) -> Course:
        if course_code not in self.courses:
            raise KeyError(f"Course code {course_code} not found.")
        return self.courses[course_code]

    # --- enrollment ---
    def enroll_student_in_course(self, student_id: str, course_code: str):
        student = self.get_student(student_id)
        course = self.get_course(course_code)
        # perform enrollment
        student.enroll_course(course_code)
        course.add_student(student_id)

    # --- grades ---
    def add_grade_for_student(self, student_id: str, course_code: str, grade: str):
        student = self.get_student(student_id)
        if course_code not in student.courses:
            raise ValueError(f"Student {student_id} is not enrolled in {course_code}.")
        student.add_grade(course_code, grade)

    # --- display ---
    def display_student(self, student_id: str):
        student = self.get_student(student_id)
        student.display_student_info()

    def display_course(self, course_code: str):
        course = self.get_course(course_code)
        course.display_course_info(self.students)

    # --- file operations ---
    def save_data(self, filename="students_courses.json"):
        data = {
            "students": {sid: s.to_dict() for sid, s in self.students.items()},
            "courses": {cc: c.to_dict() for cc, c in self.courses.items()}
        }
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        print("All student and course data saved successfully.")

    def load_data(self, filename="students_courses.json"):
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        students = data.get("students", {})
        courses = data.get("courses", {})
        # rebuild students and courses
        self.students = {sid: Student.from_dict(sdata) for sid, sdata in students.items()}
        self.courses = {cc: Course.from_dict(cdata) for cc, cdata in courses.items()}
        # ensure consistency: if course lists student ids that exist, ensure student's courses include course_code
        for cc, c in self.courses.items():
            for sid in c.students:
                if sid in self.students:
                    if cc not in self.students[sid].courses:
                        self.students[sid].courses.append(cc)
        print("Data loaded successfully.")

def main_menu():
    sms = StudentManagementSystem()
    MENU = """
==== Student Management System ====

1. Add New Student
2. Add New Course
3. Enroll Student in Course
4. Add Grade for Student
5. Display Student Details
6. Display Course Details
7. Save Data to File
8. Load Data from File
0. Exit
"""
    while True:
        print(MENU)
        choice = input("Select Option: ").strip()
        try:
            if choice == "1":
                name = input("Enter Name: ").strip()
                age = int(input("Enter Age: ").strip())
                address = input("Enter Address: ").strip()
                student_id = input("Enter Student ID: ").strip()
                sms.add_student(name, age, address, student_id)
                print(f"Student {name} (ID: {student_id}) added successfully.")
            elif choice == "2":
                cname = input("Enter Course Name: ").strip()
                ccode = input("Enter Course Code: ").strip()
                instr = input("Enter Instructor: ").strip()
                sms.add_course(cname, ccode, instr)
                print(f"Course {cname} (Code: {ccode}) created with instructor {instr}.")
            elif choice == "3":
                sid = input("Enter Student ID: ").strip()
                ccode = input("Enter Course Code: ").strip()
                sms.enroll_student_in_course(sid, ccode)
                print(f"Student {sms.get_student(sid).name} (ID: {sid}) enrolled in {sms.get_course(ccode).course_name} (Code: {ccode}).")
            elif choice == "4":
                sid = input("Enter Student ID: ").strip()
                ccode = input("Enter Course Code: ").strip()
                grade = input("Enter Grade: ").strip()
                sms.add_grade_for_student(sid, ccode, grade)
                print(f"Grade {grade} added for {sms.get_student(sid).name} in {sms.get_course(ccode).course_name}.")
            elif choice == "5":
                sid = input("Enter Student ID: ").strip()
                sms.display_student(sid)
            elif choice == "6":
                ccode = input("Enter Course Code: ").strip()
                sms.display_course(ccode)
            elif choice == "7":
                fname = input("Enter filename to save (default: students_courses.json): ").strip() or "students_courses.json"
                sms.save_data(fname)
            elif choice == "8":
                fname = input("Enter filename to load (default: students_courses.json): ").strip() or "students_courses.json"
                sms.load_data(fname)
            elif choice == "0":
                print("Exiting Student Management System. Goodbye!")
                break
            else:
                print("Invalid option. Please select a number from the menu.")
        except ValueError as ve:
            print("Value error:", ve)
        except KeyError as ke:
            print("Lookup error:", ke)
        except FileNotFoundError:
            print("File not found. Please check the filename and try again.")
        except Exception as e:
            print("An unexpected error occurred:", e)

if __name__ == "__main__":
    main_menu()
