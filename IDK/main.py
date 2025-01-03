# gym_records_tool.py

import sqlite3
import os
import csv
from datetime import datetime

# Configuration
SETTINGS_FILE = "settings.py"
DEFAULT_DB_PATH = "gym_records.db"


# Load settings
def load_settings():
    if os.path.exists(SETTINGS_FILE):
        settings = {}
        with open(SETTINGS_FILE, "r") as f:
            exec(f.read(), settings)
        return settings
    return {"DB_PATH": DEFAULT_DB_PATH}


settings = load_settings()
DB_PATH = settings.get("DB_PATH", DEFAULT_DB_PATH)


# Database setup
def setup_database():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS exercises (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                weight INTEGER,
                sets INTEGER,
                reps INTEGER,
                date TEXT NOT NULL
            )
        """)
        conn.commit()


setup_database()


# Database operations
class GymRecords:
    """
    The GymRecords class provides an interface for interacting with the gym records database.

    Methods:
        add_exercise(name, weight, sets, reps, unit="kg"):
            Adds a new exercise record to the database.

        get_exercises(name=None):
            Retrieves exercises from the database, optionally filtered by name.

        export_to_csv(filename="gym_records.csv"):
            Exports all exercise records to a CSV file.
    """

    def __init__(self):
        """
        Initializes a new GymRecords object and connects to the database.
        """
        self.conn = sqlite3.connect(DB_PATH)

    def add_exercise(self, name, weight, sets, reps, unit="kg"):
        """
        Adds a new exercise record to the database.

        Parameters:
            name (str): The name of the exercise.
            weight (int): The weight used for the exercise.
            sets (int): The number of sets performed.
            reps (int): The number of repetitions per set.
            unit (str): The unit of weight (e.g., 'kg' or 'lb'). Default is 'kg'.
        """
        date = datetime.now().strftime("%Y-%m-%d")
        with self.conn:
            self.conn.execute(
                "INSERT INTO exercises (name, weight, sets, reps, date) VALUES (?, ?, ?, ?, ?)",
                (name, f"{weight} {unit}", sets, reps, date)
            )

    def get_exercises(self, name=None):
        """
        Retrieves exercises from the database.

        Parameters:
            name (str, optional): The name of the exercise to filter by. Defaults to None.

        Returns:
            list: A list of tuples containing exercise records.
        """
        query = "SELECT id, name, weight, sets, reps, date FROM exercises"
        params = []
        if name:
            query += " WHERE name LIKE ?"
            params.append(f"%{name}%")
        with self.conn:
            return self.conn.execute(query, params).fetchall()

    def export_to_csv(self, filename="gym_records.csv"):
        """
        Exports all exercise records to a CSV file.

        Parameters:
            filename (str): The name of the CSV file to create. Default is 'gym_records.csv'.
        """
        exercises = self.get_exercises()
        with open(filename, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Name", "Weight", "Sets", "Reps", "Date"])
            writer.writerows(exercises)


# Command-line interface
def main():
    print("Gym Records Tool")
    records = GymRecords()

    while True:
        print("\nOptions:")
        print("1. Add a new exercise")
        print("2. View exercises")
        print("3. Export to CSV")
        print("4. Exit")

        choice = input("Choose an option: ")

        if choice == "1":
            name = input("Exercise name: ")
            weight = int(input("Weight: "))
            unit = input("Unit (kg or lb): ").strip() or "kg"
            sets = int(input("Sets: "))
            reps = int(input("Reps: "))
            records.add_exercise(name, weight, sets, reps, unit)
            print("Exercise added.")
        elif choice == "2":
            name = input("Search by name (leave blank for all): ")
            exercises = records.get_exercises(name)
            for ex in exercises:
                print(ex)
        elif choice == "3":
            filename = input("Enter filename for export (default: gym_records.csv): ") or "gym_records.csv"
            records.export_to_csv(filename)
            print(f"Data exported to {filename}.")
        elif choice == "4":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
    main()
