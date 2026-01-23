import sqlite3
import json
from pathlib import Path
from typing import List, Optional
from datetime import datetime

if __name__ == "__main__":
    import sys
    sys.path.append(str(Path(__file__).parent.parent))
    from ai_gym_timetable_extractor.models import GymClass, GymSchedule
else:
    from .models import GymClass, GymSchedule


class GymScheduleDatabase:
    """Singleton database for managing gym schedule data with SQL query support."""
    
    _instance: Optional['GymScheduleDatabase'] = None
    _initialized: bool = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, db_path: Optional[str | Path] = None):
        """Initialize the database (only once due to singleton pattern).
        
        Args:
            db_path: Path to the SQLite database file. If None, defaults to data/db/gym_schedule.db
        """
        if not GymScheduleDatabase._initialized:
            self.conn: Optional[sqlite3.Connection] = None
            self.cursor: Optional[sqlite3.Cursor] = None
            self.db_path = self._get_db_path(db_path)
            self._create_database()
            GymScheduleDatabase._initialized = True
    
    def _get_db_path(self, db_path: Optional[str | Path] = None) -> Path:
        """Get the database file path, creating directories if needed.
        
        Args:
            db_path: Custom database path, or None to use default
            
        Returns:
            Path object for the database file
        """
        if db_path is None:
            # Default to data/db/gym_schedule.db
            if __name__ == "__main__":
                # Running as script
                base_path = Path(__file__).parent.parent.parent
            else:
                # Running as module
                base_path = Path.cwd()
            db_path = base_path / "data" / "db" / "gym_schedule.db"
        else:
            db_path = Path(db_path)
        
        # Create directory if it doesn't exist
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        return db_path
    
    def _create_database(self):
        """Create a SQLite database and set up the schema."""
        self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row  # Enable dict-like access to rows
        self.cursor = self.conn.cursor()
        
        # Create the gym_classes table based on GymClass model
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS gym_classes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                day_of_week TEXT NOT NULL,
                timeslot TEXT NOT NULL,
                activity TEXT NOT NULL,
                venue TEXT NOT NULL,
                class_type TEXT NOT NULL,
                vacancy INTEGER NOT NULL,
                modified_at TEXT NOT NULL,
                UNIQUE(date, timeslot, activity)
            )
        ''')
        
        # Create indexes for common query patterns
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_date ON gym_classes(date)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_activity ON gym_classes(activity)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_day_of_week ON gym_classes(day_of_week)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_timeslot ON gym_classes(timeslot)')
        
        self.conn.commit()
    
    def load_from_json(self, json_path: str | Path) -> int:
        """
        Load gym schedule data from a JSON file into the database.
        Uses upsert strategy: updates existing records (matched by date, timeslot, activity)
        or inserts new ones.
        
        Args:
            json_path: Path to the aggregated_schedule.json file
            
        Returns:
            Number of records loaded/updated
        """
        json_path = Path(json_path)
        
        if not json_path.exists():
            raise FileNotFoundError(f"JSON file not found: {json_path}")
        
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        # Validate and parse using Pydantic model
        schedule = GymSchedule(**data)
        
        # Upsert all classes (INSERT OR REPLACE)
        records_loaded = 0
        for gym_class in schedule.classes:
            self.cursor.execute('''
                INSERT OR REPLACE INTO gym_classes 
                (date, day_of_week, timeslot, activity, venue, class_type, vacancy, modified_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                gym_class.date,
                gym_class.day_of_week,
                gym_class.timeslot,
                gym_class.activity,
                gym_class.venue,
                gym_class.class_type,
                gym_class.vacancy,
                gym_class.modified_at.isoformat() if gym_class.modified_at else datetime.now().isoformat()
            ))
            records_loaded += 1
        
        self.conn.commit()
        return records_loaded
    
    def query(self, sql: str, params: tuple = ()) -> List[sqlite3.Row]:
        """
        Execute a SQL query and return results.
        
        Args:
            sql: SQL query string
            params: Query parameters (for parameterized queries)
            
        Returns:
            List of rows as sqlite3.Row objects (dict-like access)
        """
        self.cursor.execute(sql, params)
        return self.cursor.fetchall()
    
    def query_as_dict(self, sql: str, params: tuple = ()) -> List[dict]:
        """
        Execute a SQL query and return results as list of dictionaries.
        
        Args:
            sql: SQL query string
            params: Query parameters (for parameterized queries)
            
        Returns:
            List of dictionaries representing rows
        """
        rows = self.query(sql, params)
        return [dict(row) for row in rows]
    
    def query_as_models(self, sql: str, params: tuple = ()) -> List[GymClass]:
        """
        Execute a SQL query and return results as GymClass model instances.
        
        Args:
            sql: SQL query string
            params: Query parameters (for parameterized queries)
            
        Returns:
            List of GymClass model instances
        """
        rows = self.query_as_dict(sql, params)
        gym_classes = []
        for row in rows:
            # Remove the 'id' field as it's not part of GymClass model
            row.pop('id', None)
            # Convert modified_at string back to datetime
            if 'modified_at' in row and row['modified_at']:
                row['modified_at'] = datetime.fromisoformat(row['modified_at'])
            gym_classes.append(GymClass(**row))
        return gym_classes
    
    def execute(self, sql: str, params: tuple = ()) -> int:
        """
        Execute a SQL statement (INSERT, UPDATE, DELETE, etc.).
        
        Args:
            sql: SQL statement
            params: Statement parameters
            
        Returns:
            Number of rows affected
        """
        self.cursor.execute(sql, params)
        self.conn.commit()
        return self.cursor.rowcount
    
    def get_all_classes(self) -> List[GymClass]:
        """Get all gym classes as GymClass model instances."""
        return self.query_as_models('SELECT * FROM gym_classes ORDER BY date, timeslot')
    
    def get_classes_by_date(self, date: str) -> List[GymClass]:
        """Get all classes for a specific date."""
        return self.query_as_models(
            'SELECT * FROM gym_classes WHERE date = ? ORDER BY timeslot',
            (date,)
        )
    
    def get_classes_by_activity(self, activity: str) -> List[GymClass]:
        """Get all classes for a specific activity."""
        return self.query_as_models(
            'SELECT * FROM gym_classes WHERE activity LIKE ? ORDER BY date, timeslot',
            (f'%{activity}%',)
        )
    
    def get_classes_by_day_of_week(self, day: str) -> List[GymClass]:
        """Get all classes for a specific day of the week."""
        return self.query_as_models(
            'SELECT * FROM gym_classes WHERE day_of_week LIKE ? ORDER BY timeslot',
            (f'%{day}%',)
        )
    
    def get_classes_with_vacancy(self, min_vacancy: int = 1) -> List[GymClass]:
        """Get all classes with available spots."""
        return self.query_as_models(
            'SELECT * FROM gym_classes WHERE vacancy >= ? ORDER BY date, timeslot',
            (min_vacancy,)
        )
    
    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None
    
    @classmethod
    def reset_instance(cls):
        """Reset the singleton instance (useful for testing)."""
        if cls._instance and cls._instance.conn:
            cls._instance.close()
        cls._instance = None
        cls._initialized = False


