import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import database as db
import enhanced_leave_application
import utilities as utils

def show_admin_leave_management():
    """Display leave management interface for administrators"""
    st.subheader("Leave Management")
    
    # Create tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs(["Pending Requests", "All Requests", "Leave Statistics", "Apply for Leave"])
    
    with tab1:
        show_pending_leave_requests()
    
    with tab2:
        show_all_leave_requests()
    
    with tab3:
        show_leave_statistics()
        
    with tab4:
        # Show leave application form for admin
        show_employee_leave_application()

def show_pending_leave_requests():
    """Display pending leave requests for admin approval"""
    # Get all pending leave requests
    pending_requests = db.get_leave_requests(status="pending")
    
    if not pending_requests:
        st.info("No pending leave requests found.")
        return
    
    st.write(f"### Pending Leave Requests ({len(pending_requests)})")
    
    # Display each pending request in a card
    for request in pending_requests:
        with st.container(border=True):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**Employee:** {request['employee_name']}")
                st.write(f"**Type:** {request['leave_type']}")
                st.write(f"**Period:** {request['start_date']} to {request['end_date']} ({int(request['days_count'])} days)")
                st.write(f"**Reason:** {request['reason']}")
                st.write(f"**Requested:** {request['created_at']}")
            
            with col2:
                # Get the employee ID of the current admin user
                user_id = st.session_state.user_id
                admin_employee = db.get_employee_profile(user_id)
                admin_id = admin_employee['id'] if admin_employee else None
                
                response = st.text_area("Response (optional)", key=f"response_{request['id']}")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("Approve", key=f"approve_{request['id']}", type="primary"):
                        if db.approve_leave_request(request['id'], admin_id, response):
                            st.success("Leave request approved successfully!")
                            st.rerun()
                        else:
                            st.error("Failed to approve leave request.")
                
                with col_b:
                    if st.button("Reject", key=f"reject_{request['id']}"):
                        if db.reject_leave_request(request['id'], admin_id, response or "Rejected by administrator"):
                            st.success("Leave request rejected successfully!")
                            st.rerun()
                        else:
                            st.error("Failed to reject leave request.")

def show_all_leave_requests():
    """Display all leave requests with filtering options"""
    # Get all leave requests
    all_requests = db.get_leave_requests()
    
    if not all_requests:
        st.info("No leave requests found.")
        return
    
    # Create a DataFrame for easier filtering and display
    df = pd.DataFrame(all_requests)
    
    # Add filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status_filter = st.multiselect(
            "Status",
            options=["pending", "approved", "rejected", "cancelled"],
            default=[]
        )
    
    with col2:
        if len(df) > 0 and 'leave_type' in df.columns:
            leave_types = df['leave_type'].unique().tolist()
            type_filter = st.multiselect("Leave Type", options=leave_types, default=[])
        else:
            type_filter = []
    
    with col3:
        date_range = st.date_input(
            "Date Range",
            value=(datetime.now() - timedelta(days=30), datetime.now()),
            format="YYYY-MM-DD"
        )
    
    # Apply filters
    filtered_df = df.copy()
    
    if status_filter:
        filtered_df = filtered_df[filtered_df['status'].isin(status_filter)]
    
    if type_filter:
        filtered_df = filtered_df[filtered_df['leave_type'].isin(type_filter)]
    
    if len(date_range) == 2:
        start_date, end_date = date_range
        
        # Handle potential different date formats with try-except
        try:
            # Convert dates with error handling
            start_dates = pd.to_datetime(filtered_df['start_date'], errors='coerce')
            end_dates = pd.to_datetime(filtered_df['end_date'], errors='coerce')
            filter_end = pd.to_datetime(str(end_date))
            filter_start = pd.to_datetime(str(start_date))
            
            # Apply the date filter
            filtered_df = filtered_df[
                (start_dates <= filter_end) &
                (end_dates >= filter_start)
            ]
        except Exception as e:
            st.error(f"Error filtering by date: {e}")
    
    # Display results
    if len(filtered_df) > 0:
        st.write(f"### Showing {len(filtered_df)} Leave Requests")
        
        # Add export option
        st.markdown(utils.get_table_download_link(filtered_df, "Export Data", "leave_requests.csv"), unsafe_allow_html=True)
        
        # Display as a table
        st.dataframe(
            filtered_df[[
                'id', 'employee_name', 'leave_type', 'start_date', 
                'end_date', 'days_count', 'status', 'created_at'
            ]].rename(columns={
                'id': 'ID',
                'employee_name': 'Employee',
                'leave_type': 'Type',
                'start_date': 'Start Date',
                'end_date': 'End Date',
                'days_count': 'Days',
                'status': 'Status',
                'created_at': 'Requested On'
            }),
            use_container_width=True
        )
        
        # Show details for selected request
        selected_id = st.selectbox(
            "Select a request to view details",
            options=filtered_df['id'].tolist(),
            format_func=lambda x: f"#{x} - {filtered_df[filtered_df['id']==x]['employee_name'].iloc[0]} ({filtered_df[filtered_df['id']==x]['leave_type'].iloc[0]})"
        )
        
        if selected_id:
            show_leave_request_details(selected_id)
    else:
        st.info("No leave requests match the selected filters.")

