EMPLOYEE_DIRECTORY = [
    {
        "name": "Alex Morgan",
        "email": "alex.morgan@company.com",
        "employee_id": "E1001",
        "department": "Accounting",
        "title": "Staff Accountant",
        "location": "Headquarters",
    },
    {
        "name": "Jordan Lee",
        "email": "jordan.lee@company.com",
        "employee_id": "E1002",
        "department": "Human Resources",
        "title": "HR Coordinator",
        "location": "Headquarters",
    },
    {
        "name": "Taylor Smith",
        "email": "taylor.smith@company.com",
        "employee_id": "E1003",
        "department": "Sales",
        "title": "Account Executive",
        "location": "Remote",
    },
    {
        "name": "Casey Patel",
        "email": "casey.patel@company.com",
        "employee_id": "E1004",
        "department": "Operations",
        "title": "Operations Analyst",
        "location": "Warehouse",
    },
    {
        "name": "Morgan Rivera",
        "email": "morgan.rivera@company.com",
        "employee_id": "E1005",
        "department": "Information Technology",
        "title": "Systems Technician",
        "location": "Headquarters",
    },
    {
        "name": "Riley Chen",
        "email": "riley.chen@company.com",
        "employee_id": "E1006",
        "department": "Marketing",
        "title": "Marketing Specialist",
        "location": "Remote",
    },
    {
        "name": "Jamie Brooks",
        "email": "jamie.brooks@company.com",
        "employee_id": "E1007",
        "department": "Customer Support",
        "title": "Support Lead",
        "location": "Headquarters",
    },
    {
        "name": "Drew Wilson",
        "email": "drew.wilson@company.com",
        "employee_id": "E1008",
        "department": "Finance",
        "title": "Financial Analyst",
        "location": "Headquarters",
    },
    {
        "name": "Avery Johnson",
        "email": "avery.johnson@company.com",
        "employee_id": "E1009",
        "department": "Legal",
        "title": "Legal Assistant",
        "location": "Headquarters",
    },
    {
        "name": "Quinn Davis",
        "email": "quinn.davis@company.com",
        "employee_id": "E1010",
        "department": "Product",
        "title": "Product Coordinator",
        "location": "Remote",
    },
    {
        "name": "Sam Carter",
        "email": "sam.carter@company.com",
        "employee_id": "E1011",
        "department": "Engineering",
        "title": "Software Engineer",
        "location": "Remote",
    },
    {
        "name": "Parker Evans",
        "email": "parker.evans@company.com",
        "employee_id": "E1012",
        "department": "Facilities",
        "title": "Facilities Coordinator",
        "location": "Warehouse",
    },
    {
        "name": "Skyler Nguyen",
        "email": "skyler.nguyen@company.com",
        "employee_id": "E1013",
        "department": "Sales",
        "title": "Sales Operations Analyst",
        "location": "Headquarters",
    },
    {
        "name": "Harper Martinez",
        "email": "harper.martinez@company.com",
        "employee_id": "E1014",
        "department": "Executive",
        "title": "Executive Assistant",
        "location": "Headquarters",
    },
    {
        "name": "Reese Thompson",
        "email": "reese.thompson@company.com",
        "employee_id": "E1015",
        "department": "Training",
        "title": "Learning Specialist",
        "location": "Remote",
    },
    {
        "name": "Cameron White",
        "email": "cameron.white@company.com",
        "employee_id": "E1016",
        "department": "Purchasing",
        "title": "Procurement Coordinator",
        "location": "Headquarters",
    },
]


def find_employee_record(email="", employee_id=""):
    email = email.strip().lower()
    employee_id = employee_id.strip().upper()

    if not email and not employee_id:
        return None

    for employee in EMPLOYEE_DIRECTORY:
        if email and employee["email"].lower() == email:
            return employee

        if employee_id and employee["employee_id"].upper() == employee_id:
            return employee

    return None


def public_employee_record(employee):
    if employee is None:
        return None

    return {
        "name": employee["name"],
        "email": employee["email"],
        "employee_id": employee["employee_id"],
        "department": employee["department"],
        "title": employee["title"],
        "location": employee["location"],
    }