# Convenience function to get the singleton instance
def get_database() -> GymScheduleDatabase:
    """Get the singleton database instance."""
    return GymScheduleDatabase()


if __name__ == "__main__":
    # Example usage
    db = get_database()
    
    # Load data from JSON
    json_file = Path(__file__).parent.parent.parent / "data" / "aggregated" / "aggregated_schedule.json"
    if json_file.exists():
        count = db.load_from_json(json_file)
        print(f"Loaded {count} classes into database")
        
        # Example queries
        print("\n--- All Yoga classes ---")
        yoga_classes = db.get_classes_by_activity("Yoga")
        for cls in yoga_classes[:3]:  # Show first 3
            print(f"{cls.date} {cls.timeslot} - {cls.activity} ({cls.vacancy} spots)")
        
        print("\n--- Classes on 2026-01-19 ---")
        monday_classes = db.get_classes_by_date("2026-01-19")
        for cls in monday_classes[:3]:  # Show first 3
            print(f"{cls.timeslot} - {cls.activity} ({cls.vacancy} spots)")
        
        print("\n--- Custom SQL Query ---")
        results = db.query_as_dict(
            "SELECT activity, COUNT(*) as count FROM gym_classes GROUP BY activity ORDER BY count DESC LIMIT 5"
        )
        for row in results:
            print(f"{row['activity']}: {row['count']} classes")
    else:
        print(f"JSON file not found at {json_file}")
