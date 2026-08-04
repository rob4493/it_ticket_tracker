# IT Help Desk Ticket Tracker

This project is a simple web-based IT help desk ticket tracker. The goal is to simulate a small internal business system where employees can submit IT support requests and admins can review, filter, and update ticket statuses.

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

- A basic Flask application in `it_track.py`
- A home page template
- A shared base layout template
- Templates for the main employee and admin pages
- Active routes for the home page, login/logout, employee portal, submit ticket, admin dashboard, admin ticket detail, ticket conversation replies, and health check
- A custom dark-theme CSS file
- A `requirements.txt` file listing Flask as the first dependency
- A `.gitignore` file for local Python environment files
- A `/health` route that can be used to confirm the app is running
- A ticket submission form that validates required fields, saves to SQLite, and shows a confirmation page
- A rule-based smart priority suggestion on submitted tickets
- A simulated employee directory lookup that can fill employee details by company email or employee ID
- An employee ticket lookup page that supports ticket number, email address, or both, with compact email-only results
- Basic session login with employee and admin role separation
- An admin console that displays submitted tickets, queue metrics, clickable ticket numbers, ticket detail pages, admin editing, private internal IT notes, and employee-visible replies

Additional advanced analytics, stronger production authentication, and email notifications are planned for later phases.

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
- Simulated employee directory lookup by company email or employee ID
- Basic login and role-aware navigation
- Protected admin-only pages
- Ticket statuses stored in the database: Open, In Progress, and Resolved
- Employee ticket lookup by ticket number, email address, or both, with compact email-only results
- Admin dashboard with ticket table and queue metrics
- Admin ticket detail page with status, assignee, issue type, and priority editing
- Admin queue sorting by ticket number, requester, issue, priority, status, assignee, and created date
- Admin queue search and filters by keyword, status, priority, issue type, and assignee
- Critical smart-suggestion indicators in the admin queue
- Shortened visible timestamps without seconds
- Internal/private IT notes on admin ticket detail pages
- Employee-visible ticket conversation between IT and the requester
- Rule-based smart priority suggestion
- Basic analytics for ticket counts, most common issue type, average resolution time, issue mix, assignee workload, and priority mix

## Future Features

The next planned improvements are:

- Live admin search results while typing
- Critical ticket email notification for rule-detected Critical tickets
- Export or reporting tools for ticket analytics

## Current File Structure

```text
it_ticket_tracker/
  it_track.py
  database.py
  employee_directory.py
  seed_demo_data.py
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
    login.html
  static/
    css/
      styles.css
```

## Template Notes

The project has the main template files for the current employee, admin, and login workflows.

Current templates:

- `base.html`: Shared layout used by the other pages.
- `home.html`: Current home page.
- `employee_portal.html`: Employee area for checking ticket status, viewing IT replies, and adding requester replies.
- `submit_ticket.html`: Ticket submission form.
- `ticket_success.html`: Confirmation page after a ticket is submitted.
- `admin_dashboard.html`: Admin page for viewing submitted tickets and queue metrics.
- `ticket_detail.html`: Admin page for viewing one ticket, updating admin triage fields, adding employee-visible replies, and adding private internal IT notes.
- `login.html`: Shared demo login page for employee and admin roles.

The home, login, employee portal, submit ticket, ticket success, admin dashboard, and ticket detail templates are connected to active routes right now.

Current active routes:

- `/`: Home page.
- `/login`: Shared demo login page for employee and admin access.
- `/logout`: Clears the current session.
- `/employee`: Employee ticket lookup page.
- `/employee-directory/lookup`: JSON lookup route for the simulated employee directory.
- `/employee/ticket/<id>`: Employee-safe full ticket detail after email verification.
- `/submit`: Employee ticket submission form.
- `/admin`: Admin console for reviewing submitted tickets.
- `/admin/ticket/<id>`: Admin ticket detail page with status, assignee, issue type, priority editing, and private internal IT notes.
- `/admin/ticket/<id>/edit`: Admin-only POST route for status, assignee, issue type, and priority updates.
- `/admin/ticket/<id>/note`: Admin-only POST route for private internal IT notes.
- `/admin/ticket/<id>/reply`: Admin-only POST route for employee-visible replies.
- `/employee/ticket/<id>/reply`: Employee POST route for requester replies after email verification.
- `/health`: Basic health check route.

## Current Login Behavior

The app uses simple Flask session login for demo role separation. This is intentionally beginner-friendly and meant for portfolio demonstration, not production security.

Demo accounts:

```text
Employee username: employee
Employee password: employee123

Admin username: admin
Admin password: admin123
```

Employees see employee navigation for submitting tickets and checking their tickets. Admins see admin navigation for the admin console. Admin-only routes redirect anonymous users to `/login` and return an access message if an employee account tries to open an admin page.

## Current Admin Console Behavior

The `/admin` page now shows submitted tickets from SQLite in a table.

Current admin fields shown:

- Ticket number
- Requester name
- Issue type
- Admin priority
- Status
- Assignee
- Created date/time, displayed without seconds
- View link

Visible timestamps are shortened to date plus hour and minute, while the database keeps the full stored timestamp.

The admin console also shows an admin-only Queue Snapshot with live queue metrics:

- Total tickets
- Open tickets
- In Progress tickets
- Resolved tickets
- Critical suggested tickets
- Most common issue type
- Unassigned open tickets
- Average resolution time

