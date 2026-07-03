# IT Help Desk Ticket Tracker

This project will become a simple web-based IT help desk ticket tracker. The goal is to simulate a small internal business system where users can submit IT support requests and an admin can review, filter, and update ticket statuses.

The preferred stack for this project is:

- Python
- Flask
- SQLite
- HTML
- CSS
- JavaScript, only where useful

## Current Status

This is the current working version of the project.

Right now, the app includes:

- A basic Flask application in `app.py`
- A home page template
- A shared base layout template
- Templates for the main employee and admin pages
- Active routes for the home page, employee portal, submit ticket, admin dashboard, admin ticket detail, and health check
- A custom dark-theme CSS file
- A `requirements.txt` file listing Flask as the first dependency
- A `.gitignore` file for local Python environment files
- A `/health` route that can be used to confirm the app is running
- A ticket submission form that validates required fields, saves to SQLite, and shows a confirmation page
- A rule-based smart priority suggestion on submitted tickets
- An employee ticket lookup page that supports ticket number, email address, or both
- An admin console that displays submitted tickets, queue metrics, clickable ticket numbers, and read-only ticket detail pages

Full admin ticket editing, search, filtering, advanced analytics, employee directory lookup, and email notifications are planned for later phases.

## Project Goal

The finished project should demonstrate:

- Basic Python web development
- Flask routing and templates
- SQLite database usage
- IT support workflow thinking
- Ticket status management
- Search and filtering
- Simple operational analytics
- Clear project documentation

## Completed Features

The project currently includes:

- Submit ticket form
- Ticket fields such as name, email, employee ID, department, issue type, description, and priority
- SQLite ticket storage
- Auto-generated ticket numbers
- Ticket confirmation page
- Ticket statuses stored in the database: Open, In Progress, and Resolved
- Employee ticket lookup by ticket number, email address, or both
- Admin dashboard with ticket table and queue metrics
- Read-only admin ticket detail page
- Rule-based smart priority suggestion
- Basic analytics for ticket counts and most common issue type

## Planned Features

The project still needs:

- Admin status update workflow
- Admin priority override
- Admin issue type and field correction
- Ticket assignment and reassignment
- Internal IT notes
- Employee-visible ticket conversation
- Critical ticket email notification for rule-detected Critical tickets
- Employee directory lookup to auto-fill department from employee email or ID
- Search and filter tools
- Advanced analytics, such as average resolution time and tickets by assignee

## Current File Structure

```text
it_ticket_tracker/
  app.py
  database.py
  schema.sql
  tickets.db
  requirements.txt
  README.md
  build_path.txt
  templates/
    base.html
    home.html
    employee_portal.html
    submit_ticket.html
    ticket_success.html
    admin_dashboard.html
    ticket_detail.html
    admin_login.html
  static/
    css/
      styles.css
```

## Template Notes

The project now has the main template files for the current employee and admin workflows. Some templates are active pages, while others are reserved for later features.

Current templates:

- `base.html`: Shared layout used by the other pages.
- `home.html`: Current home page.
- `employee_portal.html`: Employee area for checking ticket status. Follow-up updates will be added later.
- `submit_ticket.html`: Ticket submission form.
- `ticket_success.html`: Confirmation page after a ticket is submitted.
- `admin_dashboard.html`: Admin page for viewing submitted tickets and queue metrics.
- `ticket_detail.html`: Admin page for viewing one ticket. Status updates will be added later.
- `admin_login.html`: Future admin login page.

The home, employee portal, submit ticket, ticket success, admin dashboard, and ticket detail templates are connected to active routes right now. Admin login will be connected when authentication is built.

Current active routes:

- `/`: Home page.
- `/employee`: Employee ticket lookup page.
- `/submit`: Employee ticket submission form.
- `/admin`: Admin console for reviewing submitted tickets.
- `/admin/ticket/<id>`: Read-only admin ticket detail page.
- `/health`: Basic health check route.

## Current Admin Console Behavior

The `/admin` page now shows submitted tickets from SQLite in a table.

Current admin fields shown:

- Ticket number
- Requester name
- Issue type
- Smart suggested priority
- Status
- Assignee
- Created timestamp
- View link

The admin console also shows basic queue metrics:

- Total tickets
- Open tickets
- In Progress tickets
- Resolved tickets
- Critical suggested tickets
- Most common issue type

