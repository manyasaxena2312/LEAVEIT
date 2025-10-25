import sqlite3

def init_db():
    conn = sqlite3.connect('leave_management.db')
    c = conn.cursor()
    
    # Create employees table
    c.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL
        )
    ''')
    
    # Create leave_requests table
    c.execute('''
        CREATE TABLE IF NOT EXISTS leave_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            reason TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            FOREIGN KEY (employee_id) REFERENCES employees (id)
        )
    ''')
    
    # Insert sample employees
    sample_employees = [
        ('John Doe', 'john@company.com'),
        ('Jane Smith', 'jane@company.com'),
        ('Mike Johnson', 'mike@company.com')
    ]
    
    for employee in sample_employees:
        try:
            c.execute('INSERT OR IGNORE INTO employees (name, email) VALUES (?, ?)', employee)
        except:
            pass
    
    conn.commit()
    conn.close()
    print("Database initialized successfully!")

if __name__ == '__main__':
    init_db()