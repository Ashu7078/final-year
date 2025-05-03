import sqlite3
import pandas as pd
import os
from datetime import datetime, timedelta
import streamlit as st

# Get the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(current_dir, 'ems.db')

def get_connection():
    """Get a connection to the SQLite database"""
    try:
        conn = sqlite3.connect(DB_PATH)
        return conn
    except sqlite3.Error as e:
        st.error(f"Database connection error: {e}")
        return None
        
def delete_employee(employee_id):
    """Delete an employee and their user account if exists"""
    conn = get_connection()
    if not conn:
        return False
    
    cursor = conn.cursor()
    
    try:
        # First get the user_id if any
        cursor.execute("SELECT user_id FROM employees WHERE id = ?", (employee_id,))
        result = cursor.fetchone()
        
        if not result:
            return False
            
        user_id = result[0]
        
        # Start transaction
        conn.execute("BEGIN TRANSACTION")
        
        # Delete related records
        # 1. Delete leave requests
        cursor.execute("DELETE FROM leave_requests WHERE employee_id = ?", (employee_id,))
        
        # 2. Delete inquiries
        cursor.execute("DELETE FROM inquiries WHERE employee_id = ?", (employee_id,))
        
        # 3. Delete leave balance
        cursor.execute("DELETE FROM leave_balance WHERE employee_id = ?", (employee_id,))
        
        # 4. Delete notifications
        if user_id:
            cursor.execute("DELETE FROM notifications WHERE user_id = ?", (user_id,))
        
        # 5. Delete the employee record
        cursor.execute("DELETE FROM employees WHERE id = ?", (employee_id,))
        
        # 6. Delete the user account if it exists
        if user_id:
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        
        conn.commit()
        success = True
    except sqlite3.Error as e:
        st.error(f"Error deleting employee: {e}")
        conn.rollback()
        success = False
    
    conn.close()
    return success
    
def delete_department(department_name):
    """Delete a department and reassign employees to default department"""
    conn = get_connection()
    if not conn:
        return False
    
    cursor = conn.cursor()
    
    try:
        # Start transaction
        conn.execute("BEGIN TRANSACTION")
        
        # Check if the department exists
        cursor.execute("SELECT COUNT(*) FROM employees WHERE department = ?", (department_name,))
        count = cursor.fetchone()[0]
        
        if count == 0:
            # If no employees in this department, still return success
            conn.commit()
            return True
        
        # Reassign employees to default department
        cursor.execute(
            """
            UPDATE employees 
            SET department = 'Unassigned', updated_at = datetime('now')
            WHERE department = ?
            """, 
            (department_name,)
        )
        
        # Log this action
        st.write(f"DEBUG: Updated {cursor.rowcount} employees from department {department_name} to Unassigned")
        
        conn.commit()
        success = True
    except sqlite3.Error as e:
        st.error(f"Error deleting department: {e}")
        conn.rollback()
        success = False
    
    conn.close()
    return success