The ticket number and View action both open the admin ticket detail page.

The ticket detail page currently shows read-only information, including the full smart-priority triage reason. Status updates, assignments, issue type correction, priority correction, and internal admin notes are planned for later phases.

## Planned Admin Workflow Enhancements

Future admin ticket editing should support:

- Manual priority changes when IT determines the employee-selected or smart-suggested priority should be raised or lowered.
- Manual issue type changes when the employee chooses the wrong category.
- Status changes from Open to In Progress to Resolved.
- Assignment and reassignment to IT staff.
- Internal/private notes for IT workers only.
- Employee-visible ticket conversation updates for follow-up questions, reset instructions, or safe resolution steps.
- Critical ticket email notification to admins when the rule-based detection marks a ticket Critical.

Critical email notifications should be based on detection only, not on an employee selecting Critical manually. This helps prevent priority abuse while still alerting IT when the description suggests a true urgent risk.

## Current Form Behavior

The `/submit` page now accepts basic ticket information:

- Name
- Email
- Employee ID, optional
- Department
- Issue type
- Priority
- Description

When the form is submitted, Flask checks that required fields are present, saves the ticket to SQLite, generates a ticket number, and then shows a confirmation page.

Ticket numbers use this format:

```text
IT-2026-0001
```

The year is based on the ticket creation date, and the final number is based on the database ID.

Employee ticket lookup supports ticket number, email address, or both. A ticket number can find one specific ticket, while email can show tickets submitted by that requester. If both are provided, both values must match the saved ticket.

## Current Employee Portal Behavior

The `/employee` page lets employees search for tickets using:

- Ticket number only
- Email address only
- Ticket number and email address together

Ticket number search finds one specific ticket. Email search can return multiple tickets submitted by the same requester. When both are provided, both values must match the saved ticket.

The employee-facing results show safe ticket details only:

- Ticket number
- Issue type
- Status
- Priority selected by the employee
- Department
- Submitted and updated timestamps
- Description

Internal admin notes and full smart-priority triage details are not shown to employees.

The app also calculates a smart priority suggestion. This is currently rule-based, not connected to an AI API. It looks at the issue type and description for high-risk phrases, such as security incidents, suspicious links, unknown downloads, account compromise, or broader business-impact language.

The full smart suggestion is intended for future admin review, not regular employee display. Employees only see a calm urgent-review notice when the rule suggests Critical and the employee selected a lower priority. The smart suggestion does not override the employee-selected priority yet.

## Planned Employee Directory Lookup

In a real company, employee email addresses or employee IDs often connect to an internal directory. That directory can provide details such as name, department, title, manager, or location.

For this project, a future version can simulate that behavior with a small employee directory. When an employee enters an email address or employee ID, the app could automatically fill the department field.

Example:

```text
Employee email: alex.morgan@company.com
Detected department: Accounting
```

If the employee is not found in the directory, the form can still let them enter the department manually.

Possible real-world integrations later:

- Active Directory
- Microsoft Entra ID / Azure AD
- Okta
- Google Workspace
- HR information system
- Internal employee directory API

## How To Run The App

From the project folder, create and activate a virtual environment.

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the project dependencies:

```powershell
pip install -r requirements.txt
```

Run the Flask app:

```powershell
python app.py
```

Then open this address in a web browser:

```text
http://127.0.0.1:5000
```

To check whether the server is responding, visit:

```text
http://127.0.0.1:5000/health
```

You should see:

```json
{
  "status": "ok"
}
```

## Development Notes

This project is being built one step at a time. The foundation, ticket submission, database storage, employee lookup, and read-only admin console are now in place.

The next logical step is admin ticket editing, starting with status changes and then expanding into priority correction, assignment, issue type correction, and notes.

## Visual Direction

The current visual style uses a dark service desk console theme:

- Left-side navigation instead of a top marketing-style nav
- Compact workspace header
- Separate Employee and Admin navigation sections
- Workflow/table hybrid home layout
- Dark charcoal background with fewer card-style panels
- Bright blue primary actions
- Cyan interface accents
- Violet build/status accent for non-ticket states
- Light text with muted gray-blue supporting text
- Modern dashboard font stack: Inter, Segoe UI, system UI, sans-serif

This direction is intended to feel like a practical internal IT operations console instead of a public marketing website or generic SaaS landing page.

Green is intentionally reserved for future Resolved status indicators so the color system stays clear.