def show_leave_request_details(request_id):
    """Display detailed information for a specific leave request"""
    # Get the request details
    request = next((r for r in db.get_leave_requests() if r['id'] == request_id), None)
    
    if not request:
        st.error("Leave request not found.")
        return
    
    # Format the display
    st.markdown("---")
    st.subheader(f"Leave Request Details - ID #{request_id}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"**Employee:** {request['employee_name']}")
        st.markdown(f"**Department:** {request['department']}")
        st.markdown(f"**Leave Type:** {request['leave_type']}")
        st.markdown(f"**Status:** {request['status'].capitalize()}")
    
    with col2:
        st.markdown(f"**Start Date:** {request['start_date']}")
        st.markdown(f"**End Date:** {request['end_date']}")
        st.markdown(f"**Days:** {request['days_count']}")
        st.markdown(f"**Requested On:** {request['created_at']}")
    
    st.markdown("**Reason:**")
    st.markdown(f"<div style='background-color: rgba(50, 50, 50, 0.4); padding: 10px; border-radius: 5px;'>{request['reason']}</div>", unsafe_allow_html=True)
    
    # Show response information if it exists
    if request['response_date']:
        st.markdown("**Response:**")
        st.markdown(f"<div style='background-color: rgba(50, 50, 50, 0.4); padding: 10px; border-radius: 5px;'>{request['response_message'] or 'No message provided'}</div>", unsafe_allow_html=True)
        st.markdown(f"**Responded On:** {request['response_date']}")
    
    # Show action buttons based on status
    if request['status'] == 'pending':
        # Get the employee ID of the current admin user
        user_id = st.session_state.user_id
        admin_employee = db.get_employee_profile(user_id)
        admin_id = admin_employee['id'] if admin_employee else None
        
        col1, col2 = st.columns(2)
        
        with col1:
            response = st.text_area("Response (optional)", key=f"response_detail_{request_id}")
            
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("Approve Request", key=f"approve_detail_{request_id}", type="primary"):
                if db.approve_leave_request(request_id, admin_id, response):
                    st.success("Leave request approved successfully!")
                    st.rerun()
                else:
                    st.error("Failed to approve leave request.")
        
        with col_b:
            if st.button("Reject Request", key=f"reject_detail_{request_id}"):
                if db.reject_leave_request(request_id, admin_id, response or "Rejected by administrator"):
                    st.success("Leave request rejected successfully!")
                    st.rerun()
                else:
                    st.error("Failed to reject leave request.")

def get_employee_name_by_id(employee_id):
    """Get employee name by ID"""
    # This is a simplified version that works with the existing database functions
    conn = db.get_connection()
    if not conn:
        return "Unknown Employee"
    
    cursor = conn.cursor()
    cursor.execute(
        "SELECT first_name, last_name FROM employees WHERE id = ?",
        (employee_id,)
    )
    
    employee = cursor.fetchone()
    conn.close()
    
    if employee:
        return f"{employee[0]} {employee[1]}"
    return "Unknown Employee"

def show_leave_statistics():
    """Show leave statistics and visualizations"""
    st.subheader("Leave Statistics")
    
    # Get leave statistics
    leave_stats = db.get_leave_statistics()
    
    if not leave_stats:
        st.info("No leave data available for statistics.")
        return
    
    # Display summary stats
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Leave Requests", leave_stats.get('total_requests', 0))
    
    with col2:
        st.metric("Approved Requests", leave_stats.get('approved_requests', 0))
    
    with col3:
        st.metric("Pending Requests", leave_stats.get('pending_requests', 0))
    
    # Create statistics by leave type
    if 'leave_type_stats' in leave_stats and leave_stats['leave_type_stats']:
        st.subheader("Leave Distribution by Type")
        
        leave_type_df = pd.DataFrame(leave_stats['leave_type_stats'])
        
        fig = px.pie(
            leave_type_df,
            values='count',
            names='leave_type',
            title="",
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig.update_layout(
            margin=dict(l=20, r=20, t=30, b=20),
            height=350
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Create statistics by department
    if 'department_stats' in leave_stats and leave_stats['department_stats']:
        st.subheader("Leave Requests by Department")
        
        dept_df = pd.DataFrame(leave_stats['department_stats'])
        
        fig = px.bar(
            dept_df,
            x='department',
            y='count',
            title="",
            color='department',
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig.update_layout(
            xaxis_title="Department",
            yaxis_title="Number of Requests",
            margin=dict(l=20, r=20, t=30, b=20),
            height=350
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Monthly trend
    if 'monthly_stats' in leave_stats and leave_stats['monthly_stats']:
        st.subheader("Monthly Leave Trends")
        
        monthly_df = pd.DataFrame(leave_stats['monthly_stats'])
        
        fig = px.line(
            monthly_df,
            x='month',
            y='count',
            title="",
            markers=True
        )
        fig.update_layout(
            xaxis_title="Month",
            yaxis_title="Number of Requests",
            margin=dict(l=20, r=20, t=30, b=20),
            height=350
        )
        st.plotly_chart(fig, use_container_width=True)
        
def show_employee_leave_application():
    """Display form for employees to apply for leave"""
    st.subheader("Apply for Leave")
    
    # Get employee profile from the current user
    employee = db.get_employee_profile(st.session_state.user_id)
    
    if not employee:
        st.error("Employee profile not found")
        return
    
    # Create tabs for different sections
    tab1, tab2, tab3 = st.tabs(["Submit Application", "My Requests", "Leave Balance"])
    
    with tab1:
        show_leave_application_form()
    
    with tab2:
        show_employee_leave_requests()
    
    with tab3:
        show_employee_leave_balance()
        
def show_leave_application_form():
    """Show form for applying for leave"""
    # Get current employee details
    employee = db.get_employee_profile(st.session_state.user_id)
    
    if not employee:
        st.error("Employee profile not found.")
        return
    
    st.write("### New Leave Request")
    
    with st.form("leave_application_form"):
        leave_type = st.selectbox(
            "Leave Type",
            options=[
                "Annual Leave",
                "Sick Leave",
                "Personal Leave",
                "Maternity/Paternity Leave",
                "Unpaid Leave"
            ]
        )
        
        # Get the current year's leave balance for validation
        balance = db.get_employee_leave_balance(employee['id'])
        
        if balance:
            # Show available balance based on selected leave type
            if leave_type == "Annual Leave":
                available = balance['annual_leave_total'] - balance['annual_leave_used']
                st.info(f"Available balance: {available} days (used {balance['annual_leave_used']} of {balance['annual_leave_total']})")
            elif leave_type == "Sick Leave":
                available = balance['sick_leave_total'] - balance['sick_leave_used']
                st.info(f"Available balance: {available} days (used {balance['sick_leave_used']} of {balance['sick_leave_total']})")
            elif leave_type == "Personal Leave":
                available = balance['personal_leave_total'] - balance['personal_leave_used']
                st.info(f"Available balance: {available} days (used {balance['personal_leave_used']} of {balance['personal_leave_total']})")
            elif leave_type == "Maternity/Paternity Leave":
                available = balance['maternity_leave_total'] - balance['maternity_leave_used']
                st.info(f"Available balance: {available} days (used {balance['maternity_leave_used']} of {balance['maternity_leave_total']})")
        
        col1, col2 = st.columns(2)
        
        with col1:
            start_date = st.date_input(
                "Start Date",
                value=datetime.now().date(),
                min_value=datetime.now().date(),
                format="YYYY-MM-DD"
            )
        
        with col2:
            end_date = st.date_input(
                "End Date",
                value=datetime.now().date() + timedelta(days=1),
                min_value=start_date,
                format="YYYY-MM-DD"
            )
        
        # Calculate number of days
        days_count = (end_date - start_date).days + 1
        st.write(f"Total days: {days_count}")
        
        reason = st.text_area("Reason for Leave", height=100)
        
        submit_button = st.form_submit_button("Submit Request", type="primary")
        
        if submit_button:
            if not reason:
                st.error("Please provide a reason for your leave request.")
            elif days_count <= 0:
                st.error("End date must be after start date.")
            else:
                # Check if there's enough leave balance (except for unpaid leave)
                if leave_type != "Unpaid Leave" and balance:
                    if (leave_type == "Annual Leave" and days_count > (balance['annual_leave_total'] - balance['annual_leave_used'])) or \
                       (leave_type == "Sick Leave" and days_count > (balance['sick_leave_total'] - balance['sick_leave_used'])) or \
                       (leave_type == "Personal Leave" and days_count > (balance['personal_leave_total'] - balance['personal_leave_used'])) or \
                       (leave_type == "Maternity/Paternity Leave" and days_count > (balance['maternity_leave_total'] - balance['maternity_leave_used'])):
                        st.error("You don't have enough leave balance for this request.")
                        return
                
                # Submit the leave request
                result = db.submit_leave_request(
                    employee['id'],
                    leave_type,
                    start_date.strftime("%Y-%m-%d"),
                    end_date.strftime("%Y-%m-%d"),
                    reason
                )
                
                if result:
                    st.success("Leave request submitted successfully!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Failed to submit leave request. Please try again.")

def show_employee_leave_requests():
    """Show leave requests for the current employee"""
    # Get employee profile
    employee = db.get_employee_profile(st.session_state.user_id)
    
    if not employee:
        st.error("Employee profile not found.")
        return
    
    # Get all leave requests for this employee
    leave_requests = db.get_leave_requests(employee_id=employee['id'])
    
    if not leave_requests:
        st.info("You have no leave requests.")
        return
    
    # Filter tabs
    filter_tab1, filter_tab2, filter_tab3, filter_tab4 = st.tabs(["All Requests", "Pending", "Approved", "Rejected"])
    
    with filter_tab1:
        display_employee_leave_requests(leave_requests, key_suffix="all")
    
    with filter_tab2:
        pending_requests = [r for r in leave_requests if r['status'] == 'pending']
        if pending_requests:
            display_employee_leave_requests(pending_requests, key_suffix="pending")
        else:
            st.info("No pending leave requests.")
    
    with filter_tab3:
        approved_requests = [r for r in leave_requests if r['status'] == 'approved']
        if approved_requests:
            display_employee_leave_requests(approved_requests, key_suffix="approved")
        else:
            st.info("No approved leave requests.")
    
    with filter_tab4:
        rejected_requests = [r for r in leave_requests if r['status'] == 'rejected']
        if rejected_requests:
            display_employee_leave_requests(rejected_requests, key_suffix="rejected")
        else:
            st.info("No rejected leave requests.")

def display_employee_leave_requests(requests, key_suffix="all"):
    """Display leave requests for an employee"""
    # Convert to DataFrame
    df = pd.DataFrame(requests)
    
    # Display as a table
    st.dataframe(
        df[['id', 'leave_type', 'start_date', 'end_date', 'days_count', 'status', 'created_at']].rename(columns={
            'id': 'ID',
            'leave_type': 'Leave Type',
            'start_date': 'Start Date',
            'end_date': 'End Date',
            'days_count': 'Days',
            'status': 'Status',
            'created_at': 'Applied On'
        }),
        use_container_width=True
    )
    
    # Show detail view for selected leave request - add a unique key to avoid duplications
    selected_leave = st.selectbox(
        "Select Leave Request for Details", 
        options=df['id'].tolist(),
        format_func=lambda x: f"Request #{x} - {df[df['id']==x]['leave_type'].iloc[0]} ({df[df['id']==x]['start_date'].iloc[0]} to {df[df['id']==x]['end_date'].iloc[0]})",
        key=f"leave_select_{key_suffix}"
    )
    
    if selected_leave:
        show_employee_leave_details(selected_leave)

def show_employee_leave_details(request_id):
    """Display detailed information for a specific leave request for an employee"""
    # Get the request details
    request = next((r for r in db.get_leave_requests() if r['id'] == request_id), None)
    
    if not request:
        st.error("Leave request not found.")
        return
    
    # Format the display
    st.markdown("---")
    st.subheader(f"Leave Request Details - #{request_id}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"**Leave Type:** {request['leave_type']}")
        st.markdown(f"**Start Date:** {request['start_date']}")
        st.markdown(f"**End Date:** {request['end_date']}")
        
    with col2:
        st.markdown(f"**Total Days:** {request['days_count']}")
        st.markdown(f"**Status:** {request['status'].capitalize()}")
        st.markdown(f"**Applied On:** {request['created_at']}")
        
    st.markdown("**Reason:**")
    st.markdown(f"<div style='background-color: rgba(50, 50, 50, 0.4); padding: 10px; border-radius: 5px;'>{request['reason']}</div>", unsafe_allow_html=True)
    
    # Show response information if it exists
    if 'response_message' in request and request['response_message']:
        st.markdown("**Response:**")
        st.markdown(f"<div style='background-color: rgba(50, 50, 50, 0.4); padding: 10px; border-radius: 5px;'>{request['response_message']}</div>", unsafe_allow_html=True)
        
    if 'response_date' in request and request['response_date']:
        st.markdown(f"**Responded On:** {request['response_date']}")
    
    # Show cancel button for pending requests
    if request['status'] == 'pending':
        if st.button("Cancel Request", key=f"cancel_{request_id}", type="primary"):
            # Cancel the leave request
            conn = db.get_connection()
            cursor = conn.cursor()
            
            try:
                cursor.execute("UPDATE leave_requests SET status = 'cancelled', response_date = datetime('now') WHERE id = ?", (request_id,))
                conn.commit()
                st.success("Leave request cancelled")
                time.sleep(1)
                st.rerun()
            except Exception as e:
                st.error(f"Error cancelling request: {e}")
            finally:
                conn.close()

def show_employee_leave_balance():
    """Show leave balance for the current employee"""
    # Get employee profile
    employee = db.get_employee_profile(st.session_state.user_id)
    
    if not employee:
        st.error("Employee profile not found.")
        return
    
    # Get current year's leave balance
    current_year = datetime.now().year
    balance = db.get_employee_leave_balance(employee['id'], current_year)
    
    if not balance:
        st.error("Failed to retrieve leave balance information.")
        return
    
    st.write(f"### Leave Balance for {current_year}")
    
    # Create a visualization for leave balance
    leave_types = [
        "Annual Leave",
        "Sick Leave",
        "Personal Leave",
        "Maternity/Paternity Leave"
    ]
    
    total_values = [
        balance['annual_leave_total'],
        balance['sick_leave_total'],
        balance['personal_leave_total'],
        balance['maternity_leave_total']
    ]
    
    used_values = [
        balance['annual_leave_used'],
        balance['sick_leave_used'],
        balance['personal_leave_used'],
        balance['maternity_leave_used']
    ]
    
    remaining = [t - u for t, u in zip(total_values, used_values)]
    
    # Create DataFrame for visualization
    df = pd.DataFrame({
        'Leave Type': leave_types,
        'Total': total_values,
        'Used': used_values,
        'Remaining': remaining
    })
    
    # Display as a table first
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    # Create a horizontal bar chart
    fig = px.bar(
        df, 
        y='Leave Type', 
        x=['Used', 'Remaining'], 
        orientation='h',
        title="Leave Usage",
        labels={"value": "Days", "variable": "Status"},
        color_discrete_map={"Used": "#ff9999", "Remaining": "#99ccff"},
        height=400
    )
    
    # Add total values as text
    for i, leave_type in enumerate(leave_types):
        fig.add_annotation(
            x=total_values[i] + 1,
            y=i,
            text=f"Total: {total_values[i]}",
            showarrow=False,
            font=dict(size=12)
        )
    
    st.plotly_chart(fig, use_container_width=True)