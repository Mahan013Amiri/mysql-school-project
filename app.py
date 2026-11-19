import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
    )


def list_students(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email, age, phone FROM students")
    for row in cursor.fetchall():
        print(row)
    cursor.close()


def add_student(conn):
    name = input("Name: ").strip()
    email = input("Email: ").strip() or None
    age = input("Age: ").strip()
    phone = input("Phone: ").strip() or None
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO students (name, email, age, phone) VALUES (%s, %s, %s, %s)",
            (name, email, int(age) if age else None, phone),
        )
        conn.commit()
        print("Student added.")
    except mysql.connector.Error as err:
        conn.rollback()
        print("Error:", err)
    finally:
        cursor.close()


def update_email(conn):
    student_id = input("Student id: ").strip()
    email = input("New email: ").strip()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE students SET email = %s WHERE id = %s", (email, int(student_id))
        )
        conn.commit()
        print(cursor.rowcount, "row(s) updated.")
    except mysql.connector.Error as err:
        conn.rollback()
        print("Error:", err)
    finally:
        cursor.close()


def delete_student(conn):
    student_id = input("Student id: ").strip()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM students WHERE id = %s", (int(student_id),))
        conn.commit()
        print(cursor.rowcount, "row(s) deleted.")
    except mysql.connector.Error as err:
        conn.rollback()
        print("Error:", err)
    finally:
        cursor.close()


def main():
    conn = get_connection()
    actions = {
        "1": list_students,
        "2": add_student,
        "3": update_email,
        "4": delete_student,
    }
    try:
        while True:
            print("\n1) List  2) Add  3) Update email  4) Delete  0) Exit")
            choice = input("Choose: ").strip()
            if choice == "0":
                break
            action = actions.get(choice)
            if action:
                action(conn)
            else:
                print("Invalid choice.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()