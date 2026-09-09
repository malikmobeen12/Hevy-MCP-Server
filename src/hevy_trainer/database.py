import csv
import sqlite3
from pathlib import Path
from typing import List, Dict, Any

class HevyDatabase:
    """
    Manages an in-memory SQLite database populated from a Hevy workouts CSV export.
    """
    def __init__(self, csv_path: str | Path):
        self.csv_path = Path(csv_path)
        self.conn = sqlite3.connect(':memory:', check_same_thread=False)
        self._create_tables()

    def _create_tables(self) -> None:
        """Initialize the database schema."""
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE workouts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                start_time TEXT,
                end_time TEXT,
                description TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE exercises (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workout_id INTEGER,
                title TEXT,
                superset_id TEXT,
                notes TEXT,
                FOREIGN KEY(workout_id) REFERENCES workouts(id)
            )
        ''')
        cursor.execute('''
            CREATE TABLE sets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                exercise_id INTEGER,
                set_index INTEGER,
                set_type TEXT,
                weight_kg REAL,
                reps INTEGER,
                rpe REAL,
                FOREIGN KEY(exercise_id) REFERENCES exercises(id)
            )
        ''')
        self.conn.commit()

    def load(self) -> bool:
        """
        Load the CSV file into the SQLite database.
        Returns True if successful, False if the file does not exist.
        """
        if not self.csv_path.exists():
            return False
            
        with open(self.csv_path, mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            cursor = self.conn.cursor()
            
            current_workout_time = None
            current_workout_id = None
            current_exercise_title = None
            current_exercise_id = None
            
            for row in reader:
                # Insert workout if new start_time
                if row['start_time'] != current_workout_time:
                    cursor.execute('''
                        INSERT INTO workouts (title, start_time, end_time, description)
                        VALUES (?, ?, ?, ?)
                    ''', (row['title'], row['start_time'], row['end_time'], row['description']))
                    current_workout_id = cursor.lastrowid
                    current_workout_time = row['start_time']
                    current_exercise_title = None
                    
                # Insert exercise if new exercise in this workout
                if row['exercise_title'] != current_exercise_title:
                    cursor.execute('''
                        INSERT INTO exercises (workout_id, title, superset_id, notes)
                        VALUES (?, ?, ?, ?)
                    ''', (current_workout_id, row['exercise_title'], row['superset_id'], row['exercise_notes']))
                    current_exercise_id = cursor.lastrowid
                    current_exercise_title = row['exercise_title']
                    
                # Insert set
                cursor.execute('''
                    INSERT INTO sets (exercise_id, set_index, set_type, weight_kg, reps, rpe)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    current_exercise_id,
                    int(row['set_index']) if row['set_index'] else 0,
                    row['set_type'],
                    float(row['weight_kg']) if row['weight_kg'] else 0.0,
                    int(row['reps']) if row['reps'] else 0,
                    float(row['rpe']) if row['rpe'] else 0.0
                ))
                
        self.conn.commit()
        return True

    def get_schema(self) -> str:
        """Returns the schema of the loaded database for LLM context."""
        return """
        Table: workouts
        Columns: id (INTEGER), title (TEXT), start_time (TEXT), end_time (TEXT), description (TEXT)

        Table: exercises
        Columns: id (INTEGER), workout_id (INTEGER), title (TEXT), superset_id (TEXT), notes (TEXT)

        Table: sets
        Columns: id (INTEGER), exercise_id (INTEGER), set_index (INTEGER), set_type (TEXT), weight_kg (REAL), reps (INTEGER), rpe (REAL)
        """

    def query(self, sql: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """
        Execute a read-only SQL SELECT query against the database.
        
        Args:
            sql: The SQL query to execute.
            params: Optional tuple of parameters to bind to the query.
            
        Returns:
            A list of dictionaries representing the rows.
        """
        self.conn.row_factory = sqlite3.Row
        cursor = self.conn.cursor()
        cursor.execute(sql, params)
        return [dict(row) for row in cursor.fetchall()]
