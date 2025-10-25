from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from database import init_db

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Needed for flash messages

# Initialize database
init_db()

@app.route('/')
def index():
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    conn = sqlite3.connect('leave_management.db')
    c = conn.cursor()
    
    # Get stats
    c.execute('SELECT COUNT(*) FROM employees')
    total_employees = c.fetchone()[0]
    
    c.execute('SELECT COUNT(*) FROM leave_requests')
    total_requests = c.fetchone()[0]
    
    c.execute('SELECT COUNT(*) FROM leave_requests WHERE status = "pending"')
    pending_requests = c.fetchone()[0]
    
    # Get recent leave requests
    c.execute('''
        SELECT lr.id, e.name, lr.start_date, lr.end_date, lr.reason, lr.status 
        FROM leave_requests lr 
        JOIN employees e ON lr.employee_id = e.id
        ORDER BY lr.id DESC 
        LIMIT 5
    ''')
    recent_requests = c.fetchall()
    
    conn.close()
    
    return render_template('dashboard.html',
                         total_employees=total_employees,
                         total_requests=total_requests,
                         pending_requests=pending_requests,
                         recent_requests=recent_requests)

# Leave Management Routes
@app.route('/leave_requests')
def view_leave_requests():
    conn = sqlite3.connect('leave_management.db')
    c = conn.cursor()
    
    c.execute('''
        SELECT lr.id, e.name, lr.start_date, lr.end_date, lr.reason, lr.status 
        FROM leave_requests lr 
        JOIN employees e ON lr.employee_id = e.id
        ORDER BY lr.id DESC
    ''')
    leave_requests = c.fetchall()
    
    c.execute('SELECT id, name FROM employees')
    employees = c.fetchall()
    
    conn.close()
    
    return render_template('leave_requests.html', 
                         leave_requests=leave_requests, 
                         employees=employees)

@app.route('/add_leave_request', methods=['POST'])
def add_leave_request():
    employee_id = request.form['employee_id']
    start_date = request.form['start_date']
    end_date = request.form['end_date']
    reason = request.form['reason']
    
    conn = sqlite3.connect('leave_management.db')
    c = conn.cursor()
    
    c.execute('''
        INSERT INTO leave_requests (employee_id, start_date, end_date, reason, status)
        VALUES (?, ?, ?, ?, 'pending')
    ''', (employee_id, start_date, end_date, reason))
    
    conn.commit()
    conn.close()
    
    flash('Leave request submitted successfully!', 'success')
    return redirect(url_for('view_leave_requests'))

@app.route('/update_status/<int:request_id>/<status>')
def update_status(request_id, status):
    conn = sqlite3.connect('leave_management.db')
    c = conn.cursor()
    
    c.execute('UPDATE leave_requests SET status = ? WHERE id = ?', (status, request_id))
    
    conn.commit()
    conn.close()
    
    flash(f'Leave request {status} successfully!', 'success')
    return redirect(url_for('view_leave_requests'))

# Employee Management Routes
@app.route('/employees')
def view_employees():
    conn = sqlite3.connect('leave_management.db')
    c = conn.cursor()
    
    c.execute('SELECT id, name, email FROM employees ORDER BY id')
    employees = c.fetchall()
    conn.close()
    
    return render_template('employees.html', employees=employees)

@app.route('/add_employee', methods=['POST'])
def add_employee():
    name = request.form['name']
    email = request.form['email']
    
    conn = sqlite3.connect('leave_management.db')
    c = conn.cursor()
    
    try:
        c.execute('INSERT INTO employees (name, email) VALUES (?, ?)', (name, email))
        conn.commit()
        flash('Employee added successfully!', 'success')
    except sqlite3.IntegrityError:
        flash('Error: An employee with this email already exists.', 'error')
    except Exception as e:
        flash(f'Error: {e}', 'error')
    
    conn.close()
    return redirect(url_for('view_employees'))

@app.route('/delete_employee/<int:employee_id>')
def delete_employee(employee_id):
    conn = sqlite3.connect('leave_management.db')
    c = conn.cursor()
    
    try:
        # First check if employee has leave requests
        c.execute('SELECT COUNT(*) FROM leave_requests WHERE employee_id = ?', (employee_id,))
        leave_count = c.fetchone()[0]
        
        if leave_count > 0:
            # Delete leave requests first
            c.execute('DELETE FROM leave_requests WHERE employee_id = ?', (employee_id,))
        
        # Then delete the employee
        c.execute('DELETE FROM employees WHERE id = ?', (employee_id,))
        conn.commit()
        flash('Employee deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting employee: {e}', 'error')
    
    conn.close()
    return redirect(url_for('view_employees'))

if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=5000)