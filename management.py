
import json
import os
import shutil
from datetime import datetime

FILE = "students_database.json"
BACKUP = "students_backup.json"


# ---------- DATABASE ----------

def load_data():
    if os.path.exists(FILE):
        try:
            with open(FILE, "r", encoding="utf-8") as f:
                data = json.load(f)

            data.setdefault("students", [])
            data.setdefault("history", [])
            data.setdefault("next_id", 1001)
            return data

        except (json.JSONDecodeError, OSError):
            print("Database could not be loaded!")

    return {
        "students": [],
        "history": [],
        "next_id": 1001
    }


def save_data(data):
    try:
        with open(FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        return True
    except OSError:
        print("Error saving database!")
        return False


def log_action(data, message):
    data["history"].append({
        "message": message,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })


def find_student(data, student_id):
    for student in data["students"]:
        if student["id"] == student_id:
            return student
    return None


def get_student_id():
    try:
        return int(input("Enter student ID: "))
    except ValueError:
        print("Please enter a valid numeric ID!")
        return None


# ---------- STUDENT MANAGEMENT ----------

def add_student(data):
    print("\n--- ADD STUDENT ---")

    name = input("Full name: ").strip()
    if not name:
        print("Name is required!")
        return

    age_text = input("Age: ").strip()
    course = input("Course: ").strip()
    student_class = input("Class/Year: ").strip()
    phone = input("Phone number: ").strip()
    email = input("Email: ").strip()
    address = input("Address: ").strip()

    try:
        age = int(age_text)
        if age <= 0:
            print("Age must be positive!")
            return
    except ValueError:
        print("Invalid age!")
        return

    if not course or not student_class:
        print("Course and class are required!")
        return

    if phone and not phone.isdigit():
        print("Phone must contain digits only!")
        return

    student = {
        "id": data["next_id"],
        "name": name,
        "age": age,
        "course": course,
        "class": student_class,
        "phone": phone,
        "email": email,
        "address": address,
        "marks": {},
        "attendance": {
            "present": 0,
            "total": 0
        },
        "fees": {
            "total": 0.0,
            "paid": 0.0
        },
        "created": datetime.now().strftime("%Y-%m-%d"),
        "active": True
    }

    data["students"].append(student)
    data["next_id"] += 1

    log_action(data, f"Added student: {name}")
    if save_data(data):
        print("Student added successfully!")
        print("Student ID:", student["id"])


def display_student(student):
    print("\n" + "-" * 45)
    print("STUDENT ID :", student["id"])
    print("Name       :", student["name"])
    print("Age        :", student["age"])
    print("Course     :", student["course"])
    print("Class/Year :", student["class"])
    print("Phone      :", student["phone"])
    print("Email      :", student["email"])
    print("Address    :", student["address"])
    print("Status     :", "Active" if student["active"] else "Inactive")
    print("Marks      :", student["marks"])
    print("-" * 45)


def view_students(data):
    students = data["students"]

    if not students:
        print("No student records found!")
        return

    for student in students:
        display_student(student)


def search_student(data):
    query = input("Search by ID, name, course or class: ")
    query = query.strip().lower()

    if not query:
        print("Enter a search term!")
        return

    results = []

    for student in data["students"]:
        fields = [
            str(student["id"]),
            student["name"],
            student["course"],
            student["class"],
            student["email"]
        ]

        if any(query in field.lower() for field in fields):
            results.append(student)

    if results:
        for student in results:
            display_student(student)
    else:
        print("No matching student found!")


def update_student(data):
    student_id = get_student_id()
    if student_id is None:
        return

    student = find_student(data, student_id)

    if not student:
        print("Student not found!")
        return

    print("Press Enter to keep the old value.")

    fields = ["name", "course", "class", "phone", "email", "address"]

    for field in fields:
        value = input(f"{field.title()} [{student[field]}]: ").strip()

        if value:
            if field == "phone" and not value.isdigit():
                print("Invalid phone number; keeping old value.")
                continue
            student[field] = value

    age = input(f"Age [{student['age']}]: ").strip()

    if age:
        try:
            new_age = int(age)
            if new_age <= 0:
                raise ValueError
            student["age"] = new_age
        except ValueError:
            print("Invalid age; keeping old value.")

    log_action(data, f"Updated student ID {student_id}")
    if save_data(data):
        print("Student updated successfully!")


def delete_student(data):
    student_id = get_student_id()
    if student_id is None:
        return

    student = find_student(data, student_id)

    if not student:
        print("Student not found!")
        return

    confirm = input("Type YES to deactivate this student: ")

    if confirm.strip() == "YES":
        student["active"] = False
        log_action(data, f"Deactivated student ID {student_id}")
        if save_data(data):
            print("Student deactivated.")
    else:
        print("Operation cancelled.")


def sort_students(data):
    print("1. Sort by name")
    print("2. Sort by age")
    print("3. Sort by student ID")
    print("4. Sort by course")

    choice = input("Choose: ")

    keys = {
        "1": lambda s: s["name"].lower(),
        "2": lambda s: s["age"],
        "3": lambda s: s["id"],
        "4": lambda s: s["course"].lower()
    }

    if choice not in keys:
        print("Invalid choice!")
        return

    for student in sorted(data["students"], key=keys[choice]):
        display_student(student)


# ---------- MARKS AND RESULTS ----------

def add_marks(data):
    student_id = get_student_id()
    if student_id is None:
        return

    student = find_student(data, student_id)

    if not student:
        print("Student not found!")
        return

    subject = input("Subject name: ").strip()

    if not subject:
        print("Subject is required!")
        return

    try:
        marks = float(input("Marks obtained (0-100): "))

        if not 0 <= marks <= 100:
            print("Marks must be between 0 and 100!")
            return

    except ValueError:
        print("Enter numeric marks!")
        return

    student["marks"][subject] = marks
    log_action(data, f"Added marks for {student['name']}")
    if save_data(data):
        print("Marks saved!")


def calculate_result(student):
    marks = student["marks"]

    if not marks:
        print("No marks recorded!")
        return

    average = sum(marks.values()) / len(marks)

    if average >= 90:
        grade = "A+"
    elif average >= 80:
        grade = "A"
    elif average >= 70:
        grade = "B"
    elif average >= 60:
        grade = "C"
    elif average >= 40:
        grade = "D"
    else:
        grade = "F"

    print("\n--- REPORT CARD ---")
    print("Student:", student["name"])
    print("ID:", student["id"])

    for subject, score in marks.items():
        print(f"{subject}: {score}/100")

    print("Percentage:", round(average, 2), "%")
    print("Grade:", grade)
    print("Result:", "Pass" if average >= 40 else "Fail")


def show_result(data):
    student_id = get_student_id()
    if student_id is None:
        return

    student = find_student(data, student_id)

    if student:
        calculate_result(student)
    else:
        print("Student not found!")


def topper_list(data):
    ranked = []

    for student in data["students"]:
        if student["active"] and student["marks"]:
            average = sum(student["marks"].values()) / len(student["marks"])
            ranked.append((average, student))

    ranked.sort(key=lambda item: item[0], reverse=True)

    if not ranked:
        print("No marks available!")
        return

    print("\n--- TOP 10 STUDENTS ---")

    for position, (average, student) in enumerate(ranked[:10], 1):
        print(
            position,
            student["name"],
            "-",
            round(average, 2),
            "%"
        )


# ---------- ATTENDANCE ----------

def mark_attendance(data):
    student_id = get_student_id()
    if student_id is None:
        return

    student = find_student(data, student_id)

    if not student or not student["active"]:
        print("Active student not found!")
        return

    present = input("Was the student present? (yes/no): ").lower()

    if present not in ("yes", "no"):
        print("Enter yes or no!")
        return

    student["attendance"]["total"] += 1

    if present == "yes":
        student["attendance"]["present"] += 1

    log_action(data, f"Attendance updated for {student['name']}")
    if save_data(data):
        print("Attendance recorded!")


def attendance_report(data):
    student_id = get_student_id()
    if student_id is None:
        return

    student = find_student(data, student_id)

    if not student:
        print("Student not found!")
        return

    attendance = student["attendance"]
    total = attendance["total"]
    present = attendance["present"]

    percentage = (present / total * 100) if total else 0

    print("Student:", student["name"])
    print("Present:", present)
    print("Total Classes:", total)
    print("Attendance:", round(percentage, 2), "%")

    if total == 0:
        print("No attendance recorded yet.")
    elif percentage < 75:
        print("Attendance is below 75%.")
    else:
        print("Attendance is 75% or above.")


# ---------- FEES MANAGEMENT ----------

def set_fees(data):
    student_id = get_student_id()
    if student_id is None:
        return

    student = find_student(data, student_id)

    if not student:
        print("Student not found!")
        return

    try:
        total = float(input("Total course fee: "))

        if total < student["fees"]["paid"] or total < 0:
            print("Total fee cannot be below amount already paid!")
            return

    except ValueError:
        print("Invalid amount!")
        return

    student["fees"]["total"] = total
    log_action(data, f"Fee set for {student['name']}")
    if save_data(data):
        print("Course fee updated!")


def pay_fees(data):
    student_id = get_student_id()
    if student_id is None:
        return

    student = find_student(data, student_id)

    if not student:
        print("Student not found!")
        return

    fees = student["fees"]
    due = fees["total"] - fees["paid"]

    if due <= 0:
        print("No fees due.")
        return

    try:
        amount = float(input(f"Amount to pay (due Rs. {due}): "))

        if amount <= 0 or amount > due:
            print("Enter a positive amount not exceeding the due fee!")
            return

    except ValueError:
        print("Invalid amount!")
        return

    fees["paid"] = round(fees["paid"] + amount, 2)
    log_action(data, f"Fee payment recorded for {student['name']}")

    if save_data(data):
        print("Payment recorded!")
        print("Remaining fees: Rs.", round(fees["total"] - fees["paid"], 2))


def fee_report(data):
    student_id = get_student_id()
    if student_id is None:
        return

    student = find_student(data, student_id)

    if not student:
        print("Student not found!")
        return

    fees = student["fees"]

    print("\n--- FEE REPORT ---")
    print("Student:", student["name"])
    print("Total Fee: Rs.", fees["total"])
    print("Paid: Rs.", fees["paid"])
    print("Remaining: Rs.", round(fees["total"] - fees["paid"], 2))


def pending_fees(data):
    print("\n--- PENDING FEES ---")
    found = False

    for student in data["students"]:
        fees = student["fees"]
        due = fees["total"] - fees["paid"]

        if student["active"] and due > 0:
            print(
                student["id"],
                student["name"],
                "- Due Rs.",
                round(due, 2)
            )
            found = True

    if not found:
        print("No pending fees!")


# ---------- REPORTS AND UTILITIES ----------

def class_statistics(data):
    students = [
        student for student in data["students"]
        if student["active"]
    ]

    print("\n--- CLASS STATISTICS ---")
    print("Total Active Students:", len(students))

    courses = {}

    for student in students:
        course = student["course"]
        courses[course] = courses.get(course, 0) + 1

    print("\nStudents by Course:")

    for course, count in sorted(courses.items()):
        print(f"{course}: {count}")

    total_marks = [
        sum(student["marks"].values()) / len(student["marks"])
        for student in students if student["marks"]
    ]

    if total_marks:
        print("Overall Average:", round(sum(total_marks) / len(total_marks), 2), "%")


def history_report(data):
    print("\n--- RECENT ACTIVITY ---")

    for entry in reversed(data["history"][-20:]):
        print(entry["time"], "-", entry["message"])

    if not data["history"]:
        print("No activity recorded.")


def backup_database(data):
    if not save_data(data):
        return

    try:
        shutil.copy2(FILE, BACKUP)
        print("Backup created:", BACKUP)
    except OSError:
        print("Backup failed!")


def restore_backup(data):
    if not os.path.exists(BACKUP):
        print("No backup found!")
        return

    confirm = input("Type RESTORE to replace current data: ")

    if confirm != "RESTORE":
        print("Restore cancelled.")
        return

    try:
        with open(BACKUP, "r", encoding="utf-8") as file:
            backup_data = json.load(file)

        if not all(
            key in backup_data
            for key in ("students", "history", "next_id")
        ):
            print("Backup format is invalid!")
            return

        data.clear()
        data.update(backup_data)

        if save_data(data):
            print("Backup restored successfully!")

    except (json.JSONDecodeError, OSError):
        print("Could not restore backup!")


# ---------- MENU ----------

def show_menu():
    print("\n" + "=" * 45)
    print("      STUDENT MANAGEMENT SYSTEM")
    print("=" * 45)
    print(" 1. Add Student")
    print(" 2. View All Students")
    print(" 3. Search Student")
    print(" 4. Update Student")
    print(" 5. Deactivate Student")
    print(" 6. Sort Students")
    print(" 7. Add/Update Marks")
    print(" 8. View Report Card")
    print(" 9. Topper List")
    print("10. Mark Attendance")
    print("11. Attendance Report")
    print("12. Set Course Fees")
    print("13. Record Fee Payment")
    print("14. Individual Fee Report")
    print("15. Pending Fee Report")
    print("16. Class Statistics")
    print("17. Activity History")
    print("18. Backup Database")
    print("19. Restore Backup")
    print(" 0. Save and Exit")
    print("=" * 45)


def main():
    data = load_data()

    actions = {
        "1": add_student,
        "2": view_students,
        "3": search_student,
        "4": update_student,
        "5": delete_student,
        "6": sort_students,
        "7": add_marks,
        "8": show_result,
        "9": topper_list,
        "10": mark_attendance,
        "11": attendance_report,
        "12": set_fees,
        "13": pay_fees,
        "14": fee_report,
        "15": pending_fees,
        "16": class_statistics,
        "17": history_report,
        "18": backup_database,
        "19": restore_backup
    }

    print("Welcome to Student Management System!")

    while True:
        show_menu()
        choice = input("Enter your choice: ").strip()

        if choice == "0":
            if save_data(data):
                print("Data saved. Goodbye!")
                break
        elif choice in actions:
            try:
                actions[choice](data)
            except (KeyError, TypeError, ValueError) as error:
                print("Operation failed:", error)
        else:
            print("Invalid choice! Try again.")


if __name__ == "__main__":
    main()
