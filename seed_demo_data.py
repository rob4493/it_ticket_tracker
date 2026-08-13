from datetime import datetime, timedelta

from database import get_connection, init_db
from employee_directory import EMPLOYEE_DIRECTORY


DEMO_TICKETS = [
    ("E1001", "Hardware", "Medium", "Open", "", 1, None, "Laptop fan is loud and the device feels hot during normal work."),
    ("E1002", "Password or account access", "Low", "Resolved", "Nina Helpdesk", 2, 5, "Password reset needed after returning from leave."),
    ("E1003", "Network or Wi-Fi", "Medium", "In Progress", "Priya Network", 3, None, "Conference room Wi-Fi keeps dropping during video calls."),
    ("E1004", "Software", "Low", "Open", "Morgan Rivera", 3, None, "Requesting install of approved PDF editor."),
    ("E1005", "Security concern", "Critical", "In Progress", "Luis Security", 4, None, "Clicked a link in a suspicious email and downloaded an unknown file."),
    ("E1006", "Email", "Medium", "Resolved", "Omar Systems", 5, 28, "Shared mailbox is not receiving external vendor messages."),
    ("E1007", "Printer", "Low", "Open", "", 5, None, "Printer on second floor shows paper jam after clearing tray."),
    ("E1008", "Hardware", "High", "In Progress", "Morgan Rivera", 6, None, "Docking station no longer detects two monitors."),
    ("E1009", "Software", "Medium", "Resolved", "Nina Helpdesk", 7, 18, "Legal template add-in disappeared from Word."),
    ("E1010", "Network or Wi-Fi", "Critical", "Open", "Priya Network", 7, None, "Entire office cannot connect to internal file shares."),
    ("E1011", "Password or account access", "Medium", "Resolved", "Omar Systems", 8, 3, "Developer account locked out after MFA phone replacement."),
    ("E1012", "Printer", "Low", "Resolved", "Nina Helpdesk", 8, 11, "Warehouse label printer prints blank labels."),
    ("E1013", "Email", "Low", "Open", "", 9, None, "Outlook search results are missing recent customer messages."),
    ("E1014", "Security concern", "Critical", "Resolved", "Luis Security", 10, 6, "Received MFA approval prompts that were not requested."),
    ("E1015", "Software", "Medium", "In Progress", "Morgan Rivera", 11, None, "Training platform videos fail to load for new hires."),
    ("E1016", "Hardware", "Low", "Open", "", 11, None, "Keyboard intermittently repeats letters while typing."),
    ("E1001", "Email", "Medium", "Resolved", "Omar Systems", 12, 26, "Finance distribution list missing two new employees."),
    ("E1002", "Network or Wi-Fi", "High", "Resolved", "Priya Network", 12, 9, "HR onboarding room has no wired network connection."),
    ("E1003", "Password or account access", "Medium", "Open", "Nina Helpdesk", 13, None, "CRM login fails after password change."),
    ("E1004", "Other", "Low", "Resolved", "Morgan Rivera", 13, 4, "Need help setting up scanner shortcut on desktop."),
    ("E1006", "Security concern", "Critical", "Open", "Luis Security", 14, None, "Marketing laptop reports possible malware popups."),
    ("E1008", "Software", "High", "In Progress", "Omar Systems", 14, None, "Finance reporting app crashes during month-end export."),
    ("E1011", "Network or Wi-Fi", "Medium", "Open", "Priya Network", 15, None, "VPN disconnects every few minutes from remote office."),
    ("E1012", "Hardware", "Medium", "Resolved", "Morgan Rivera", 16, 14, "Barcode scanner not recognized by inventory workstation."),
    ("E1013", "Email", "Low", "Open", "", 16, None, "Need email signature updated after title change."),
    ("E1015", "Printer", "Low", "In Progress", "Nina Helpdesk", 17, None, "Training room printer requires admin credentials."),
    ("E1016", "Other", "Medium", "Resolved", "Omar Systems", 18, 31, "Purchasing shared folder permissions need review."),
    ("E1014", "Password or account access", "High", "Open", "Luis Security", 19, None, "Executive assistant cannot access encrypted files."),
]


