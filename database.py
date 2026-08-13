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


def update_ticket_admin_fields(ticket_id, admin_update):
    current_ticket = get_ticket_by_id(ticket_id)
    if current_ticket is None:
        return current_ticket

    has_changes = (
        current_ticket["status"] != admin_update["status"]
        or current_ticket["issue_type"] != admin_update["issue_type"]
        or current_ticket["final_priority"] != admin_update["final_priority"]
        or (current_ticket["assigned_to"] or "") != admin_update["assigned_to"]
    )

    if not has_changes:
        return current_ticket

    timestamp = datetime.now().isoformat(timespec="seconds")
    resolved_at = current_ticket["resolved_at"]

    if admin_update["status"] == "Resolved" and resolved_at is None:
        resolved_at = timestamp
    elif admin_update["status"] != "Resolved":
        resolved_at = None

    with get_connection() as connection:
        connection.execute(
            """
            UPDATE tickets
            SET status = ?,
                issue_type = ?,
                final_priority = ?,
                assigned_to = ?,
                updated_at = ?,
                resolved_at = ?
            WHERE id = ?
            """,
            (
                admin_update["status"],
                admin_update["issue_type"],
                admin_update["final_priority"],
                admin_update["assigned_to"] or None,
                timestamp,
                resolved_at,
                ticket_id,
            ),
        )
        connection.commit()

    return get_ticket_by_id(ticket_id)


def add_internal_note(ticket_id, author_name, message):
    timestamp = datetime.now().isoformat(timespec="seconds")

    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO ticket_updates (
              ticket_id,
              author_name,
              message,
              is_internal,
              created_at
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (ticket_id, author_name, message, 1, timestamp),
        )
        connection.commit()


def get_internal_notes(ticket_id):
    with get_connection() as connection:
        return connection.execute(
            """
            SELECT *
            FROM ticket_updates
            WHERE ticket_id = ?
              AND is_internal = 1
            ORDER BY created_at DESC
            """,
            (ticket_id,),
        ).fetchall()


def add_public_update(ticket_id, author_name, message):
    timestamp = datetime.now().isoformat(timespec="seconds")

    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO ticket_updates (
              ticket_id,
              author_name,
              message,
              is_internal,
              created_at
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (ticket_id, author_name, message, 0, timestamp),
        )
        connection.execute(
            "UPDATE tickets SET updated_at = ? WHERE id = ?",
            (timestamp, ticket_id),
        )
        connection.commit()


def get_public_updates(ticket_id):
    with get_connection() as connection:
        return connection.execute(
            """
            SELECT *
            FROM ticket_updates
            WHERE ticket_id = ?
              AND is_internal = 0
            ORDER BY created_at ASC
            """,
            (ticket_id,),
        ).fetchall()


def add_notification_log(ticket_id, notification):
    timestamp = datetime.now().isoformat(timespec="seconds")

    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO notification_logs (
              ticket_id,
              notification_type,
              recipient,
              subject,
              message,
              delivery_status,
              created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                ticket_id,
                notification["notification_type"],
                notification["recipient"],
                notification["subject"],
                notification["message"],
                notification["delivery_status"],
                timestamp,
            ),
        )
        connection.commit()


