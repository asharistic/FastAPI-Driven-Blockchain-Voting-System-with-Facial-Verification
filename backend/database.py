import os
import psycopg
from psycopg.rows import dict_row
from datetime import datetime
from contextlib import contextmanager

# Database URL - PostgreSQL connection string
# Format: postgresql://user:password@host:port/database
# Example: postgresql://postgres:password@localhost:5432/voting_system
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres:postgres@localhost:5432/voting_system"
)


@contextmanager
def get_connection():
    """Context manager for database connections"""
    conn = psycopg.connect(DATABASE_URL)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    """Initialize database tables"""
    with get_connection() as conn:
        cur = conn.cursor()
        # Create tables if not exist
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS elections (
                id SERIAL PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                start_time TIMESTAMP NOT NULL,
                end_time TIMESTAMP NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS voters (
                id SERIAL PRIMARY KEY,
                voter_id VARCHAR(255) UNIQUE NOT NULL,
                name VARCHAR(255) NOT NULL,
                face_embedding JSONB,
                has_voted BOOLEAN DEFAULT FALSE,
                registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS candidates (
                id SERIAL PRIMARY KEY,
                candidate_id VARCHAR(255) UNIQUE NOT NULL,
                name VARCHAR(255) NOT NULL,
                party VARCHAR(255),
                election_id INTEGER,
                image_url TEXT,
                bio TEXT
            )
            """
        )
        conn.commit()


# ---------- Candidate helpers ----------
def list_candidates() -> list[dict]:
    with get_connection() as conn:
        cur = conn.cursor(row_factory=dict_row)
        cur.execute("SELECT candidate_id, name, party, election_id, image_url, bio FROM candidates")
        rows = cur.fetchall()
        return [dict(r) for r in rows]


def get_candidate_by_candidate_id(candidate_id: str) -> dict | None:
    with get_connection() as conn:
        cur = conn.cursor(row_factory=dict_row)
        cur.execute("SELECT * FROM candidates WHERE candidate_id = %s", (candidate_id,))
        row = cur.fetchone()
        if row:
            return dict(row)
        return None


def create_candidate(candidate: dict) -> None:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO candidates (candidate_id, name, party, election_id, image_url, bio) VALUES (%s, %s, %s, %s, %s, %s)",
            (
                candidate.get("candidate_id"),
                candidate.get("name"),
                candidate.get("party"),
                candidate.get("election_id"),
                candidate.get("image_url"),
                candidate.get("bio"),
            ),
        )


def update_candidate(candidate_id: str, fields: dict) -> bool:
    if not fields:
        return True
    keys = list(fields.keys())
    values = [fields[k] for k in keys]
    set_clause = ", ".join([f"{k} = %s" for k in keys])
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(f"UPDATE candidates SET {set_clause} WHERE candidate_id = %s", (*values, candidate_id))
        return cur.rowcount > 0


def delete_candidate(candidate_id: str) -> bool:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM candidates WHERE candidate_id = %s", (candidate_id,))
        return cur.rowcount > 0


# ---------- Voter helpers ----------
def list_voters() -> list[dict]:
    with get_connection() as conn:
        cur = conn.cursor(row_factory=dict_row)
        cur.execute("SELECT voter_id, name, has_voted, registered_at FROM voters")
        rows = cur.fetchall()
        return [dict(r) for r in rows]


def list_voters_with_faces() -> list[dict]:
    """Get all voters with their face embeddings (for face comparison)"""
    with get_connection() as conn:
        cur = conn.cursor(row_factory=dict_row)
        cur.execute("SELECT voter_id, name, face_embedding, has_voted FROM voters WHERE face_embedding IS NOT NULL")
        rows = cur.fetchall()
        return [dict(r) for r in rows]


def get_voter_by_voter_id(voter_id: str) -> dict | None:
    with get_connection() as conn:
        cur = conn.cursor(row_factory=dict_row)
        cur.execute("SELECT * FROM voters WHERE voter_id = %s", (voter_id,))
        row = cur.fetchone()
        if row:
            return dict(row)
        return None


def create_voter(voter_id: str, name: str, face_embedding: list | None) -> None:
    """
    Create a new voter with face embedding
    face_embedding: List of floats representing the face embedding vector
    """
    import json
    with get_connection() as conn:
        cur = conn.cursor()
        # Convert embedding list to JSON for storage in JSONB column
        embedding_json = json.dumps(face_embedding) if face_embedding else None
        cur.execute(
            "INSERT INTO voters (voter_id, name, face_embedding, has_voted, registered_at) VALUES (%s, %s, %s::jsonb, %s, %s)",
            (voter_id, name, embedding_json, False, datetime.utcnow()),
        )


def set_voter_has_voted(voter_id: str) -> None:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("UPDATE voters SET has_voted = TRUE WHERE voter_id = %s", (voter_id,))


def update_voter(voter_id: str, fields: dict) -> bool:
    if not fields:
        return True
    keys = list(fields.keys())
    values = [fields[k] for k in keys]
    set_clause = ", ".join([f"{k} = %s" for k in keys])
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(f"UPDATE voters SET {set_clause} WHERE voter_id = %s", (*values, voter_id))
        return cur.rowcount > 0


def delete_voter(voter_id: str) -> bool:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM voters WHERE voter_id = %s", (voter_id,))
        return cur.rowcount > 0


# ---------- Election helpers ----------
def create_election(election: dict) -> int:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO elections (title, description, start_time, end_time, is_active, created_at) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id",
            (
                election.get("title"),
                election.get("description"),
                election.get("start_time"),
                election.get("end_time"),
                election.get("is_active", True),
                datetime.utcnow(),
            ),
        )
        new_id = cur.fetchone()[0]
        return new_id


def list_elections() -> list[dict]:
    with get_connection() as conn:
        cur = conn.cursor(row_factory=dict_row)
        cur.execute("SELECT * FROM elections")
        rows = cur.fetchall()
        return [dict(r) for r in rows]


def get_election_by_id(election_id: int) -> dict | None:
    with get_connection() as conn:
        cur = conn.cursor(row_factory=dict_row)
        cur.execute("SELECT * FROM elections WHERE id = %s", (election_id,))
        row = cur.fetchone()
        if row:
            return dict(row)
        return None


def update_election(election_id: int, fields: dict) -> bool:
    if not fields:
        return True
    keys = list(fields.keys())
    values = [fields[k] for k in keys]
    set_clause = ", ".join([f"{k} = %s" for k in keys])
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(f"UPDATE elections SET {set_clause} WHERE id = %s", (*values, election_id))
        return cur.rowcount > 0


def delete_election(election_id: int) -> bool:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM elections WHERE id = %s", (election_id,))
        return cur.rowcount > 0


# ---------- Stats helpers ----------
def count(table: str) -> int:
    with get_connection() as conn:
        cur = conn.cursor()
        # Use parameterized query to prevent SQL injection
        cur.execute(f"SELECT COUNT(*) as c FROM {table}")
        row = cur.fetchone()
        return int(row[0]) if row else 0
