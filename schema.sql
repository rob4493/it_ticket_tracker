CREATE TABLE IF NOT EXISTS tickets (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ticket_number TEXT UNIQUE,
  requester_name TEXT NOT NULL,
  requester_email TEXT NOT NULL,
  requester_employee_id TEXT,
  department TEXT NOT NULL,
  issue_type TEXT NOT NULL,
  user_selected_priority TEXT NOT NULL,
  suggested_priority TEXT NOT NULL,
  priority_reason TEXT NOT NULL,
  final_priority TEXT NOT NULL,
  description TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'Open',
  assigned_to TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  resolved_at TEXT
);

CREATE TABLE IF NOT EXISTS ticket_updates (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ticket_id INTEGER NOT NULL,
  author_name TEXT NOT NULL,
  message TEXT NOT NULL,
  is_internal INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL,
  FOREIGN KEY (ticket_id) REFERENCES tickets (id)
);
