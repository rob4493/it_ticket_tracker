from datetime import datetime

from flask import Flask, redirect, render_template, request, url_for

from database import (
    add_internal_note,
    add_public_update,
    create_ticket,
    find_employee_tickets,
    get_admin_metrics,
    get_all_tickets,
    get_assignee_options,
    get_internal_notes,
    get_public_updates,
    get_ticket_by_id,
    init_db,
    update_ticket_admin_fields,
)


app = Flask(__name__)
init_db()


@app.template_filter("short_datetime")
def short_datetime(value):
    if not value:
        return "Not set"

    try:
        return datetime.fromisoformat(value).strftime("%Y-%m-%d %H:%M")
    except ValueError:
        return value


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
TICKET_STATUSES = ["Open", "In Progress", "Resolved"]
ADMIN_SORT_OPTIONS = {"ticket", "requester", "issue", "priority", "status", "assignee", "created"}
ADMIN_SORT_DIRECTIONS = {"asc", "desc"}

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
    success_message = ""
    search = {"ticket_number": "", "email": ""}
    display_mode = "detail"

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
            if search["email"] and not search["ticket_number"]:
                display_mode = "list"

    return render_employee_portal(
        errors=errors,
        lookup_attempted=lookup_attempted,
        search=search,
        tickets=tickets,
        success_message=success_message,
        display_mode=display_mode,
    )


@app.route("/employee/ticket/<int:ticket_id>")
def employee_ticket_detail(ticket_id):
    ticket = get_ticket_by_id(ticket_id)
    email = request.args.get("email", "").strip().lower()
    search = {
        "ticket_number": ticket["ticket_number"] if ticket else "",
        "email": email,
    }

    if ticket is None:
        return render_employee_portal(
            errors=["Ticket not found."],
            lookup_attempted=True,
            search=search,
            tickets=[],
            display_mode="detail",
        ), 404

    if not email:
        return render_employee_portal(
            errors=["Enter the requester email address to view this ticket."],
            lookup_attempted=True,
            search=search,
            tickets=[],
            display_mode="detail",
        )

    if email != ticket["requester_email"].lower():
        return render_employee_portal(
            errors=["Email must match the requester email on the ticket."],
            lookup_attempted=True,
            search=search,
            tickets=[],
            display_mode="detail",
        )

    return render_employee_portal(
        errors=[],
        lookup_attempted=True,
        search=search,
        tickets=[ticket],
        display_mode="detail",
    )


@app.route("/employee/ticket/<int:ticket_id>/reply", methods=["POST"])
def add_employee_reply(ticket_id):
    ticket = get_ticket_by_id(ticket_id)
    if ticket is None:
        return render_employee_portal(
            errors=["Ticket not found."],
            lookup_attempted=True,
            search={"ticket_number": "", "email": ""},
            tickets=[],
            display_mode="detail",
        ), 404

    reply_email = request.form.get("reply_email", "").strip().lower()
    reply_message = request.form.get("message", "").strip()
    search = {"ticket_number": ticket["ticket_number"], "email": reply_email}
    errors = []

    if not reply_email:
        errors.append("Enter your email address before replying.")
    elif reply_email != ticket["requester_email"].lower():
        errors.append("Email must match the requester email on the ticket.")

    if not reply_message:
        errors.append("Reply message cannot be blank.")

    if not errors:
        add_public_update(ticket_id, ticket["requester_name"], reply_message)
        return redirect(
            url_for(
                "employee_ticket_detail",
                ticket_id=ticket_id,
                email=reply_email,
                success="Reply added to the ticket conversation.",
            )
        )

    return render_employee_portal(
        errors=errors,
        lookup_attempted=True,
        search=search,
        tickets=[ticket],
        display_mode="detail",
    )


def render_employee_portal(
    errors,
    lookup_attempted,
    search,
    tickets,
    success_message="",
    display_mode="detail",
):
    if not success_message:
        success_message = request.args.get("success", "").strip()

    public_updates_by_ticket = {
        ticket["id"]: get_public_updates(ticket["id"])
        for ticket in tickets
        if display_mode == "detail"
    }

    return render_template(
        "employee_portal.html",
        errors=errors,
        lookup_attempted=lookup_attempted,
        search=search,
        tickets=tickets,
        public_updates_by_ticket=public_updates_by_ticket,
        success_message=success_message,
        display_mode=display_mode,
    )


@app.route("/admin")
def admin_dashboard():
    sort_by = request.args.get("sort", "status").strip().lower()
    sort_direction = request.args.get("direction", "asc").strip().lower()
    filters = {
        "search": request.args.get("search", "").strip(),
        "status": request.args.get("status", "").strip(),
        "priority": request.args.get("priority", "").strip(),
        "issue_type": request.args.get("issue_type", "").strip(),
        "assignee": request.args.get("assignee", "").strip(),
    }

    if sort_by not in ADMIN_SORT_OPTIONS:
        sort_by = "status"

    if sort_direction not in ADMIN_SORT_DIRECTIONS:
        sort_direction = "asc"

    if filters["status"] and filters["status"] not in TICKET_STATUSES:
        filters["status"] = ""

    if filters["priority"] and filters["priority"] not in PRIORITIES:
        filters["priority"] = ""

    if filters["issue_type"] and filters["issue_type"] not in ISSUE_TYPES:
        filters["issue_type"] = ""

    assignee_options = get_assignee_options()
    if (
        filters["assignee"]
        and filters["assignee"] != "Unassigned"
        and filters["assignee"] not in assignee_options
    ):
        filters["assignee"] = ""

    tickets = get_all_tickets(
        sort_by=sort_by,
        sort_direction=sort_direction,
        filters=filters,
    )
    metrics = get_admin_metrics()
    return render_template(
        "admin_dashboard.html",
        metrics=metrics,
        tickets=tickets,
        sort_by=sort_by,
        sort_direction=sort_direction,
        filters=filters,
        statuses=TICKET_STATUSES,
        priorities=PRIORITIES,
        issue_types=ISSUE_TYPES,
        assignee_options=assignee_options,
    )