The ticket number and View action both open the admin ticket detail page.

The queue table supports sorting by ticket number, requester, issue, priority, status, assignee, and created date. Clicking a column header toggles the sort direction.

The admin queue also supports searching by ticket number, requester, email, issue type, description keyword, or assignee. Admins can filter by status, priority, issue type, and assignee. The Critical priority filter includes both IT Priority Critical tickets and Smart Critical suggestions. Sorting preserves the current search and filter choices.

The admin dashboard includes beginner-friendly analytics for issue type distribution, assignee workload, and final priority mix. These are displayed as compact dashboard panels instead of a separate reporting page for now.

Future live-search enhancement: the admin search box can update results as the admin types, after a short delay. The current Apply Filters button should stay as the reliable fallback, with live search added as a light JavaScript enhancement rather than replacing the form workflow.

Rows with a Critical smart suggestion receive a subtle red highlight, a red ticket number, and a `Smart Critical` tag beside the current IT priority.

The ticket detail page uses a condensed two-column layout with submitted employee details, employee-visible conversation, and internal notes on the left, plus admin controls in a right-side panel. Admins can update status, assignee, issue type, IT priority, add visible replies for the requester, and add private notes for IT handoffs or troubleshooting context. Internal notes and employee-visible replies submit through their own routes so they do not validate or change admin triage fields.

## Admin Workflow Notes

Current admin ticket editing supports:

- Manual priority changes when IT determines the employee-selected or smart-suggested priority should be raised or lowered.
- Manual issue type changes when the employee chooses the wrong category.
- Status changes from Open to In Progress to Resolved.
- Assignment and reassignment to IT staff.
- Internal/private notes for IT workers only.
- Employee-visible ticket conversation updates for follow-up questions, reset instructions, or safe resolution steps.

Future admin workflow improvements should support:

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

Employee ticket lookup supports ticket number, email address, or both. A ticket number can find one specific ticket and show the full employee-safe details immediately. Email-only search can show a compact list of tickets submitted by that requester. If both are provided, both values must match the saved ticket.

## Current Employee Portal Behavior

The `/employee` page lets employees search for tickets using:

- Ticket number only
- Email address only
- Ticket number and email address together

Ticket number search finds one specific ticket and shows the full ticket details immediately. Email-only search returns a compact list of matching tickets so employees can scan by issue, status, date, and description preview before opening the exact ticket. When both are provided, both values must match the saved ticket.

The employee-facing results show safe ticket details only:

- Ticket number
- Issue type
- Status
- Priority selected by the employee
- Department
- Submitted and updated timestamps, displayed without seconds
- Description
- Employee-visible conversation updates and replies

Internal admin notes and full smart-priority triage details are not shown to employees.

Employees can reply to a ticket conversation from the employee portal. The reply form asks for the requester email and checks that it matches the ticket before saving the message. This is a beginner-friendly stand-in for future login-based identity checks.

The app also calculates a smart priority suggestion. This is currently rule-based, not connected to an AI API. It looks at the issue type and description for high-risk phrases, such as security incidents, suspicious links, unknown downloads, account compromise, or broader business-impact language.

The full smart suggestion is intended for future admin review, not regular employee display. Employees only see a calm urgent-review notice when the rule suggests Critical and the employee selected a lower priority. The smart suggestion does not override the employee-selected priority yet.

## Current Employee Directory Lookup

In a real company, employee email addresses or employee IDs often connect to an internal directory. That directory can provide details such as name, department, title, manager, or location.

For this project, the app simulates that behavior with a small employee directory in `employee_directory.py`. When an employee enters a matching company email address or employee ID on the submit ticket form, the app can fill available details such as name, email, employee ID, and department.

Example:

```text
Employee email: alex.morgan@company.com
Detected department: Accounting
```

If the employee is not found in the directory, the form can still let them enter the department manually.

The lookup also runs on the server during ticket submission. That means the form still works even if the browser JavaScript does not run.

## Demo Data

The project includes `seed_demo_data.py` for local screenshots and testing. It adds sample employees from the simulated directory and creates demo tickets with different issue types, priorities, statuses, assignees, and resolution times.

Run it from the project folder:

```powershell
python seed_demo_data.py
```

The script refreshes existing `[Demo]` tickets before adding the sample set, so it is safe to run again without duplicating the sample data.

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
python it_track.py
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

This project is being built one step at a time. The foundation, login and role separation, ticket submission, database storage, simulated employee directory lookup, employee ticket lookup, admin console, admin triage editing, internal IT notes, employee-visible ticket conversation, admin queue filtering, and admin analytics are now in place.

The next logical workflow step is either critical ticket email notification or live admin search.

Live admin search is also planned as a future user-experience enhancement. The preferred approach is to keep the current Flask filter form working normally, then add JavaScript that waits briefly after typing before updating results.

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
- Condensed admin ticket detail layout with a right-side control panel
- Critical smart-suggestion rows lightly highlighted in the admin queue
- Private internal notes displayed inside the admin ticket detail workflow
- Employee-visible conversation displayed as a simple ticket thread

This direction is intended to feel like a practical internal IT operations console instead of a public marketing website or generic SaaS landing page.

Status badges use green for Open, amber for In Progress, and dark gray for Resolved or Closed states.
