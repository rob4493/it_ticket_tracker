import sqlite3
from datetime import datetime, timedelta

from database import DATABASE_PATH


SAMPLE_LOG_STATUS = "Simulated email logged"
SAMPLE_LOG_TYPE = "Critical smart detection"
SAMPLE_RECIPIENT = "it-admins@company.com"
SAMPLE_LOG_MARKER = "[Sample dashboard log]"


def main():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    critical_tickets = connection.execute(
        """
        SELECT id,
               ticket_number,
               requester_name,
               issue_type,
               priority_reason
        FROM tickets
        WHERE suggested_priority = 'Critical'
        ORDER BY created_at DESC
        LIMIT 4
        """
    ).fetchall()

    if not critical_tickets:
        print("No smart-critical tickets found. Run seed_demo_data.py first.")
        connection.close()
        return

    connection.execute(
        """
        DELETE FROM notification_logs
        WHERE (
            notification_type = ?
            AND recipient = ?
            AND message LIKE ?
        )
        OR delivery_status = 'Sample email log for dashboard review'
        """,
        (SAMPLE_LOG_TYPE, SAMPLE_RECIPIENT, f"{SAMPLE_LOG_MARKER}%"),
    )

    now = datetime.now().replace(microsecond=0)

    for index, ticket in enumerate(critical_tickets):
        created_at = (now - timedelta(minutes=index * 8)).isoformat()
        reason = (
            ticket["priority_reason"]
            or "Smart detection marked this ticket for immediate IT review."
        )
        message = (
            f"{SAMPLE_LOG_MARKER}\n"
            f"Ticket {ticket['ticket_number']} was flagged as Critical by smart detection.\n"
            f"Requester: {ticket['requester_name']}\n"
            f"Issue type: {ticket['issue_type']}\n"
            f"Reason: {reason}"
        )

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
                ticket["id"],
                SAMPLE_LOG_TYPE,
                SAMPLE_RECIPIENT,
                f"Critical IT ticket detected: {ticket['ticket_number']}",
                message,
                SAMPLE_LOG_STATUS,
                created_at,
            ),
        )

    connection.commit()
    connection.close()
    print(f"Created {len(critical_tickets)} sample critical notification logs.")


if __name__ == "__main__":
    main()