@app.route("/admin/ticket/<int:ticket_id>")
def admin_ticket_detail(ticket_id):
    if get_ticket_by_id(ticket_id) is None:
        return render_admin_ticket_detail(ticket_id=ticket_id), 404

    return render_admin_ticket_detail(
        ticket_id=ticket_id,
        success_message=request.args.get("success", "").strip(),
    )


@app.route("/admin/ticket/<int:ticket_id>/edit", methods=["POST"])
def update_admin_ticket(ticket_id):
    ticket = get_ticket_by_id(ticket_id)
    if ticket is None:
        return render_admin_ticket_detail(ticket_id=ticket_id), 404

    admin_update = {
        "status": request.form.get("status", "").strip(),
        "issue_type": request.form.get("issue_type", "").strip(),
        "final_priority": request.form.get("final_priority", "").strip(),
        "assigned_to": request.form.get("assigned_to", "").strip(),
    }

    errors = validate_admin_ticket_update(admin_update)

    if errors:
        return render_admin_ticket_detail(ticket_id=ticket_id, errors=errors)

    if admin_update_matches_ticket(admin_update, ticket):
        success_message = "No admin fields changed."
    else:
        update_ticket_admin_fields(ticket_id, admin_update)
        success_message = "Admin ticket fields updated."

    return redirect(url_for("admin_ticket_detail", ticket_id=ticket_id, success=success_message))


@app.route("/admin/ticket/<int:ticket_id>/note", methods=["POST"])
def add_ticket_note(ticket_id):
    if get_ticket_by_id(ticket_id) is None:
        return render_admin_ticket_detail(ticket_id=ticket_id), 404

    note_author = request.form.get("author_name", "").strip() or "IT Admin"
    note_message = request.form.get("message", "").strip()

    if not note_message:
        return render_admin_ticket_detail(
            ticket_id=ticket_id,
            errors=["Internal note cannot be blank."],
            note_author=note_author,
        )

    add_internal_note(ticket_id, note_author, note_message)
    return redirect(url_for("admin_ticket_detail", ticket_id=ticket_id, success="Internal note added."))


@app.route("/admin/ticket/<int:ticket_id>/reply", methods=["POST"])
def add_admin_reply(ticket_id):
    if get_ticket_by_id(ticket_id) is None:
        return render_admin_ticket_detail(ticket_id=ticket_id), 404

    reply_author = request.form.get("reply_author", "").strip() or "IT Support"
    reply_message = request.form.get("message", "").strip()

    if not reply_message:
        return render_admin_ticket_detail(
            ticket_id=ticket_id,
            errors=["Employee-visible reply cannot be blank."],
            reply_author=reply_author,
        )

    add_public_update(ticket_id, reply_author, reply_message)
    return redirect(url_for("admin_ticket_detail", ticket_id=ticket_id, success="Employee-visible reply added."))


def render_admin_ticket_detail(
    ticket_id,
    errors=None,
    success_message="",
    note_author="IT Admin",
    reply_author="IT Support",
):
    ticket = get_ticket_by_id(ticket_id)
    if ticket is None:
        return render_template(
            "ticket_detail.html",
            ticket=None,
            internal_notes=[],
            statuses=TICKET_STATUSES,
            issue_types=ISSUE_TYPES,
            priorities=PRIORITIES,
            errors=errors or [],
            success_message=success_message,
            note_author=note_author,
            public_updates=[],
            reply_author=reply_author,
        )

    return render_template(
        "ticket_detail.html",
        ticket=ticket,
        internal_notes=get_internal_notes(ticket_id),
        public_updates=get_public_updates(ticket_id),
        statuses=TICKET_STATUSES,
        issue_types=ISSUE_TYPES,
        priorities=PRIORITIES,
        errors=errors or [],
        success_message=success_message,
        note_author=note_author,
        reply_author=reply_author,
    )


def validate_admin_ticket_update(admin_update):
    errors = []

    if admin_update["status"] not in TICKET_STATUSES:
        errors.append("Select a valid ticket status.")

    if admin_update["issue_type"] not in ISSUE_TYPES:
        errors.append("Select a valid issue type.")

    if admin_update["final_priority"] not in PRIORITIES:
        errors.append("Select a valid priority.")

    return errors


def admin_update_matches_ticket(admin_update, ticket):
    return (
        admin_update["status"] == ticket["status"]
        and admin_update["issue_type"] == ticket["issue_type"]
        and admin_update["final_priority"] == ticket["final_priority"]
        and admin_update["assigned_to"] == (ticket["assigned_to"] or "")
    )


@app.route("/health")
def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
