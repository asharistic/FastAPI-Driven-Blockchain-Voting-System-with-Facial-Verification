import os
import sqlite3
from datetime import datetime

# Database URL (path) handling
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./backend/voting_system.db")


def _extract_sqlite_path(url: str) -> str:
    # Expect formats like sqlite:///C:/path/db.sqlite or sqlite:///./backend/voting_system.db
    if not url.startswith("sqlite:///"):
        # Fallback to file path as-is
        return url
    return url.replace("sqlite:///", "")


DB_PATH = _extract_sqlite_path(DATABASE_URL)


def get_connection() -> sqlite3.Connection:
    # Ensure parent directory exists for the SQLite file path
    parent_dir = os.path.dirname(DB_PATH)
    if parent_dir and not os.path.exists(parent_dir):
        os.makedirs(parent_dir, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_connection()
    cur = conn.cursor()
    # Create tables if not exist
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS elections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            is_active INTEGER DEFAULT 1,
            created_at TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS voters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            voter_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            face_data BLOB,
            has_voted INTEGER DEFAULT 0,
            registered_at TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            party TEXT,
            election_id INTEGER,
            image_url TEXT,
            bio TEXT
        )
        """
    )
    conn.commit()
    conn.close()


# ---------- Candidate helpers ----------
def list_candidates() -> list[dict]:
    conn = get_connection()
    rows = conn.execute("SELECT candidate_id, name, party, election_id, image_url, bio FROM candidates").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_candidate_by_candidate_id(candidate_id: str) -> dict | None:
    conn = get_connection()
    row = conn.execute("SELECT * FROM candidates WHERE candidate_id = ?", (candidate_id,)).fetchone()
    conn.close()
    if row:
        # Convert sqlite3.Row to dict with proper key access
        return {key: row[key] for key in row.keys()}
    return None


def create_candidate(candidate: dict) -> None:
    conn = get_connection()
    conn.execute(
        "INSERT INTO candidates (candidate_id, name, party, election_id, image_url, bio) VALUES (?, ?, ?, ?, ?, ?)",
        (
            candidate.get("candidate_id"),
            candidate.get("name"),
            candidate.get("party"),
            candidate.get("election_id"),
            candidate.get("image_url"),
            candidate.get("bio"),
        ),
    )
    conn.commit()
    conn.close()


def update_candidate(candidate_id: str, fields: dict) -> bool:
    if not fields:
        return True
    keys = list(fields.keys())
    values = [fields[k] for k in keys]
    set_clause = ", ".join([f"{k} = ?" for k in keys])
    conn = get_connection()
    cur = conn.execute(f"UPDATE candidates SET {set_clause} WHERE candidate_id = ?", (*values, candidate_id))
    conn.commit()
    conn.close()
    return cur.rowcount > 0


def delete_candidate(candidate_id: str) -> bool:
    conn = get_connection()
    cur = conn.execute("DELETE FROM candidates WHERE candidate_id = ?", (candidate_id,))
    conn.commit()
    conn.close()
    return cur.rowcount > 0


# ---------- Voter helpers ----------
def list_voters() -> list[dict]:
    conn = get_connection()
    rows = conn.execute("SELECT voter_id, name, has_voted, registered_at FROM voters").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def list_voters_with_faces() -> list[dict]:
    """Get all voters with their face data (for face comparison)"""
    conn = get_connection()
    rows = conn.execute("SELECT voter_id, name, face_data, has_voted FROM voters WHERE face_data IS NOT NULL").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_voter_by_voter_id(voter_id: str) -> dict | None:
    conn = get_connection()
    row = conn.execute("SELECT * FROM voters WHERE voter_id = ?", (voter_id,)).fetchone()
    conn.close()
    if row:
        # Convert sqlite3.Row to dict with proper key access
        return {key: row[key] for key in row.keys()}
    return None


def create_voter(voter_id: str, name: str, face_data: bytes | None) -> None:
    conn = get_connection()
    conn.execute(
        "INSERT INTO voters (voter_id, name, face_data, has_voted, registered_at) VALUES (?, ?, ?, 0, ?)",
        (voter_id, name, face_data, datetime.utcnow().isoformat()),
    )
    conn.commit()
    conn.close()


def set_voter_has_voted(voter_id: str) -> None:
    conn = get_connection()
    conn.execute("UPDATE voters SET has_voted = 1 WHERE voter_id = ?", (voter_id,))
    conn.commit()
    conn.close()


def update_voter(voter_id: str, fields: dict) -> bool:
    if not fields:
        return True
    keys = list(fields.keys())
    values = [fields[k] for k in keys]
    set_clause = ", ".join([f"{k} = ?" for k in keys])
    conn = get_connection()
    cur = conn.execute(f"UPDATE voters SET {set_clause} WHERE voter_id = ?", (*values, voter_id))
    conn.commit()
    conn.close()
    return cur.rowcount > 0


def delete_voter(voter_id: str) -> bool:
    conn = get_connection()
    cur = conn.execute("DELETE FROM voters WHERE voter_id = ?", (voter_id,))
    conn.commit()
    conn.close()
    return cur.rowcount > 0


# ---------- Election helpers ----------
def create_election(election: dict) -> int:
    conn = get_connection()
    cur = conn.execute(
        "INSERT INTO elections (title, description, start_time, end_time, is_active, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (
            election.get("title"),
            election.get("description"),
            election.get("start_time"),
            election.get("end_time"),
            1 if election.get("is_active", True) else 0,
            datetime.utcnow().isoformat(),
        ),
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id


def list_elections() -> list[dict]:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM elections").fetchall()
    conn.close()
    # Convert booleans and datetime strings consistently
    return [dict(r) for r in rows]


def get_election_by_id(election_id: int) -> dict | None:
    conn = get_connection()
    row = conn.execute("SELECT * FROM elections WHERE id = ?", (election_id,)).fetchone()
    conn.close()
    if row:
        # Convert sqlite3.Row to dict with proper key access
        return {key: row[key] for key in row.keys()}
    return None


def update_election(election_id: int, fields: dict) -> bool:
    if not fields:
        return True
    keys = list(fields.keys())
    values = [fields[k] for k in keys]
    set_clause = ", ".join([f"{k} = ?" for k in keys])
    conn = get_connection()
    cur = conn.execute(f"UPDATE elections SET {set_clause} WHERE id = ?", (*values, election_id))
    conn.commit()
    conn.close()
    return cur.rowcount > 0


def delete_election(election_id: int) -> bool:
    conn = get_connection()
    cur = conn.execute("DELETE FROM elections WHERE id = ?", (election_id,))
    conn.commit()
    conn.close()
    return cur.rowcount > 0


# ---------- Stats helpers ----------
def count(table: str) -> int:
    conn = get_connection()
    row = conn.execute(f"SELECT COUNT(*) as c FROM {table}").fetchone()
    conn.close()
    return int(row[0]) if row else 0
