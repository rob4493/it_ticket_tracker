from flask import Flask, render_template, request

from database import (
    create_ticket,
    find_employee_tickets,
    get_admin_metrics,
    get_all_tickets,
    get_ticket_by_id,
    init_db,
)


app = Flask(__name__)
init_db()


@app.route("/")
def home():
    return render_template("home.html")


ISSUE_TYPES = [
    "Password or account access",
    "Hardware",
    "Software",
    "Network or Wi-Fi",
    "Email",
    "Printer",
    "Security concern",
    "Other",
]

PRIORITIES = ["Low", "Medium", "High", "Critical"]
PRIORITY_RANK = {"Low": 1, "Medium": 2, "High": 3, "Critical": 4}

SECURITY_CRITICAL_TERMS = [
    "phishing",
    "suspicious email",
    "clicked a link",
    "clicked link",
    "downloaded",
    "unknown file",
    "attachment",
    "malware",
    "virus",
    "ransomware",
    "compromised",
    "password stolen",
    "unauthorized access",
    "data breach",
]

BUSINESS_IMPACT_TERMS = [
    "entire office",
    "everyone",
    "all users",
    "company-wide",
    "cannot work",
    "system down",
    "outage",
]


@app.route("/submit", methods=["GET", "POST"])
def submit_ticket():
    if request.method == "POST":
        ticket = {
            "name": request.form.get("name", "").strip(),
            "email": request.form.get("email", "").strip(),
            "employee_id": request.form.get("employee_id", "").strip(),
            "department": request.form.get("department", "").strip(),
            "issue_type": request.form.get("issue_type", "").strip(),
            "priority": request.form.get("priority", "").strip(),
            "description": request.form.get("description", "").strip(),
        }

        errors = validate_ticket_form(ticket)
        if errors:
            return render_template(
                "submit_ticket.html",
                errors=errors,
                ticket=ticket,
                issue_types=ISSUE_TYPES,
                priorities=PRIORITIES,
            )

        priority_suggestion = suggest_priority(ticket)
        saved_ticket = create_ticket(ticket, priority_suggestion)
        show_employee_urgent_notice = should_show_employee_urgent_notice(
            ticket["priority"], priority_suggestion["priority"]
        )
        return render_template(
            "ticket_success.html",
            ticket=saved_ticket,
            priority_suggestion=priority_suggestion,
            show_employee_urgent_notice=show_employee_urgent_notice,
        )

    return render_template(
        "submit_ticket.html",
        errors=[],
        ticket={},
        issue_types=ISSUE_TYPES,
        priorities=PRIORITIES,
    )


def validate_ticket_form(ticket):
    errors = []
    required_fields = {
        "name": "Name is required.",
        "email": "Email is required.",
        "department": "Department is required.",
        "issue_type": "Issue type is required.",
        "priority": "Priority is required.",
        "description": "Description is required.",
    }

    for field, message in required_fields.items():
        if not ticket[field]:
            errors.append(message)

    if ticket["issue_type"] and ticket["issue_type"] not in ISSUE_TYPES:
        errors.append("Select a valid issue type.")

    if ticket["priority"] and ticket["priority"] not in PRIORITIES:
        errors.append("Select a valid priority.")

    return errors


def suggest_priority(ticket):
    issue_type = ticket["issue_type"]
    description = ticket["description"].lower()

    if issue_type == "Security concern":
        for term in SECURITY_CRITICAL_TERMS:
            if term in description:
                return {
                    "priority": "Critical",
                    "reason": "Security-related ticket mentions a high-risk phrase that may indicate phishing, malware, unauthorized access, or account compromise.",
                }

        return {
            "priority": "High",
            "reason": "Security concerns should be reviewed quickly even when no critical trigger phrase is detected.",
        }

    if issue_type == "Network or Wi-Fi":
        for term in BUSINESS_IMPACT_TERMS:
            if term in description:
                return {
                    "priority": "Critical",
                    "reason": "Network issue appears to affect multiple users or business operations.",
                }

        return {
            "priority": "Medium",
            "reason": "Network issues often disrupt work, but this description does not indicate a company-wide outage.",
        }

    if issue_type == "Password or account access":
        if "locked out" in description or "cannot login" in description or "can't login" in description:
            return {
                "priority": "Medium",
                "reason": "Account access issue may prevent the employee from working.",
            }

        return {
            "priority": "Low",
            "reason": "Routine account access requests are usually handled as low priority unless business impact is stated.",
        }

    if issue_type == "Hardware" and (
        "will not turn on" in description or "won't turn on" in description
    ):
        return {
            "priority": "High",
            "reason": "Hardware issue may prevent the employee from using their workstation.",
        }

    return {
        "priority": ticket["priority"],
        "reason": "No higher-risk triage rule was triggered, so the employee-selected priority is kept as the suggestion.",
    }


def should_show_employee_urgent_notice(selected_priority, suggested_priority):
    return (
        suggested_priority == "Critical"
        and PRIORITY_RANK[suggested_priority] > PRIORITY_RANK[selected_priority]
    )


@app.route("/employee", methods=["GET", "POST"])
def employee_portal():
    tickets = []
    lookup_attempted = False
    errors = []
    search = {"ticket_number": "", "email": ""}

    if request.method == "POST":
        lookup_attempted = True
        search = {
            "ticket_number": request.form.get("ticket_number", "").strip(),
            "email": request.form.get("email", "").strip(),
        }

        if not search["ticket_number"] and not search["email"]:
            errors.append("Enter a ticket number, email address, or both.")
        else:
            tickets = find_employee_tickets(
                ticket_number=search["ticket_number"],
                email=search["email"],
            )

    return render_template(
        "employee_portal.html",
        errors=errors,
        lookup_attempted=lookup_attempted,
        search=search,
        tickets=tickets,
    )


@app.route("/admin")
def admin_dashboard():
    tickets = get_all_tickets()
    metrics = get_admin_metrics()
    return render_template(
        "admin_dashboard.html",
        metrics=metrics,
        tickets=tickets,
    )


@app.route("/admin/ticket/<int:ticket_id>")
def admin_ticket_detail(ticket_id):
    ticket = get_ticket_by_id(ticket_id)
    if ticket is None:
        return render_template("ticket_detail.html", ticket=None), 404

    return render_template("ticket_detail.html", ticket=ticket)


@app.route("/health")
def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