PRIORITY_REASONS = {
    "Low": "Demo ticket uses routine priority for non-blocking support work.",
    "Medium": "Demo ticket may slow down work but does not indicate a company-wide outage.",
    "High": "Demo ticket may block important business work or a key user workflow.",
    "Critical": "Demo ticket indicates a security or business-impact scenario requiring urgent review.",
}


def main():
    init_db()

    with get_connection() as connection:
        existing_demo_rows = connection.execute(
            "SELECT id FROM tickets WHERE description LIKE '[Demo]%'"
        ).fetchall()
        existing_demo_ids = [row["id"] for row in existing_demo_rows]

        if existing_demo_ids:
            placeholders = ",".join("?" for _ in existing_demo_ids)
            connection.execute(
                f"DELETE FROM notification_logs WHERE ticket_id IN ({placeholders})",
                existing_demo_ids,
            )
            connection.execute(
                f"DELETE FROM ticket_updates WHERE ticket_id IN ({placeholders})",
                existing_demo_ids,
            )
            connection.execute(
                f"DELETE FROM tickets WHERE id IN ({placeholders})",
                existing_demo_ids,
            )

        base_time = datetime.now().replace(second=0, microsecond=0)

        for index, demo_ticket in enumerate(DEMO_TICKETS, start=1):
            (
                employee_id,
                issue_type,
                priority,
                status,
                assignee,
                created_days_ago,
                resolution_hours,
                description,
            ) = demo_ticket
            employee = employee_by_id(employee_id)
            created_at = base_time - timedelta(days=created_days_ago, hours=index % 7)
            updated_at = created_at + timedelta(hours=4 + (index % 9))
            resolved_at = None

            if status == "Resolved" and resolution_hours is not None:
                resolved_at = created_at + timedelta(hours=resolution_hours)
                updated_at = resolved_at

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
                  assigned_to,
                  created_at,
                  updated_at,
                  resolved_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    employee["name"],
                    employee["email"],
                    employee["employee_id"],
                    employee["department"],
                    issue_type,
                    priority,
                    suggested_priority(issue_type, priority, description),
                    PRIORITY_REASONS[priority],
                    priority,
                    f"[Demo] {description}",
                    status,
                    assignee or None,
                    created_at.isoformat(timespec="seconds"),
                    updated_at.isoformat(timespec="seconds"),
                    resolved_at.isoformat(timespec="seconds") if resolved_at else None,
                ),
            )
            ticket_id = cursor.lastrowid
            ticket_number = f"IT-{created_at.year}-{ticket_id:04d}"
            connection.execute(
                "UPDATE tickets SET ticket_number = ? WHERE id = ?",
                (ticket_number, ticket_id),
            )

            detected_priority = suggested_priority(issue_type, priority, description)
            if detected_priority == "Critical":
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
                        "Critical smart detection",
                        "it-admins@company.com",
                        f"Critical IT ticket detected: {ticket_number}",
                        (
                            f"{ticket_number} was flagged Critical by rule-based detection. "
                            f"Requester: {employee['name']}. Issue type: {issue_type}."
                        ),
                        "Simulated email logged",
                        created_at.isoformat(timespec="seconds"),
                    ),
                )

            if index % 4 == 0:
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
                    (
                        ticket_id,
                        assignee or "IT Admin",
                        "Demo note: reviewed ticket details and confirmed next support step.",
                        1,
                        updated_at.isoformat(timespec="seconds"),
                    ),
                )

        connection.commit()

    print(f"Refreshed {len(DEMO_TICKETS)} demo tickets.")


def employee_by_id(employee_id):
    for employee in EMPLOYEE_DIRECTORY:
        if employee["employee_id"] == employee_id:
            return employee

    raise ValueError(f"Employee ID not found in directory: {employee_id}")


def suggested_priority(issue_type, priority, description):
    security_text = description.lower()

    if issue_type == "Security concern" and (
        "clicked" in security_text
        or "malware" in security_text
        or "mfa" in security_text
        or "encrypted" in security_text
    ):
        return "Critical"

    return priority


if __name__ == "__main__":
    main()