def init_database():
    """Initialize database with required tables if they don't exist"""
    conn = get_connection()
    if not conn:
        return False
    
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'employee',
        last_login DATETIME,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create employees table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        email TEXT UNIQUE,
        phone TEXT,
        department TEXT,
        position TEXT,
        join_date DATE,
        birth_date DATE,
        address TEXT,
        manager_id INTEGER,
        status TEXT DEFAULT 'active',
        profile_picture TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (manager_id) REFERENCES employees(id)
    )
    ''')
    
    # Create leave_requests table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS leave_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER NOT NULL,
        leave_type TEXT NOT NULL,
        start_date DATE NOT NULL,
        end_date DATE NOT NULL,
        days_count REAL NOT NULL,
        reason TEXT,
        status TEXT DEFAULT 'pending',
        approved_by INTEGER,
        response_message TEXT,
        response_date DATETIME,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (employee_id) REFERENCES employees(id),
        FOREIGN KEY (approved_by) REFERENCES employees(id)
    )
    ''')
    
    # Create leave_balance table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS leave_balance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER NOT NULL,
        year INTEGER NOT NULL,
        annual_leave_total INTEGER DEFAULT 20,
        annual_leave_used INTEGER DEFAULT 0,
        sick_leave_total INTEGER DEFAULT 10,
        sick_leave_used INTEGER DEFAULT 0,
        personal_leave_total INTEGER DEFAULT 5,
        personal_leave_used INTEGER DEFAULT 0,
        maternity_leave_total INTEGER DEFAULT 0,
        maternity_leave_used INTEGER DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME,
        FOREIGN KEY (employee_id) REFERENCES employees(id),
        UNIQUE(employee_id, year)
    )
    ''')
    
    # Create inquiries table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS inquiries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER NOT NULL,
        subject TEXT NOT NULL,
        message TEXT NOT NULL,
        status TEXT DEFAULT 'pending',
        response TEXT,
        response_date DATETIME,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (employee_id) REFERENCES employees(id)
    )
    ''')
    
    # Create notifications table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        message TEXT NOT NULL,
        is_read INTEGER DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    ''')
    
    # Add some default data if tables are empty
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    
    if user_count == 0:
        # Add admin user
        cursor.execute('''
        INSERT INTO users (username, password, role) 
        VALUES ('admin', 'admin123', 'admin')
        ''')
        
        admin_id = cursor.lastrowid
        
        # Add admin employee
        cursor.execute('''
        INSERT INTO employees (user_id, first_name, last_name, email, department, position, join_date) 
        VALUES (?, 'Admin', 'User', 'admin@example.com', 'Management', 'Administrator', '2022-01-01')
        ''', (admin_id,))
        
        admin_emp_id = cursor.lastrowid
        
        # Add test employee user
        cursor.execute('''
        INSERT INTO users (username, password, role) 
        VALUES ('employee', 'pass123', 'employee')
        ''')
        
        emp_id = cursor.lastrowid
        
        # Add test employee
        cursor.execute('''
        INSERT INTO employees (user_id, first_name, last_name, email, department, position, join_date, phone, address, status) 
        VALUES (?, 'John', 'Doe', 'john.doe@example.com', 'Engineering', 'Software Engineer', '2023-03-15', '+1-555-123-4567', '123 Tech Lane, San Francisco, CA 94107', 'Active')
        ''', (emp_id,))
        
        employee_id = cursor.lastrowid
        
        # Add more demo employees
        # Employee 2
        cursor.execute('''
        INSERT INTO employees (first_name, last_name, email, department, position, join_date, phone, address, status) 
        VALUES ('Emma', 'Smith', 'emma.smith@example.com', 'Human Resources', 'HR Manager', '2021-08-12', '+1-555-234-5678', '456 HR Avenue, New York, NY 10001', 'Active')
        ''')
        
        # Employee 3
        cursor.execute('''
        INSERT INTO employees (first_name, last_name, email, department, position, join_date, phone, address, status) 
        VALUES ('Michael', 'Johnson', 'michael.j@example.com', 'Marketing', 'Marketing Specialist', '2022-05-23', '+1-555-345-6789', '789 Market St, Chicago, IL 60601', 'Active')
        ''')
        
        # Employee 4
        cursor.execute('''
        INSERT INTO employees (first_name, last_name, email, department, position, join_date, phone, address, status) 
        VALUES ('Sarah', 'Williams', 'sarah.w@example.com', 'Finance', 'Financial Analyst', '2020-11-05', '+1-555-456-7890', '321 Money Lane, Boston, MA 02108', 'Active')
        ''')
        
        # Employee 5
        cursor.execute('''
        INSERT INTO employees (first_name, last_name, email, department, position, join_date, phone, address, status) 
        VALUES ('David', 'Brown', 'david.b@example.com', 'Engineering', 'Senior Developer', '2019-07-18', '+1-555-567-8901', '654 Code Street, Seattle, WA 98101', 'Active')
        ''')
        
        # Employee 6
        cursor.execute('''
        INSERT INTO employees (first_name, last_name, email, department, position, join_date, phone, address, status, manager_id) 
        VALUES ('Jennifer', 'Miller', 'jennifer.m@example.com', 'Engineering', 'QA Engineer', '2023-01-10', '+1-555-678-9012', '987 Test Ave, Austin, TX 78701', 'Active', ?)
        ''', (employee_id,))
        
        # Employee 7 (Inactive)
        cursor.execute('''
        INSERT INTO employees (first_name, last_name, email, department, position, join_date, phone, address, status) 
        VALUES ('Robert', 'Garcia', 'robert.g@example.com', 'Sales', 'Sales Manager', '2018-09-01', '+1-555-789-0123', '246 Sell Street, Miami, FL 33101', 'Inactive')
        ''')
        
        # Add leave balance for all employees
        current_year = datetime.now().year
        for emp_id in range(1, 8):
            cursor.execute('''
            INSERT INTO leave_balance (employee_id, year)
            VALUES (?, ?)
            ''', (emp_id, current_year))
            
        # Add some sample leave requests
        # Approved leave
        cursor.execute('''
        INSERT INTO leave_requests (employee_id, leave_type, start_date, end_date, days_count, reason, status, approved_by, response_message)
        VALUES (2, 'Annual Leave', '2025-05-20', '2025-05-22', 3, 'Family vacation', 'approved', ?, 'Approved. Enjoy your vacation!')
        ''', (admin_emp_id,))
        
        # Pending leave
        cursor.execute('''
        INSERT INTO leave_requests (employee_id, leave_type, start_date, end_date, days_count, reason)
        VALUES (3, 'Sick Leave', '2025-05-15', '2025-05-16', 2, 'Doctor appointment')
        ''')
        
        # Rejected leave
        cursor.execute('''
        INSERT INTO leave_requests (employee_id, leave_type, start_date, end_date, days_count, reason, status, approved_by, response_message)
        VALUES (4, 'Personal Leave', '2025-06-01', '2025-06-03', 3, 'Personal matter', 'rejected', ?, 'Critical project deadline during this period.')
        ''', (admin_emp_id,))
        
        # Add some sample inquiries
        cursor.execute('''
        INSERT INTO inquiries (employee_id, subject, message, status)
        VALUES (2, 'Salary Question', 'When will the annual salary review happen?', 'pending')
        ''')
        
        cursor.execute('''
        INSERT INTO inquiries (employee_id, subject, message, status, response, response_date)
        VALUES (3, 'Training Request', 'I would like to attend the upcoming AWS certification training.', 'resolved', 'Your request has been approved. Please check your email for registration details.', datetime('now', '-2 days'))
        ''')
        
        # Add some sample notifications
        cursor.execute('''
        INSERT INTO notifications (user_id, title, message)
        VALUES (?, 'Welcome to EMS', 'Welcome to the Employee Management System. This is your dashboard where you can manage all employee-related tasks.')
        ''', (admin_id,))
        
        cursor.execute('''
        INSERT INTO notifications (user_id, title, message)
        VALUES (?, 'Profile Update Required', 'Please update your profile information including your current address and phone number.')
        ''', (emp_id,))
    
    conn.commit()
    conn.close()
    return True

# User authentication functions
def authenticate_user(username, password):
    """Authenticate user with username and password"""
    conn = get_connection()
    if not conn:
        return None
    
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, role FROM users WHERE username = ? AND password = ?",
        (username, password)
    )
    
    user = cursor.fetchone()
    
    if user:
        # Update last login
        cursor.execute(
            "UPDATE users SET last_login = datetime('now') WHERE id = ?",
            (user[0],)
        )
        conn.commit()
        
        # Return user ID and role
        result = {"id": user[0], "role": user[1]}
    else:
        result = None
    
    conn.close()
    return result

# Employee functions
def get_employee_profile(user_id):
    """Get employee profile by user ID"""
    conn = get_connection()
    if not conn:
        return None
    
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT e.id, e.first_name, e.last_name, e.email, e.phone, e.department, 
        e.position, e.join_date, e.birth_date, e.address, e.status, 
        m.first_name || ' ' || m.last_name as manager_name, e.profile_picture
        FROM employees e
        LEFT JOIN employees m ON e.manager_id = m.id
        WHERE e.user_id = ?
        """,
        (user_id,)
    )
    
    employee = cursor.fetchone()
    conn.close()
    
    if employee:
        return {
            "id": employee[0],
            "first_name": employee[1],
            "last_name": employee[2],
            "email": employee[3],
            "phone": employee[4],
            "department": employee[5],
            "position": employee[6],
            "join_date": employee[7],
            "birth_date": employee[8],
            "address": employee[9],
            "status": employee[10],
            "manager_name": employee[11],
            "profile_picture": employee[12]
        }
    else:
        return None

def get_all_employees():
    """Get all employees"""
    conn = get_connection()
    if not conn:
        return []
    
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT e.id, e.first_name, e.last_name, e.email, e.phone, e.department, 
        e.position, e.join_date, e.status, e.address, e.profile_picture,
        u.role, e.user_id
        FROM employees e
        LEFT JOIN users u ON e.user_id = u.id
        ORDER BY e.last_name, e.first_name
        """
    )
    
    employees = []
    for row in cursor.fetchall():
        employees.append({
            "id": row[0],
            "first_name": row[1],
            "last_name": row[2],
            "email": row[3],
            "phone": row[4],
            "department": row[5],
            "position": row[6],
            "join_date": row[7],
            "status": row[8],
            "address": row[9],
            "profile_picture": row[10],
            "role": row[11] if row[11] else "employee",
            "user_id": row[12]
        })
    
    conn.close()
    return employees

def add_employee(data):
    """Add a new employee"""
    conn = get_connection()
    if not conn:
        return {"success": False, "message": "Database connection error"}
    
    cursor = conn.cursor()
    
    try:
        # Begin transaction
        conn.execute("BEGIN")
        
        # Check if email already exists
        cursor.execute("SELECT id FROM employees WHERE email = ?", (data['email'],))
        if cursor.fetchone():
            conn.rollback()
            conn.close()
            return {"success": False, "message": "Email already exists"}
        
        # Create user account if needed (optional)
        user_id = None
        if 'create_account' in data and data['create_account']:
            # Generate username from email or first_name.last_name
            if 'email' in data and data['email']:
                username = data['email'].split('@')[0]
            else:
                username = f"{data['first_name'].lower()}.{data['last_name'].lower()}"
                
            # Generate a random password
            import random
            import string
            password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
            
            # Check if username exists
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            if cursor.fetchone():
                # Add a random number to make it unique
                username = f"{username}{random.randint(100, 999)}"
            
            # Insert user
            cursor.execute(
                "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                (username, password, 'employee')
            )
            user_id = cursor.lastrowid
        
        # Insert employee with or without user_id
        if user_id:
            cursor.execute(
                """
                INSERT INTO employees 
                (user_id, first_name, last_name, email, phone, department, position, 
                join_date, status, address, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
                """,
                (
                    user_id,
                    data['first_name'],
                    data['last_name'],
                    data['email'],
                    data.get('phone', None),
                    data.get('department', None),
                    data.get('position', None),
                    data.get('join_date', datetime.now().strftime('%Y-%m-%d')),
                    data.get('status', 'Active'),
                    data.get('address', None)
                )
            )
        else:
            cursor.execute(
                """
                INSERT INTO employees 
                (first_name, last_name, email, phone, department, position, 
                join_date, status, address, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
                """,
                (
                    data['first_name'],
                    data['last_name'],
                    data['email'],
                    data.get('phone', None),
                    data.get('department', None),
                    data.get('position', None),
                    data.get('join_date', datetime.now().strftime('%Y-%m-%d')),
                    data.get('status', 'Active'),
                    data.get('address', None)
                )
            )
        
        employee_id = cursor.lastrowid
        
        # Add profile picture if provided
        if 'profile_picture' in data and data['profile_picture']:
            cursor.execute(
                """
                UPDATE employees 
                SET profile_picture = ?
                WHERE id = ?
                """,
                (data['profile_picture'], employee_id)
            )
        
        # Setup initial leave balance for current year
        current_year = datetime.now().year
        cursor.execute(
            """
            INSERT INTO leave_balance 
            (employee_id, year, annual_leave_total, sick_leave_total, personal_leave_total)
            VALUES (?, ?, 20, 10, 5)
            """,
            (employee_id, current_year)
        )
        
        # Commit transaction
        conn.commit()
        
        # Return result
        result = {
            "success": True,
            "employee_id": employee_id,
            "message": "Employee added successfully"
        }
        
        # Add user account details if created
        if user_id:
            result["user_account"] = {
                "username": username,
                "password": password
            }
        
    except sqlite3.Error as e:
        conn.rollback()
        result = {"success": False, "message": str(e)}
    
    conn.close()
    return result

def update_employee_profile(employee_id, data):
    """Update employee profile with given data"""
    conn = get_connection()
    if not conn:
        return False
    
    cursor = conn.cursor()
    
    try:
        # Check if we're only updating the profile picture
        if 'profile_picture' in data and len(data) == 1:
            cursor.execute(
                """
                UPDATE employees SET
                profile_picture = ?,
                updated_at = datetime('now')
                WHERE id = ?
                """,
                (data['profile_picture'], employee_id)
            )
        else:
            # Regular profile update
            update_fields = []
            update_values = []
            
            # Check which fields are present in data and add them to the update
            if 'first_name' in data:
                update_fields.append("first_name = ?")
                update_values.append(data['first_name'])
                
            if 'last_name' in data:
                update_fields.append("last_name = ?")
                update_values.append(data['last_name'])
                
            if 'email' in data:
                update_fields.append("email = ?")
                update_values.append(data['email'])
                
            if 'phone' in data:
                update_fields.append("phone = ?")
                update_values.append(data['phone'])
                
            if 'department' in data:
                update_fields.append("department = ?")
                update_values.append(data['department'])
                
            if 'position' in data:
                update_fields.append("position = ?")
                update_values.append(data['position'])
                
            if 'address' in data:
                update_fields.append("address = ?")
                update_values.append(data['address'])
                
            if 'status' in data:
                update_fields.append("status = ?")
                update_values.append(data['status'])
                
            if 'profile_picture' in data:
                update_fields.append("profile_picture = ?")
                update_values.append(data['profile_picture'])
            
            # Add the updated_at timestamp and employee_id
            update_fields.append("updated_at = datetime('now')")
            update_values.append(employee_id)
            
            # Execute the update query
            if update_fields:
                query = f"""
                UPDATE employees SET
                {", ".join(update_fields)}
                WHERE id = ?
                """
                cursor.execute(query, update_values)
        
        conn.commit()
        success = True
    except sqlite3.Error as e:
        st.error(f"Error updating profile: {e}")
        success = False
    
    conn.close()
    return success

# Leave management functions
def get_employee_leave_balance(employee_id, year=None):
    """Get leave balance for an employee"""
    if year is None:
        year = datetime.now().year
    
    conn = get_connection()
    if not conn:
        return None
    
    cursor = conn.cursor()
    
    # Check if record exists for this year
    cursor.execute(
        "SELECT COUNT(*) FROM leave_balance WHERE employee_id = ? AND year = ?",
        (employee_id, year)
    )
    count = cursor.fetchone()[0]
    
    # Create record if it doesn't exist
    if count == 0:
        try:
            cursor.execute(
                """
                INSERT INTO leave_balance 
                (employee_id, year, annual_leave_total, sick_leave_total, personal_leave_total)
                VALUES (?, ?, 20, 10, 5)
                """,
                (employee_id, year)
            )
            conn.commit()
        except sqlite3.Error as e:
            st.error(f"Error creating leave balance: {e}")
            conn.close()
            return None
    
    # Get the leave balance
    cursor.execute(
        """
        SELECT annual_leave_total, annual_leave_used, sick_leave_total, sick_leave_used,
        personal_leave_total, personal_leave_used, maternity_leave_total, maternity_leave_used
        FROM leave_balance
        WHERE employee_id = ? AND year = ?
        """,
        (employee_id, year)
    )
    
    balance = cursor.fetchone()
    conn.close()
    
    if balance:
        return {
            "annual_leave_total": balance[0],
            "annual_leave_used": balance[1],
            "sick_leave_total": balance[2],
            "sick_leave_used": balance[3],
            "personal_leave_total": balance[4],
            "personal_leave_used": balance[5],
            "maternity_leave_total": balance[6],
            "maternity_leave_used": balance[7]
        }
    else:
        return None

def submit_leave_request(employee_id, leave_type, start_date, end_date, reason):
    """Submit a new leave request"""
    conn = get_connection()
    if not conn:
        return False
    
    cursor = conn.cursor()
    
    try:
        # Calculate days count
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        days_count = (end - start).days + 1
        
        cursor.execute(
            """
            INSERT INTO leave_requests 
            (employee_id, leave_type, start_date, end_date, days_count, reason)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (employee_id, leave_type, start_date, end_date, days_count, reason)
        )
        
        conn.commit()
        
        # Add notification for admin users
        cursor.execute("SELECT id FROM users WHERE role = 'admin'")
        admin_ids = cursor.fetchall()
        
        for admin_id in admin_ids:
            add_notification(
                admin_id[0],
                "New Leave Request",
                f"A new leave request has been submitted by an employee."
            )
        
        success = True
    except sqlite3.Error as e:
        st.error(f"Error submitting leave request: {e}")
        success = False
    
    conn.close()
    return success

def get_leave_requests(employee_id=None, status=None):
    """Get leave requests with optional filters"""
    conn = get_connection()
    if not conn:
        return []
    
    cursor = conn.cursor()
    
    query = """
    SELECT lr.id, lr.employee_id, e.first_name || ' ' || e.last_name as employee_name,
    lr.leave_type, lr.start_date, lr.end_date, lr.days_count, lr.reason, lr.status,
    lr.approved_by, lr.response_message, lr.response_date, lr.created_at,
    e.department
    FROM leave_requests lr
    JOIN employees e ON lr.employee_id = e.id
    """
    
    params = []
    
    if employee_id:
        query += " WHERE lr.employee_id = ?"
        params.append(employee_id)
        
        if status:
            query += " AND lr.status = ?"
            params.append(status)
    elif status:
        query += " WHERE lr.status = ?"
        params.append(status)
    
    query += " ORDER BY lr.created_at DESC"
    
    cursor.execute(query, params)
    
    requests = []
    for row in cursor.fetchall():
        requests.append({
            "id": row[0],
            "employee_id": row[1],
            "employee_name": row[2],
            "leave_type": row[3],
            "start_date": row[4],
            "end_date": row[5],
            "days_count": row[6],
            "reason": row[7],
            "status": row[8],
            "approved_by": row[9],
            "response_message": row[10],
            "response_date": row[11],
            "created_at": row[12],
            "department": row[13]
        })
    
    conn.close()
    return requests

def approve_leave_request(request_id, admin_id, response=""):
    """Approve a leave request"""
    conn = get_connection()
    if not conn:
        return False
    
    cursor = conn.cursor()
    
    try:
        # Get leave request details
        cursor.execute(
            """
            SELECT employee_id, leave_type, days_count
            FROM leave_requests
            WHERE id = ?
            """,
            (request_id,)
        )
        request = cursor.fetchone()
        
        if not request:
            conn.close()
            return False
        
        employee_id, leave_type, days_count = request
        
        # Update request status
        cursor.execute(
            """
            UPDATE leave_requests
            SET status = 'approved', approved_by = ?, response_message = ?, response_date = datetime('now')
            WHERE id = ?
            """,
            (admin_id, response or "Your leave request has been approved.", request_id)
        )
        
        # Update leave balance
        current_year = datetime.now().year
        
        # Map leave type to database column
        leave_column = None
        if leave_type == "Annual Leave":
            leave_column = "annual_leave_used"
        elif leave_type == "Sick Leave":
            leave_column = "sick_leave_used"
        elif leave_type == "Personal Leave":
            leave_column = "personal_leave_used"
        elif leave_type == "Maternity/Paternity Leave":
            leave_column = "maternity_leave_used"
        
        # Update leave balance if not unpaid leave
        if leave_column and leave_type != "Unpaid Leave":
            cursor.execute(
                f"""
                UPDATE leave_balance
                SET {leave_column} = {leave_column} + ?
                WHERE employee_id = ? AND year = ?
                """,
                (days_count, employee_id, current_year)
            )
        
        # Get user_id for notification
        cursor.execute("SELECT user_id FROM employees WHERE id = ?", (employee_id,))
        user_id = cursor.fetchone()[0]
        
        # Add notification
        add_notification(
            user_id,
            "Leave Request Approved",
            f"Your {leave_type} request has been approved."
        )
        
        conn.commit()
        success = True
    except sqlite3.Error as e:
        st.error(f"Error approving leave request: {e}")
        success = False
    
    conn.close()
    return success

def reject_leave_request(request_id, admin_id, response):
    """Reject a leave request"""
    conn = get_connection()
    if not conn:
        return False
    
    cursor = conn.cursor()
    
    try:
        # Get employee ID for notification
        cursor.execute(
            """
            SELECT employee_id, leave_type 
            FROM leave_requests
            WHERE id = ?
            """,
            (request_id,)
        )
        result = cursor.fetchone()
        
        if not result:
            conn.close()
            return False
            
        employee_id, leave_type = result
        
        # Update request status
        cursor.execute(
            """
            UPDATE leave_requests
            SET status = 'rejected', approved_by = ?, response_message = ?, response_date = datetime('now')
            WHERE id = ?
            """,
            (admin_id, response, request_id)
        )
        
        # Get user_id for notification
        cursor.execute("SELECT user_id FROM employees WHERE id = ?", (employee_id,))
        user_id = cursor.fetchone()[0]
        
        # Add notification
        add_notification(
            user_id,
            "Leave Request Rejected",
            f"Your {leave_type} request has been rejected."
        )
        
        conn.commit()
        success = True
    except sqlite3.Error as e:
        st.error(f"Error rejecting leave request: {e}")
        success = False
    
    conn.close()
    return success

def get_leave_statistics():
    """Get leave statistics for admin dashboard"""
    conn = get_connection()
    if not conn:
        return {}
    
    cursor = conn.cursor()
    
    stats = {}
    
    # Status counts
    cursor.execute(
        """
        SELECT status, COUNT(*) as count
        FROM leave_requests
        GROUP BY status
        """
    )
    stats['status_counts'] = [{"status": row[0], "count": row[1]} for row in cursor.fetchall()]
    
    # Type counts
    cursor.execute(
        """
        SELECT leave_type, COUNT(*) as count
        FROM leave_requests
        GROUP BY leave_type
        """
    )
    stats['type_counts'] = [{"leave_type": row[0], "count": row[1]} for row in cursor.fetchall()]
    
    # Monthly counts (current year)
    cursor.execute(
        """
        SELECT 
            strftime('%Y', created_at) as year,
            strftime('%m', created_at) as month,
            COUNT(*) as count
        FROM leave_requests
        WHERE strftime('%Y', created_at) = strftime('%Y', 'now')
        GROUP BY year, month
        ORDER BY year, month
        """
    )
    stats['monthly_counts'] = [{"year": row[0], "month": row[1], "count": row[2]} for row in cursor.fetchall()]
    
    # Department counts
    cursor.execute(
        """
        SELECT e.department, COUNT(*) as count
        FROM leave_requests lr
        JOIN employees e ON lr.employee_id = e.id
        GROUP BY e.department
        """
    )
    stats['department_counts'] = [{"department": row[0] or "Not Specified", "count": row[1]} for row in cursor.fetchall()]
    
    conn.close()
    return stats

# Inquiry management functions
def get_inquiries(employee_id=None):
    """Get inquiries with optional employee filter"""
    conn = get_connection()
    if not conn:
        return []
    
    cursor = conn.cursor()
    
    query = """
    SELECT i.id, i.employee_id, e.first_name || ' ' || e.last_name as employee_name,
    i.subject, i.message, i.status, i.response, i.response_date, i.created_at
    FROM inquiries i
    JOIN employees e ON i.employee_id = e.id
    """
    
    params = []
    
    if employee_id:
        query += " WHERE i.employee_id = ?"
        params.append(employee_id)
    
    query += " ORDER BY i.created_at DESC"
    
    cursor.execute(query, params)
    
    inquiries = []
    for row in cursor.fetchall():
        inquiries.append({
            "id": row[0],
            "employee_id": row[1],
            "employee_name": row[2],
            "subject": row[3],
            "message": row[4],
            "status": row[5],
            "response": row[6],
            "response_date": row[7],
            "created_at": row[8]
        })
    
    conn.close()
    return inquiries

def add_inquiry(employee_id, subject, message):
    """Add a new inquiry"""
    conn = get_connection()
    if not conn:
        return False
    
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            """
            INSERT INTO inquiries (employee_id, subject, message)
            VALUES (?, ?, ?)
            """,
            (employee_id, subject, message)
        )
        
        conn.commit()
        
        # Add notification for admin users
        cursor.execute("SELECT id FROM users WHERE role = 'admin'")
        admin_ids = cursor.fetchall()
        
        for admin_id in admin_ids:
            add_notification(
                admin_id[0],
                "New Inquiry",
                f"A new inquiry has been submitted: {subject}"
            )
        
        success = True
    except sqlite3.Error as e:
        st.error(f"Error adding inquiry: {e}")
        success = False
    
    conn.close()
    return success

def respond_to_inquiry(inquiry_id, response):
    """Respond to an inquiry"""
    conn = get_connection()
    if not conn:
        return False
    
    cursor = conn.cursor()
    
    try:
        # Get employee info for notification
        cursor.execute(
            """
            SELECT i.employee_id, i.subject, e.user_id
            FROM inquiries i
            JOIN employees e ON i.employee_id = e.id
            WHERE i.id = ?
            """,
            (inquiry_id,)
        )
        result = cursor.fetchone()
        
        if not result:
            conn.close()
            return False
            
        employee_id, subject, user_id = result
        
        # Update inquiry
        cursor.execute(
            """
            UPDATE inquiries
            SET status = 'resolved', response = ?, response_date = datetime('now')
            WHERE id = ?
            """,
            (response, inquiry_id)
        )
        
        # Add notification
        add_notification(
            user_id,
            "Inquiry Response",
            f"Your inquiry '{subject}' has been answered."
        )
        
        conn.commit()
        success = True
    except sqlite3.Error as e:
        st.error(f"Error responding to inquiry: {e}")
        success = False
    
    conn.close()
    return success

# Notification functions
def add_notification(user_id, title, message):
    """Add a notification for a user"""
    conn = get_connection()
    if not conn:
        return False
    
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            """
            INSERT INTO notifications (user_id, title, message)
            VALUES (?, ?, ?)
            """,
            (user_id, title, message)
        )
        
        conn.commit()
        success = True
    except sqlite3.Error as e:
        st.error(f"Error adding notification: {e}")
        success = False
    
    conn.close()
    return success

def get_notifications(user_id, unread_only=False):
    """Get notifications for a user"""
    conn = get_connection()
    if not conn:
        # If we can't connect to the database, return demo data
        # Demo notifications will be shown when the database isn't properly set up
        return [
            {
                "id": 1,
                "title": "Welcome to the EMS System",
                "message": "Thank you for joining our Employee Management System. This is a demo notification.",
                "is_read": 0,
                "created_at": "2025-05-03 08:00:00"
            },
            {
                "id": 2,
                "title": "New Leave Policy",
                "message": "The company has updated its leave policy. Please check the HR portal for details.",
                "is_read": 0,
                "created_at": "2025-05-03 09:15:00"
            },
            {
                "id": 3,
                "title": "Team Meeting",
                "message": "Reminder: Weekly team meeting tomorrow at 10:00 AM in the conference room.",
                "is_read": 1,
                "created_at": "2025-05-02 14:30:00"
            }
        ] if not unread_only else [
            {
                "id": 1,
                "title": "Welcome to the EMS System",
                "message": "Thank you for joining our Employee Management System. This is a demo notification.",
                "is_read": 0,
                "created_at": "2025-05-03 08:00:00"
            },
            {
                "id": 2,
                "title": "New Leave Policy",
                "message": "The company has updated its leave policy. Please check the HR portal for details.",
                "is_read": 0,
                "created_at": "2025-05-03 09:15:00"
            }
        ]
    
    cursor = conn.cursor()
    
    query = """
    SELECT id, title, message, is_read, created_at
    FROM notifications
    WHERE user_id = ?
    """
    
    if unread_only:
        query += " AND is_read = 0"
    
    query += " ORDER BY created_at DESC"
    
    cursor.execute(query, (user_id,))
    
    notifications = []
    for row in cursor.fetchall():
        notifications.append({
            "id": row[0],
            "title": row[1],
            "message": row[2],
            "is_read": row[3],
            "created_at": row[4]
        })
    
    conn.close()
    return notifications

def mark_notification_read(notification_id):
    """Mark a notification as read"""
    conn = get_connection()
    if not conn:
        return False
    
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            """
            UPDATE notifications
            SET is_read = 1
            WHERE id = ?
            """,
            (notification_id,)
        )
        
        conn.commit()
        success = True
    except sqlite3.Error as e:
        st.error(f"Error marking notification as read: {e}")
        success = False
    
    conn.close()
    return success

# Dashboard data functions
def get_dashboard_stats():
    """Get dashboard statistics"""
    conn = get_connection()
    if not conn:
        return {}
    
    cursor = conn.cursor()
    
    stats = {}
    
    # Total employees
    cursor.execute("SELECT COUNT(*) FROM employees")
    stats['total_employees'] = cursor.fetchone()[0]
    
    # Departments count
    cursor.execute(
        """
        SELECT department, COUNT(*) as count
        FROM employees
        WHERE department IS NOT NULL AND department != ''
        GROUP BY department
        """
    )
    stats['departments'] = [{"name": row[0], "count": row[1]} for row in cursor.fetchall()]
    
    # Pending leave requests
    cursor.execute("SELECT COUNT(*) FROM leave_requests WHERE status = 'pending'")
    stats['pending_leaves'] = cursor.fetchone()[0]
    
    # Pending inquiries
    cursor.execute("SELECT COUNT(*) FROM inquiries WHERE status = 'pending'")
    stats['pending_inquiries'] = cursor.fetchone()[0]
    
    # Recent leaves
    cursor.execute(
        """
        SELECT lr.id, e.first_name || ' ' || e.last_name as employee_name,
        lr.leave_type, lr.start_date, lr.end_date, lr.status
        FROM leave_requests lr
        JOIN employees e ON lr.employee_id = e.id
        ORDER BY lr.created_at DESC
        LIMIT 5
        """
    )
    stats['recent_leaves'] = [
        {
            "id": row[0],
            "employee_name": row[1],
            "leave_type": row[2],
            "start_date": row[3],
            "end_date": row[4],
            "status": row[5]
        }
        for row in cursor.fetchall()
    ]
    
    conn.close()
    return stats

# Initialize database when module is imported
init_database()
