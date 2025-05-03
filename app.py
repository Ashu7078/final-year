import streamlit as st
import os
import sqlite3
import pandas as pd
from datetime import datetime
import time

# Import modules
import login
import dashboard
import employee_profile
import database
import utilities
import navigation
import leave_management
import inquiries_enhanced
import enhanced_leave_application
import leave_management
import inquiries_enhanced
import styles
import navigation
import utilities

# Set page config
st.set_page_config(
    page_title="Employee Management System",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom styles
styles.apply_styles()

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if 'user_id' not in st.session_state:
    st.session_state.user_id = None

if 'user_role' not in st.session_state:
    st.session_state.user_role = None

if 'current_page' not in st.session_state:
    st.session_state.current_page = "home"

if 'selected_inquiry' not in st.session_state:
    st.session_state.selected_inquiry = None

if 'view_leave_details' not in st.session_state:
    st.session_state.view_leave_details = None

if 'show_export' not in st.session_state:
    st.session_state.show_export = False

if 'export_df' not in st.session_state:
    st.session_state.export_df = None

# Main application
def main():
    # Show login screen if not logged in
    if not st.session_state.logged_in:
        login.show_login()
    else:
        # Show navigation and content
        navigation.show_navigation()
        
        # Display appropriate page content based on current page
        if st.session_state.current_page == "home":
            dashboard.show_dashboard()
        
        elif st.session_state.current_page == "profile":
            employee_profile.show_profile()
        
        elif st.session_state.current_page == "leave":
            if st.session_state.user_role == 'admin':
                leave_management.show_admin_leave_management()
            else:
                enhanced_leave_application.show_leave_application()
        
        elif st.session_state.current_page == "inquiries":
            if st.session_state.user_role == 'admin':
                inquiries_enhanced.show_inquiries()
            else:
                inquiries_enhanced.show_employee_inquiries()
        
        elif st.session_state.current_page == "payroll":
            if st.session_state.user_role == 'admin':
                st.title("Payroll Management")
                
                # Create tabs for different payroll sections
                tab1, tab2, tab3 = st.tabs(["Process Payroll", "Salary History", "Settings"])
                
                with tab1:
                    st.subheader("Process Monthly Payroll")
                    st.info("This feature is currently under development. It will allow HR to process payroll for all employees.")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.selectbox("Select Month", ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"])
                    with col2:
                        st.selectbox("Select Year", [2024, 2025])
                    
                    if st.button("Calculate Payroll", type="primary"):
                        st.success("Payroll calculation is not implemented yet. This feature will be available soon.")
                
                with tab2:
                    st.subheader("Salary History")
                    st.info("View and manage employee salary records")
                    st.dataframe(pd.DataFrame({
                        "Employee": ["John Doe", "Jane Smith", "Robert Johnson"],
                        "Position": ["Software Engineer", "HR Manager", "Sales Executive"],
                        "Month": ["April 2025", "April 2025", "April 2025"],
                        "Basic Salary": ["$5,000", "$6,000", "$4,500"],
                        "Bonus": ["$500", "$1,000", "$700"],
                        "Deductions": ["$700", "$800", "$600"],
                        "Net Salary": ["$4,800", "$6,200", "$4,600"]
                    }))
                
                with tab3:
                    st.subheader("Payroll Settings")
                    st.info("Configure payroll settings, tax rates, and deduction rules")
                    
                    st.checkbox("Enable automatic tax calculation")
                    st.checkbox("Enable performance-based bonuses")
                    st.slider("Default tax rate (%)", 0, 40, 15)
            else:
                st.title("Access Denied")
                st.error("You do not have permission to access this page.")
        
        elif st.session_state.current_page == "reports":
            if st.session_state.user_role == 'admin':
                st.title("Reports")
                
                report_type = st.selectbox("Select Report Type", [
                    "Employee Statistics", 
                    "Leave Statistics", 
                    "Payroll Reports", 
                    "Department Performance"
                ])
                
                if report_type == "Employee Statistics":
                    st.subheader("Employee Demographics")
                    st.bar_chart(pd.DataFrame({
                        "Department": ["Engineering", "HR", "Marketing", "Sales", "Operations"],
                        "Employees": [15, 5, 10, 20, 8]
                    }).set_index("Department"))
                    
                    st.subheader("Average Years of Service")
                    st.line_chart(pd.DataFrame({
                        "Department": ["Engineering", "HR", "Marketing", "Sales", "Operations"],
                        "Years": [3.5, 5.2, 2.1, 4.7, 6.3]
                    }).set_index("Department"))
                    
                elif report_type == "Leave Statistics":
                    st.subheader("Leave Utilization by Type")
                    st.bar_chart(pd.DataFrame({
                        "Leave Type": ["Annual", "Sick", "Personal", "Unpaid"],
                        "Days Used": [120, 45, 30, 10]
                    }).set_index("Leave Type"))
                    
                    st.subheader("Monthly Leave Trends")
                    st.line_chart(pd.DataFrame({
                        "Month": ["Jan", "Feb", "Mar", "Apr", "May"],
                        "Leave Requests": [10, 15, 8, 12, 9]
                    }).set_index("Month"))
                
                else:
                    st.info(f"The {report_type} report is under development.")
            else:
                st.title("Access Denied")
                st.error("You do not have permission to access this page.")
                
        elif st.session_state.current_page == "department":
            if st.session_state.user_role == 'admin':
                st.title("Department Management")
                
                tab1, tab2 = st.tabs(["All Departments", "Add Department"])
                
                with tab1:
                    st.subheader("Department List")
                    
                    # We're now handling delete directly on the button click from the department cards
                    # The confirmation dialog approach was causing issues
                    
                    # Create a dummy department list for display
                    departments = [
                        {"id": 1, "name": "Engineering", "employees": 15, "manager": "John Smith", "budget": "$500,000", "description": "Software development and technical operations", "location": "Floor 3, East Wing", "email": "engineering@company.com", "projects": ["Mobile App", "Web Platform", "Backend Services"]},
                        {"id": 2, "name": "Human Resources", "employees": 5, "manager": "Maria Garcia", "budget": "$200,000", "description": "Employee management and recruitment", "location": "Floor 2, West Wing", "email": "hr@company.com", "projects": ["Talent Acquisition", "Employee Engagement", "Training"]},
                        {"id": 3, "name": "Finance", "employees": 8, "manager": "Robert Chen", "budget": "$350,000", "description": "Financial management and accounting", "location": "Floor 2, North Wing", "email": "finance@company.com", "projects": ["Budget Planning", "Financial Analysis", "Accounting"]},
                        {"id": 4, "name": "Marketing", "employees": 10, "manager": "Sarah Johnson", "budget": "$400,000", "description": "Marketing campaigns and brand management", "location": "Floor 1, South Wing", "email": "marketing@company.com", "projects": ["Brand Campaign", "Digital Marketing", "Market Research"]},
                        {"id": 5, "name": "Sales", "employees": 20, "manager": "David Wilson", "budget": "$750,000", "description": "Sales and client relationship management", "location": "Floor 1, East Wing", "email": "sales@company.com", "projects": ["Enterprise Clients", "SMB Market", "International Sales"]}
                    ]
                    
                    # Check if viewing department details
                    if 'view_department_id' in st.session_state:
                        dept_id = st.session_state.view_department_id
                        department = next((d for d in departments if d['id'] == dept_id), None)
                        
                        if department:
                            with st.expander(f"Details for {department['name']} Department", expanded=True):
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    st.markdown(f"### {department['name']} Department")
                                    st.write(f"**Manager:** {department['manager']}")
                                    st.write(f"**Employees:** {department['employees']}")
                                    st.write(f"**Budget:** {department['budget']}")
                                    st.write(f"**Email:** {department['email']}")
                                    st.write(f"**Location:** {department['location']}")
                                
                                with col2:
                                    st.subheader("Description")
                                    st.write(department['description'])
                                    
                                    st.subheader("Current Projects")
                                    for project in department['projects']:
                                        st.write(f"- {project}")
                                
                                st.subheader("Department Performance")
                                
                                # Show department metrics
                                metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
                                with metrics_col1:
                                    st.metric("Annual Budget", department['budget'], "+5.2%")
                                with metrics_col2:
                                    st.metric("Projects Completed", "12", "+2")
                                with metrics_col3:
                                    st.metric("Team Growth", f"{department['employees']} members", "+3")
                                
                                # Sample chart
                                import random
                                chart_data = pd.DataFrame({
                                    'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                                    'Performance': [random.randint(70, 100) for _ in range(6)]
                                })
                                st.line_chart(chart_data.set_index('Month'))
                                
                                col1, col2 = st.columns(2)
                                with col1:
                                    if st.button("Edit Department", key=f"edit_from_details_{dept_id}"):
                                        st.session_state.edit_department_id = dept_id
                                        del st.session_state.view_department_id
                                        st.rerun()
                                
                                with col2:
                                    if st.button("Close", key=f"close_details_{dept_id}"):
                                        del st.session_state.view_department_id
                                        st.rerun()
                    
                    # Check if editing department
                    elif 'edit_department_id' in st.session_state:
                        dept_id = st.session_state.edit_department_id
                        department = next((d for d in departments if d['id'] == dept_id), None)
                        
                        if department:
                            st.subheader(f"Edit {department['name']} Department")
                            
                            with st.form(f"edit_department_form_{dept_id}"):
                                name = st.text_input("Department Name*", value=department['name'])
                                description = st.text_area("Description", value=department['description'])
                                manager = st.text_input("Department Manager", value=department['manager'])
                                
                                col1, col2 = st.columns(2)
                                with col1:
                                    # Remove $ and , from budget for conversion to number
                                    budget_str = department['budget'].replace('$', '').replace(',', '')
                                    try:
                                        budget_value = int(budget_str)
                                    except:
                                        budget_value = 100000
                                    
                                    budget = st.number_input("Annual Budget", min_value=0, value=budget_value, step=10000)
                                    employees = st.number_input("Number of Employees", min_value=0, value=department['employees'], step=1)
                                with col2:
                                    location = st.text_input("Location", value=department['location'])
                                    email = st.text_input("Department Email", value=department['email'])
                                
                                projects = st.text_area("Projects (one per line)", value="\n".join(department['projects']))
                                
                                col1, col2 = st.columns(2)
                                with col1:
                                    submitted = st.form_submit_button("Update Department", use_container_width=True)
                                with col2:
                                    cancel = st.form_submit_button("Cancel", use_container_width=True)
                                
                                if cancel:
                                    if 'edit_department_id' in st.session_state:
                                        del st.session_state.edit_department_id
                                    st.rerun()
                                
                                if submitted:
                                    if not name:
                                        st.error("Department name is required")
                                    else:
                                        st.success(f"Department '{name}' would be updated (feature under development)")
                                        time.sleep(1)
                                        if 'edit_department_id' in st.session_state:
                                            del st.session_state.edit_department_id
                                        st.rerun()
                    
                    # Display departments in a nice grid layout
                    else:
                        cols = st.columns(3)
                        for i, dept in enumerate(departments):
                            with cols[i % 3]:
                                with st.container(border=True):
                                    st.markdown(f"### {dept['name']}")
                                    st.write(f"**Manager:** {dept['manager']}")
                                    st.write(f"**Employees:** {dept['employees']}")
                                    st.write(f"**Budget:** {dept['budget']}")
                                    
                                    col1, col2, col3 = st.columns(3)
                                    with col1:
                                        if st.button("Edit", key=f"edit_dept_{dept['id']}", use_container_width=True):
                                            st.session_state.edit_department_id = dept['id']
                                            st.rerun()
                                    with col2:
                                        if st.button("Details", key=f"detail_dept_{dept['id']}", use_container_width=True):
                                            st.session_state.view_department_id = dept['id']
                                            st.rerun()
                                    with col3:
                                        # Only enable delete for non-empty departments (for demo purposes, as they aren't real DB records)
                                        delete_btn = st.button("Delete", key=f"delete_dept_{dept['id']}", use_container_width=True)
                                        if delete_btn:
                                            # For demo - pretend to delete by showing success message
                                            st.success(f"Department {dept['name']} would be deleted (feature under development)")
                                            time.sleep(1.5)
                                            st.rerun()
                
                with tab2:
                    st.subheader("Add New Department")
                    
                    with st.form("add_department_form"):
                        dept_name = st.text_input("Department Name*")
                        dept_desc = st.text_area("Description")
                        manager = st.selectbox("Department Manager", ["Select Manager", "John Doe", "Jane Smith", "Robert Johnson"])
                        budget = st.number_input("Annual Budget", min_value=0, value=100000, step=10000)
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            location = st.text_input("Location")
                        with col2:
                            email = st.text_input("Department Email")
                        
                        submit = st.form_submit_button("Add Department")
                        
                        if submit:
                            if not dept_name:
                                st.error("Department name is required")
                            elif manager == "Select Manager":
                                st.warning("Please select a department manager")
                            else:
                                st.success(f"Department '{dept_name}' would be added (feature under development)")
            else:
                st.title("Access Denied")
                st.error("You do not have permission to access this page.")
                
        elif st.session_state.current_page == "notification":
            if st.session_state.user_role == 'admin':
                st.title("Send Notifications")
                
                tab1, tab2 = st.tabs(["Send New Notification", "Notification History"])
                
                with tab1:
                    st.subheader("Send Notification to Employees")
                    
                    with st.form("send_notification_form"):
                        notification_type = st.selectbox("Notification Type", [
                            "Individual Employee", 
                            "Department", 
                            "All Employees"
                        ])
                        
                        # Initialize recipient variable for all cases
                        recipient = None
                        
                        if notification_type == "Individual Employee":
                            recipient = st.selectbox("Select Employee", ["John Doe", "Jane Smith", "Robert Johnson", "Amanda Lee"])
                        elif notification_type == "Department":
                            recipient = st.selectbox("Select Department", ["Engineering", "HR", "Finance", "Marketing", "Sales"])
                        
                        title = st.text_input("Notification Title*")
                        message = st.text_area("Message*", height=150)
                        
                        importance = st.radio("Importance", ["Normal", "High", "Urgent"])
                        
                        submit = st.form_submit_button("Send Notification")
                        
                        if submit:
                            if not title or not message:
                                st.error("Title and message are required")
                            else:
                                if notification_type == 'All Employees':
                                    recipient_display = "all employees"
                                else:
                                    recipient_display = recipient if recipient else "selected recipient"
                                
                                st.success(f"Notification would be sent to {recipient_display} (feature under development)")
                
                with tab2:
                    st.subheader("Previously Sent Notifications")
                    
                    # Example notification history
                    notifications = [
                        {"id": 1, "title": "System Maintenance", "recipients": "All Employees", "date": "2025-04-20", "read": "45/58"},
                        {"id": 2, "title": "Quarterly Review", "recipients": "Department: Engineering", "date": "2025-04-15", "read": "12/15"},
                        {"id": 3, "title": "New Project Assignment", "recipients": "John Doe", "date": "2025-04-10", "read": "1/1"}
                    ]
                    
                    for notif in notifications:
                        with st.container(border=True):
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.markdown(f"**{notif['title']}**")
                                st.write(f"Sent to: {notif['recipients']}")
                                st.caption(f"Date: {notif['date']} • Read: {notif['read']}")
                            with col2:
                                st.button("View Details", key=f"view_notif_{notif['id']}")
            else:
                st.title("My Notifications")
                
                # Get user notifications
                notifications = database.get_notifications(st.session_state.user_id)
                
                if notifications:
                    tab1, tab2 = st.tabs(["All Notifications", "Unread"])
                    
                    with tab1:
                        for notification in notifications:
                            with st.container(border=True):
                                st.markdown(f"**{notification['title']}**")
                                st.write(notification['message'])
                                st.caption(f"Received: {notification['created_at']}")
                                
                                if notification['is_read'] == 0:
                                    if st.button("Mark as Read", key=f"mark_read_{notification['id']}"):
                                        database.mark_notification_read(notification['id'])
                                        st.rerun()
                    
                    with tab2:
                        unread = [n for n in notifications if n['is_read'] == 0]
                        if unread:
                            for notification in unread:
                                with st.container(border=True):
                                    st.markdown(f"**{notification['title']}**")
                                    st.write(notification['message'])
                                    st.caption(f"Received: {notification['created_at']}")
                                    
                                    if st.button("Mark as Read", key=f"mark_unread_{notification['id']}"):
                                        database.mark_notification_read(notification['id'])
                                        st.rerun()
                        else:
                            st.info("You have no unread notifications")
                else:
                    st.info("You have no notifications")
                
        elif st.session_state.current_page == "import_export":
            if st.session_state.user_role == 'admin':
                st.title("Import/Export Data")
                
                tab1, tab2 = st.tabs(["Export Data", "Import Data"])
                
                with tab1:
                    st.subheader("Export System Data")
                    
                    export_type = st.selectbox("Select data to export", [
                        "Employees", 
                        "Leave Requests", 
                        "Payroll Records", 
                        "Departments"
                    ])
                    
                    export_format = st.radio("Export format", ["CSV", "Excel", "JSON"])
                    
                    if st.button("Generate Export", type="primary"):
                        with st.spinner("Preparing export file..."):
                            st.success(f"{export_type} data would be exported as {export_format}. (Feature under development)")
                            
                            # Get real employee data
                            if export_type == "Employees":
                                employees = database.get_all_employees()
                                if employees:
                                    # Convert to DataFrame
                                    df = pd.DataFrame(employees)
                                    # Filter out sensitive data
                                    if 'profile_picture' in df.columns:
                                        df = df.drop(columns=['profile_picture'])
                                    
                                    st.dataframe(df)
                                    st.markdown(utilities.get_table_download_link(df, f"Download {export_type}", f"{export_type.lower()}.csv"), unsafe_allow_html=True)
                                else:
                                    st.warning("No employee data available")
                
                with tab2:
                    st.subheader("Import Data")
                    
                    import_type = st.selectbox("Select data to import", [
                        "Employees", 
                        "Leave Balances", 
                        "Departments"
                    ])
                    
                    uploaded_file = st.file_uploader("Upload file", type=["csv", "xlsx", "json"])
                    
                    if uploaded_file is not None:
                        st.info("File uploaded successfully. Preview:")
                        
                        try:
                            # Try to read as CSV
                            df = pd.read_csv(uploaded_file)
                            st.dataframe(df.head())
                            
                            if st.button("Process Import"):
                                st.success("Data import functionality is under development.")
                        except:
                            st.error("Could not read the uploaded file. Please make sure it's a valid CSV file.")
            else:
                st.title("Access Denied")
                st.error("You do not have permission to access this page.")
        
        # Show fixed footer that doesn't move with scrolling
        st.markdown("""
        <style>
        .footer {
            position: fixed;
            bottom: 0;
            left: 0;
            width: 100%;
            background-color: rgba(30, 30, 30, 0.7);
            padding: 10px 0;
            text-align: center;
            font-size: 0.8rem;
            z-index: 999;
        }
        </style>
        <div class="footer">
            Employee Management System © 2024 | Made by Ashish
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
