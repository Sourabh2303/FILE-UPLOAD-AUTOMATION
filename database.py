import sqlite3
from pathlib import Path


# Path to the existing SQLite database
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR.parent / "assignment.db"
print(DB_PATH)
print(DB_PATH.exists())


def get_connection():
    """Create and return a SQLite database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_person(person_id):
    """Get a person from the master persons table."""
    conn = get_connection()

    person = conn.execute(
        """
        SELECT *
        FROM persons
        WHERE person_id = ?
        """,
        (person_id,)
    ).fetchone()

    conn.close()

    return person


def get_all_submissions():
    """Get all audio submissions."""
    conn = get_connection()

    submissions = conn.execute(
        """
        SELECT *
        FROM audio_submissions
        ORDER BY created_at DESC
        """
    ).fetchall()

    conn.close()

    return submissions