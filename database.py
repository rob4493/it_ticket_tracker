import sqlite3
from datetime import datetime
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "tickets.db"
SCHEMA_PATH = BASE_DIR / "schema.sql"


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with get_connection() as connection:
        connection.executescript(SCHEMA_PATH.read_text())


def create_ticket(ticket, priority_suggestion):
    timestamp = datetime.now().isoformat(timespec="seconds")

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO tickets (
              requester_name,
              requester_email,
              requester_employee_id,
              department,
              issue_type,
              user_selected_priority,
              suggested_priority,
              priority_reason,
              final_priority,
              description,
              status,
              created_at,
              updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                ticket["name"],
                ticket["email"],
                ticket["employee_id"],
                ticket["department"],
                ticket["issue_type"],
                ticket["priority"],
                priority_suggestion["priority"],
                priority_suggestion["reason"],
                ticket["priority"],
                ticket["description"],
                "Open",
                timestamp,
                timestamp,
            ),
        )
        ticket_id = cursor.lastrowid
        ticket_number = generate_ticket_number(ticket_id, timestamp)
        connection.execute(
            "UPDATE tickets SET ticket_number = ? WHERE id = ?",
            (ticket_number, ticket_id),
        )
        connection.commit()

    return get_ticket_by_id(ticket_id)


def get_ticket_by_id(ticket_id):
    with get_connection() as connection:
        return connection.execute(
            "SELECT * FROM tickets WHERE id = ?",
            (ticket_id,),
        ).fetchone()


def get_all_tickets():
    with get_connection() as connection:
        return connection.execute(
            """
            SELECT *
            FROM tickets
            ORDER BY
              CASE status
                WHEN 'Open' THEN 1
                WHEN 'In Progress' THEN 2
                WHEN 'Resolved' THEN 3
                ELSE 4
              END,
              created_at DESC
            """
        ).fetchall()


def get_admin_metrics():
    with get_connection() as connection:
        total = connection.execute("SELECT COUNT(*) FROM tickets").fetchone()[0]
        open_count = connection.execute(
            "SELECT COUNT(*) FROM tickets WHERE status = 'Open'"
        ).fetchone()[0]
        in_progress_count = connection.execute(
            "SELECT COUNT(*) FROM tickets WHERE status = 'In Progress'"
        ).fetchone()[0]
        resolved_count = connection.execute(
            "SELECT COUNT(*) FROM tickets WHERE status = 'Resolved'"
        ).fetchone()[0]
        critical_count = connection.execute(
            "SELECT COUNT(*) FROM tickets WHERE suggested_priority = 'Critical'"
        ).fetchone()[0]
        common_issue = connection.execute(
            """
            SELECT issue_type, COUNT(*) AS issue_count
            FROM tickets
            GROUP BY issue_type
            ORDER BY issue_count DESC, issue_type ASC
            LIMIT 1
            """
        ).fetchone()

    return {
        "total": total,
        "open": open_count,
        "in_progress": in_progress_count,
        "resolved": resolved_count,
        "critical": critical_count,
        "most_common_issue": common_issue["issue_type"] if common_issue else "None",
    }


def find_employee_tickets(ticket_number="", email=""):
    ticket_number = ticket_number.strip().upper()
    email = email.strip().lower()

    if not ticket_number and not email:
        return []

    query = "SELECT * FROM tickets WHERE 1 = 1"
    params = []

    if ticket_number:
        query += " AND UPPER(ticket_number) = ?"
        params.append(ticket_number)

    if email:
        query += " AND LOWER(requester_email) = ?"
        params.append(email)

    query += " ORDER BY created_at DESC"

    with get_connection() as connection:
        return connection.execute(query, params).fetchall()


def generate_ticket_number(ticket_id, timestamp):
    year = datetime.fromisoformat(timestamp).year
    return f"IT-{year}-{ticket_id:04d}"
