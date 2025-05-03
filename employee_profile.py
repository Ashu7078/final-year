import streamlit as st
import database
import utilities
from datetime import datetime
import base64
import io
import time
from PIL import Image

def show_profile():
    """Display and manage employee profile"""
    # Check if we have a specific action to perform
    if st.session_state.user_role == 'admin' and 'profile_action' in st.session_state:
        if st.session_state.profile_action == "add":
            st.title("Add New Employee")
            add_employee_form()
            return
        elif st.session_state.profile_action == "view":
            st.title("View All Employees")
            view_all_employees()
            return
        elif st.session_state.profile_action == "download":
            st.title("Download Employee Data")
            download_employee_data()
            return
    
    st.title("Employee Profile")
    
    # Get employee profile
    employee = database.get_employee_profile(st.session_state.user_id)
    
    if not employee:
        st.error("Employee profile not found")
        return
    
    # Create tabs for different profile views
    tab1, tab2, tab3 = st.tabs(["Profile Details", "Edit Profile", "Profile Picture"])
    
    with tab1:
        show_profile_details(employee)
    
    with tab2:
        edit_profile(employee)
        
    with tab3:
        upload_profile_picture(employee)

def show_profile_details(employee):
    """Display employee profile details"""
    st.subheader("Personal Information")
    
    # Main info card
    st.markdown(f"""
    <div style="background-color: rgba(30, 30, 30, 0.7); border-radius: 10px; padding: 20px; margin-bottom: 20px;">
        <h2 style="margin-top: 0;">{employee['first_name']} {employee['last_name']}</h2>
        <p>{employee['position'] or 'Position not specified'} • {employee['department'] or 'Department not specified'}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Personal and work information in columns
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style="background-color: rgba(30, 30, 30, 0.7); border-radius: 10px; padding: 20px; margin-bottom: 20px;">
            <h3 style="margin-top: 0;">Contact Information</h3>
        """, unsafe_allow_html=True)
        
        st.write(f"**Email:** {employee['email'] or 'Not provided'}")
        st.write(f"**Phone:** {employee['phone'] or 'Not provided'}")
        st.write(f"**Address:** {employee['address'] or 'Not provided'}")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background-color: rgba(30, 30, 30, 0.7); border-radius: 10px; padding: 20px; margin-bottom: 20px;">
            <h3 style="margin-top: 0;">Employment Details</h3>
        """, unsafe_allow_html=True)
        
        join_date = utilities.format_date(employee['join_date'])
        years_of_service = utilities.calculate_years_of_service(employee['join_date'])
        
        st.write(f"**Position:** {employee['position'] or 'Not specified'}")
        st.write(f"**Department:** {employee['department'] or 'Not specified'}")
        st.write(f"**Join Date:** {join_date}")
        st.write(f"**Years of Service:** {years_of_service}")
        st.write(f"**Manager:** {employee['manager_name'] or 'Not assigned'}")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Display additional information if admin
    if st.session_state.user_role == 'admin':
        st.subheader("Administrative Information")
        
        with st.expander("Employment Details"):
            st.write(f"**Employee ID:** {employee['id']}")
            st.write(f"**Status:** {employee['status']}")
            if employee['birth_date']:
                birth_date = utilities.format_date(employee['birth_date'])
                age = utilities.calculate_age(employee['birth_date'])
                st.write(f"**Birth Date:** {birth_date}")
                st.write(f"**Age:** {age or 'Unknown'}")

def edit_profile(employee):
    """Edit employee profile"""
    st.subheader("Update Your Profile")
    
    with st.form("profile_edit_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            first_name = st.text_input("First Name", value=employee['first_name'])
            last_name = st.text_input("Last Name", value=employee['last_name'])
            email = st.text_input("Email", value=employee['email'] or "")
        
        with col2:
            phone = st.text_input("Phone", value=employee['phone'] or "")
            department = st.text_input("Department", value=employee['department'] or "", disabled=st.session_state.user_role != 'admin')
            position = st.text_input("Position", value=employee['position'] or "", disabled=st.session_state.user_role != 'admin')
        
        address = st.text_area("Address", value=employee['address'] or "")
        
        submitted = st.form_submit_button("Update Profile")
        
        if submitted:
            # Validate inputs
            if not first_name or not last_name:
                st.error("First name and last name are required.")
            elif email and not utilities.validate_email(email):
                st.error("Please enter a valid email address.")
            elif phone and not utilities.validate_phone(phone):
                st.error("Please enter a valid phone number.")
            else:
                # Update profile
                update_data = {
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email,
                    'phone': phone,
                    'department': department,
                    'position': position,
                    'address': address
                }
                
                if database.update_employee_profile(employee['id'], update_data):
                    st.success("Profile updated successfully!")
                    st.rerun()
                else:
                    st.error("Failed to update profile. Please try again.")

def upload_profile_picture(employee):
    """Upload and manage profile picture"""
    st.subheader("Profile Picture")
    
    # Display current profile picture if exists
    if 'profile_picture' in employee and employee['profile_picture']:
        st.image(base64.b64decode(employee['profile_picture']), width=200)
    else:
        # Display default avatar
        st.info("No profile picture uploaded yet.")
        st.markdown("### 👤")
    
    # Upload new picture
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        try:
            # Open and resize image
            image = Image.open(uploaded_file)
            
            # Resize if too large
            max_size = (500, 500)
            image.thumbnail(max_size)
            
            # Convert to bytes
            buf = io.BytesIO()
            image.save(buf, format='PNG')
            byte_img = buf.getvalue()
            
            # Convert to base64 for storage
            encoded_img = base64.b64encode(byte_img).decode()
            
            # Show preview
            st.image(image, caption="Preview", width=200)
            
            if st.button("Save Profile Picture"):
                update_data = {'profile_picture': encoded_img}
                
                if database.update_employee_profile(employee['id'], update_data):
                    st.success("Profile picture updated successfully!")
                    st.rerun()
                else:
                    st.error("Failed to update profile picture. Please try again.")
                    
        except Exception as e:
            st.error(f"Error processing image: {e}")

def edit_profile_with_id(employee_id, employees=None):
    """Edit profile for a specific employee ID"""
    if not employees:
        employees = database.get_all_employees()
    
    employee = next((emp for emp in employees if emp['id'] == employee_id), None)
    
    if not employee:
        st.error(f"Employee with ID {employee_id} not found.")
        if st.button("Back to Employee List"):
            if 'edit_employee_id' in st.session_state:
                del st.session_state.edit_employee_id
            st.rerun()
        return
    
    st.subheader(f"Edit Employee: {employee['first_name']} {employee['last_name']}")
    
    with st.form(f"edit_employee_form_{employee_id}"):
        col1, col2 = st.columns(2)
        
        with col1:
            first_name = st.text_input("First Name*", value=employee['first_name'])
            last_name = st.text_input("Last Name*", value=employee['last_name'])
            email = st.text_input("Email*", value=employee['email'])
            phone = st.text_input("Phone Number", value=employee['phone'] if 'phone' in employee else "")
        
        with col2:
            department = st.selectbox(
                "Department*", 
                ["HR", "IT", "Finance", "Marketing", "Operations", "Sales", "R&D", "Other"],
                index=["HR", "IT", "Finance", "Marketing", "Operations", "Sales", "R&D", "Other"].index(employee['department']) if employee['department'] in ["HR", "IT", "Finance", "Marketing", "Operations", "Sales", "R&D", "Other"] else 7
            )
            position = st.text_input("Position*", value=employee['position'])
            
            # Convert join_date string to datetime object
            try:
                from datetime import datetime
                join_date_str = employee['join_date']
                join_date_obj = datetime.strptime(join_date_str, "%Y-%m-%d").date()
                join_date = st.date_input("Join Date*", value=join_date_obj)
            except Exception as e:
                join_date = st.date_input("Join Date*")
                st.error(f"Error parsing join date: {e}")
            
            status = st.selectbox(
                "Status*", 
                ["Active", "Inactive", "On Leave", "Probation"],
                index=["Active", "Inactive", "On Leave", "Probation"].index(employee['status']) if employee['status'] in ["Active", "Inactive", "On Leave", "Probation"] else 0
            )
        
        address = st.text_area("Address", value=employee['address'] if 'address' in employee else "")
        
        # Profile picture section
        st.write("Profile Picture")
        
        if 'profile_picture' in employee and employee['profile_picture']:
            try:
                st.image(base64.b64decode(employee['profile_picture']), width=150, caption="Current Profile Picture")
                keep_current = st.checkbox("Keep current profile picture", value=True)
            except Exception as e:
                st.error(f"Error displaying current profile picture: {e}")
                keep_current = st.checkbox("Keep current profile picture data", value=True)
        else:
            keep_current = False
        
        uploaded_file = st.file_uploader("Upload new profile picture...", type=["jpg", "jpeg", "png"])
        profile_picture = None
        
        if uploaded_file is not None:
            try:
                # Open and resize image
                image = Image.open(uploaded_file)
                
                # Resize if too large
                max_size = (500, 500)
                image.thumbnail(max_size)
                
                # Convert to bytes
                buf = io.BytesIO()
                image.save(buf, format='PNG')
                byte_img = buf.getvalue()
                
                # Convert to base64 for storage
                profile_picture = base64.b64encode(byte_img).decode()
                
                # Show preview
                st.image(image, caption="New Profile Picture Preview", width=150)
                    
            except Exception as e:
                st.error(f"Error processing image: {e}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            submitted = st.form_submit_button("Save Changes", type="primary", use_container_width=True)
        
        with col2:
            cancel = st.form_submit_button("Cancel", use_container_width=True)
        
        if cancel:
            if 'edit_employee_id' in st.session_state:
                del st.session_state.edit_employee_id
            st.rerun()
        
        if submitted:
            # Validate inputs
            if not first_name or not last_name or not email or not position or not department or not join_date:
                st.error("Fields marked with * are required.")
            elif not utilities.validate_email(email):
                st.error("Please enter a valid email address.")
            elif phone and not utilities.validate_phone(phone):
                st.error("Please enter a valid phone number.")
            else:
                # Prepare the profile picture data
                if keep_current and 'profile_picture' in employee and employee['profile_picture']:
                    final_profile_picture = employee['profile_picture']
                else:
                    final_profile_picture = profile_picture
                
                # Create employee data
                employee_data = {
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email,
                    'phone': phone,
                    'department': department,
                    'position': position,
                    'join_date': join_date.strftime("%Y-%m-%d"),
                    'status': status,
                    'address': address,
                    'profile_picture': final_profile_picture
                }
                
                # Call function to update employee
                success = database.update_employee_profile(employee_id, employee_data)
                
                if success:
                    st.success("Employee updated successfully!")
                    if 'edit_employee_id' in st.session_state:
                        del st.session_state.edit_employee_id
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Failed to update employee. Please try again.")

def add_employee_form():
    """Form for adding a new employee"""
    with st.form("add_employee_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            first_name = st.text_input("First Name*")
            last_name = st.text_input("Last Name*")
            email = st.text_input("Email*")
            phone = st.text_input("Phone Number")
        
        with col2:
            department = st.selectbox("Department*", ["HR", "IT", "Finance", "Marketing", "Operations", "Sales", "R&D", "Other"])
            position = st.text_input("Position*")
            join_date = st.date_input("Join Date*")
            status = st.selectbox("Status*", ["Active", "Inactive", "On Leave", "Probation"])
        
        address = st.text_area("Address")
        
        # File uploader for profile picture
        st.write("Profile Picture")
        uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
        profile_picture = None
        
        if uploaded_file is not None:
            try:
                # Open and resize image
                image = Image.open(uploaded_file)
                
                # Resize if too large
                max_size = (500, 500)
                image.thumbnail(max_size)
                
                # Convert to bytes
                buf = io.BytesIO()
                image.save(buf, format='PNG')
                byte_img = buf.getvalue()
                
                # Convert to base64 for storage
                profile_picture = base64.b64encode(byte_img).decode()
                
                # Show preview
                st.image(image, caption="Preview", width=150)
                    
            except Exception as e:
                st.error(f"Error processing image: {e}")
        
        submitted = st.form_submit_button("Add Employee")
        
        if submitted:
            # Validate inputs
            if not first_name or not last_name or not email or not position or not department or not join_date:
                st.error("Fields marked with * are required.")
            elif not utilities.validate_email(email):
                st.error("Please enter a valid email address.")
            elif phone and not utilities.validate_phone(phone):
                st.error("Please enter a valid phone number.")
            else:
                # Create employee data
                employee_data = {
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email,
                    'phone': phone,
                    'department': department,
                    'position': position,
                    'join_date': join_date.strftime("%Y-%m-%d"),
                    'status': status,
                    'address': address,
                    'profile_picture': profile_picture
                }
                
                # Call function to add employee (we need to implement this in database.py)
                if hasattr(database, 'add_employee') and callable(getattr(database, 'add_employee')):
                    result = database.add_employee(employee_data)
                    if result and result.get('success'):
                        st.success(f"Employee added successfully! Employee ID: {result.get('employee_id')}")
                        # Clear form by refreshing
                        st.rerun()
                    else:
                        st.error(f"Failed to add employee: {result.get('message', 'Unknown error')}")
                else:
                    st.error("Add employee functionality is not implemented yet.")

def view_all_employees():
    """Display all employees in card style view"""
    st.subheader("All Employees")
    
    # We've replaced the confirmation dialog with inline confirmation 
    # directly in the employee cards to fix the delete functionality
    
    # Get all employees
    employees = database.get_all_employees()
    
    if not employees:
        st.info("No employees found.")
        return
    
    # Search and filter
    search_term = st.text_input("Search by name, department, or position")
    
    if search_term:
        filtered_employees = []
        search_term = search_term.lower()
        for emp in employees:
            if (search_term in emp['first_name'].lower() or 
                search_term in emp['last_name'].lower() or 
                (emp['department'] and search_term in emp['department'].lower()) or 
                (emp['position'] and search_term in emp['position'].lower())):
                filtered_employees.append(emp)
        employees = filtered_employees
    
    if not employees:
        st.info(f"No employees found matching '{search_term}'.")
        return
    
    # Display employees in a grid of cards
    st.subheader(f"Showing {len(employees)} employees")
    
    # Create rows of 3 cards each
    rows = [employees[i:i+3] for i in range(0, len(employees), 3)]
    
    for row in rows:
        cols = st.columns(3)
        
        for i, employee in enumerate(row):
            with cols[i]:
                with st.container(border=True):
                    # Display profile picture if available
                    if 'profile_picture' in employee and employee['profile_picture']:
                        try:
                            image_data = base64.b64decode(employee['profile_picture'])
                            st.image(image_data, width=100)
                        except Exception as e:
                            st.error(f"Error displaying profile: {str(e)[:50]}...")
                            st.markdown("### 👤")
                    else:
                        st.markdown("### 👤")
                    
                    # Employee name and basic info
                    st.markdown(f"### {employee['first_name']} {employee['last_name']}")
                    st.markdown(f"**Position:** {employee['position'] or 'Not specified'}")
                    st.markdown(f"**Department:** {employee['department'] or 'Not specified'}")
                    
                    # Action buttons
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button("View", key=f"view_{employee['id']}", use_container_width=True):
                            st.session_state.view_employee_id = employee['id']
                            st.rerun()
                    with col2:
                        if st.button("Edit", key=f"edit_{employee['id']}", use_container_width=True):
                            st.session_state.edit_employee_id = employee['id']
                            st.rerun()
                    with col3:
                        if st.button("Delete", key=f"delete_{employee['id']}", use_container_width=True):
                            # Just directly delete for demo purposes
                            if database.delete_employee(employee['id']):
                                st.success(f"{employee['first_name']} {employee['last_name']} has been deleted.")
                                time.sleep(1.5)
                                st.rerun()
                            else:
                                st.error("Failed to delete employee. Please try again.")
    
    # If we're viewing details, show them in an expander
    if 'view_employee_id' in st.session_state:
        employee_id = st.session_state.view_employee_id
        employee = next((emp for emp in employees if emp['id'] == employee_id), None)
        
        if employee:
            with st.expander(f"Details for {employee['first_name']} {employee['last_name']}", expanded=True):
                col1, col2 = st.columns(2)
                
                with col1:
                    if 'profile_picture' in employee and employee['profile_picture']:
                        try:
                            st.image(base64.b64decode(employee['profile_picture']), width=200)
                        except Exception as e:
                            st.error(f"Error displaying profile image: {e}")
                            st.markdown("### 👤")
                    else:
                        st.markdown("### 👤")
                    
                    st.write(f"**Position:** {employee['position'] or 'Not specified'}")
                    st.write(f"**Department:** {employee['department'] or 'Not specified'}")
                    st.write(f"**Status:** {employee['status']}")
                
                with col2:
                    st.write(f"**Email:** {employee['email'] or 'Not provided'}")
                    st.write(f"**Phone:** {employee['phone'] or 'Not provided'}")
                    st.write(f"**Address:** {employee['address'] or 'Not provided'}")
                    
                    join_date = utilities.format_date(employee['join_date'])
                    years_of_service = utilities.calculate_years_of_service(employee['join_date'])
                    
                    st.write(f"**Join Date:** {join_date}")
                    st.write(f"**Years of Service:** {years_of_service}")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Edit Employee", key=f"edit_from_details_{employee_id}"):
                        st.session_state.edit_employee_id = employee_id
                        del st.session_state.view_employee_id
                        st.rerun()
                
                with col2:
                    if st.button("Close", key=f"close_details_{employee_id}"):
                        del st.session_state.view_employee_id
                        st.rerun()
                        
    # If we're editing an employee, show the edit form
    if 'edit_employee_id' in st.session_state:
        edit_profile_with_id(st.session_state.edit_employee_id, employees)

def download_employee_data():
    """Provide options to download employee data"""
    st.subheader("Download Employee Data")
    
    # Get all employees
    employees = database.get_all_employees()
    
    if not employees:
        st.info("No employee data available to download.")
        return
    
    # Create downloadable data
    import pandas as pd
    
    # Create basic DataFrame
    df = pd.DataFrame(employees)
    
    # Select columns to include (excluding sensitive data like profile pictures)
    columns_to_include = [
        'id', 'first_name', 'last_name', 'email', 'phone', 
        'department', 'position', 'join_date', 'status', 
        'address'
    ]
    
    # Filter columns that exist in df
    columns_to_include = [col for col in columns_to_include if col in df.columns]
    
    # Filtered dataframe
    df_filtered = df[columns_to_include]
    
    # Download as CSV only, Excel format removed
    st.markdown(utilities.get_table_download_link(df_filtered, "Download Employee Data (CSV)", "employee_data.csv"), unsafe_allow_html=True)