def get_recent_critical_notifications(limit=5):
    with get_connection() as connection:
        return connection.execute(
            """
            SELECT notification_logs.*,
                   tickets.ticket_number,
                   tickets.requester_name,
                   tickets.issue_type,
                   tickets.status,
                   tickets.priority_reason
            FROM notification_logs
            JOIN tickets ON tickets.id = notification_logs.ticket_id
            WHERE notification_logs.notification_type = 'Critical smart detection'
            ORDER BY notification_logs.created_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()


def get_critical_notifications(filters=None):
    filters = filters or {}
    where_clauses = ["notification_logs.notification_type = 'Critical smart detection'"]
    params = []

    search = filters.get("search", "").strip().lower()
    if search:
        where_clauses.append(
            """
            (
              LOWER(tickets.ticket_number) LIKE ?
              OR LOWER(tickets.requester_name) LIKE ?
              OR LOWER(tickets.requester_email) LIKE ?
              OR LOWER(tickets.issue_type) LIKE ?
              OR LOWER(tickets.status) LIKE ?
              OR LOWER(notification_logs.recipient) LIKE ?
              OR LOWER(notification_logs.subject) LIKE ?
              OR LOWER(notification_logs.message) LIKE ?
            )
            """
        )
        search_value = f"%{search}%"
        params.extend([search_value] * 8)

    if filters.get("status"):
        where_clauses.append("tickets.status = ?")
        params.append(filters["status"])

    if filters.get("issue_type"):
        where_clauses.append("tickets.issue_type = ?")
        params.append(filters["issue_type"])

    if filters.get("recipient"):
        where_clauses.append("LOWER(notification_logs.recipient) LIKE ?")
        params.append(f"%{filters['recipient'].strip().lower()}%")

    if filters.get("date_from"):
        where_clauses.append("date(notification_logs.created_at) >= date(?)")
        params.append(filters["date_from"])

    if filters.get("date_to"):
        where_clauses.append("date(notification_logs.created_at) <= date(?)")
        params.append(filters["date_to"])

    where_sql = " AND ".join(where_clauses)

    with get_connection() as connection:
        return connection.execute(
            f"""
            SELECT notification_logs.*,
                   tickets.ticket_number,
                   tickets.requester_name,
                   tickets.requester_email,
                   tickets.issue_type,
                   tickets.status,
                   tickets.final_priority,
                   tickets.suggested_priority,
                   tickets.priority_reason
            FROM notification_logs
            JOIN tickets ON tickets.id = notification_logs.ticket_id
            WHERE {where_sql}
            ORDER BY notification_logs.created_at DESC
            """,
            params,
        ).fetchall()


SORT_OPTIONS = {
    "ticket": "ticket_number",
    "requester": "LOWER(requester_name)",
    "issue": "LOWER(issue_type)",
    "priority": """
        CASE final_priority
          WHEN 'Critical' THEN 1
          WHEN 'High' THEN 2
          WHEN 'Medium' THEN 3
          WHEN 'Low' THEN 4
          ELSE 5
        END
    """,
    "status": """
        CASE status
          WHEN 'Open' THEN 1
          WHEN 'In Progress' THEN 2
          WHEN 'Resolved' THEN 3
          ELSE 4
        END
    """,
    "assignee": "LOWER(COALESCE(assigned_to, 'Unassigned'))",
    "created": "created_at",
}


def build_ticket_filter_clause(filters=None):
    filters = filters or {}
    where_clauses = []
    params = []

    search = filters.get("search", "").strip().lower()
    if search:
        where_clauses.append(
            """
            (
              LOWER(ticket_number) LIKE ?
              OR LOWER(requester_name) LIKE ?
              OR LOWER(requester_email) LIKE ?
              OR LOWER(issue_type) LIKE ?
              OR LOWER(description) LIKE ?
              OR LOWER(COALESCE(assigned_to, 'Unassigned')) LIKE ?
            )
            """
        )
        search_value = f"%{search}%"
        params.extend([search_value] * 6)

    if filters.get("status"):
        where_clauses.append("status = ?")
        params.append(filters["status"])

    if filters.get("priority"):
        if filters["priority"] == "Critical":
            where_clauses.append("(final_priority = ? OR suggested_priority = ?)")
            params.extend(["Critical", "Critical"])
        else:
            where_clauses.append("final_priority = ?")
            params.append(filters["priority"])

    if filters.get("issue_type"):
        where_clauses.append("issue_type = ?")
        params.append(filters["issue_type"])

    if filters.get("assignee"):
        if filters["assignee"] == "Unassigned":
            where_clauses.append("(assigned_to IS NULL OR assigned_to = '')")
        else:
            where_clauses.append("LOWER(assigned_to) = ?")
            params.append(filters["assignee"].lower())

    if filters.get("needs_owner"):
        where_clauses.append(
            """
            status != 'Resolved'
            AND (assigned_to IS NULL OR assigned_to = '')
            """
        )

    where_sql = ""
    if where_clauses:
        where_sql = "WHERE " + " AND ".join(where_clauses)

    return where_sql, params


def get_ticket_count(filters=None):
    where_sql, params = build_ticket_filter_clause(filters)

    with get_connection() as connection:
        return connection.execute(
            f"""
            SELECT COUNT(*)
            FROM tickets
            {where_sql}
            """,
            params,
        ).fetchone()[0]


def get_all_tickets(
    sort_by="status",
    sort_direction="asc",
    filters=None,
    limit=None,
    offset=0,
):
    sort_expression = SORT_OPTIONS.get(sort_by, SORT_OPTIONS["status"])
    direction = "DESC" if sort_direction == "desc" else "ASC"
    where_sql, params = build_ticket_filter_clause(filters)
    limit_sql = ""
    query_params = list(params)

    if limit is not None:
        limit_sql = "LIMIT ? OFFSET ?"
        query_params.extend([limit, offset])

    with get_connection() as connection:
        return connection.execute(
            f"""
            SELECT *
            FROM tickets
            {where_sql}
            ORDER BY {sort_expression} {direction}, created_at DESC
            {limit_sql}
            """,
            query_params,
        ).fetchall()


def get_assignee_options():
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT DISTINCT assigned_to
            FROM tickets
            WHERE assigned_to IS NOT NULL
              AND assigned_to != ''
            ORDER BY LOWER(assigned_to)
            """
        ).fetchall()

    return [row["assigned_to"] for row in rows]


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
        unassigned_open_count = connection.execute(
            """
            SELECT COUNT(*)
            FROM tickets
            WHERE status != 'Resolved'
              AND (assigned_to IS NULL OR assigned_to = '')
            """
        ).fetchone()[0]
        average_resolution_hours = connection.execute(
            """
            SELECT AVG((julianday(resolved_at) - julianday(created_at)) * 24)
            FROM tickets
            WHERE resolved_at IS NOT NULL
            """
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
        issue_breakdown = connection.execute(
            """
            SELECT issue_type AS label, COUNT(*) AS count
            FROM tickets
            GROUP BY issue_type
            ORDER BY count DESC, issue_type ASC
            LIMIT 5
            """
        ).fetchall()
        assignee_breakdown = connection.execute(
            """
            SELECT COALESCE(NULLIF(assigned_to, ''), 'Unassigned') AS label,
                   COUNT(*) AS count
            FROM tickets
            GROUP BY COALESCE(NULLIF(assigned_to, ''), 'Unassigned')
            ORDER BY count DESC, label ASC
            LIMIT 5
            """
        ).fetchall()
        priority_breakdown = connection.execute(
            """
            SELECT final_priority AS label, COUNT(*) AS count
            FROM tickets
            GROUP BY final_priority
            ORDER BY
              CASE final_priority
                WHEN 'Critical' THEN 1
                WHEN 'High' THEN 2
                WHEN 'Medium' THEN 3
                WHEN 'Low' THEN 4
                ELSE 5
              END
            """
        ).fetchall()

    return {
        "total": total,
        "open": open_count,
        "in_progress": in_progress_count,
        "resolved": resolved_count,
        "critical": critical_count,
        "unassigned_open": unassigned_open_count,
        "average_resolution_time": format_resolution_time(average_resolution_hours),
        "most_common_issue": common_issue["issue_type"] if common_issue else "None",
        "issue_breakdown": format_breakdown(issue_breakdown, total),
        "assignee_breakdown": format_breakdown(assignee_breakdown, total),
        "priority_breakdown": format_breakdown(priority_breakdown, total),
    }


def format_breakdown(rows, total):
    breakdown = []

    for row in rows:
        count = row["count"]
        percent = round((count / total) * 100) if total else 0
        breakdown.append(
            {
                "label": row["label"],
                "count": count,
                "percent": percent,
            }
        )

    return breakdown


def format_resolution_time(hours):
    if hours is None:
        return "No resolved tickets"

    if hours < 1:
        minutes = max(1, round(hours * 60))
        return f"{minutes} min"

    if hours < 24:
        return f"{hours:.1f} hrs"

    days = hours / 24
    return f"{days:.1f} days"


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
