import streamlit as st
import pandas as pd
import plotly.express as px
import database
import utilities
from datetime import datetime, timedelta

def show_dashboard():
    """Display the main dashboard for the application"""
    
    st.title("Dashboard")
    
    # Get stats from database
    stats = database.get_dashboard_stats()
    
    # Display different dashboards based on user role
    if st.session_state.user_role == 'admin':
        show_admin_dashboard(stats)
    else:
        show_employee_dashboard(stats)

def show_admin_dashboard(stats):
    """Display admin dashboard with overall company statistics"""
    
    # Quick Access Buttons
    st.subheader("Quick Access")
    
    # Create a grid of quick access buttons
    quick_col1, quick_col2, quick_col3, quick_col4 = st.columns(4)
    
    # CSS for fixed height cards with reduced size
    st.markdown("""
    <style>
    .fixed-height-card {
        height: 110px;
        display: flex;
        flex-direction: column;
        padding-top: 0;
    }
    .fixed-height-card h3 {
        margin-top: 0;
        margin-bottom: 10px;
        font-size: 1.1rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    with quick_col1:
        with st.container(border=True):
            st.markdown('<div class="fixed-height-card">', unsafe_allow_html=True)
            st.markdown("### Employees")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Add New", key="quick_add_employee", use_container_width=True):
                    st.session_state.current_page = "profile"
                    st.session_state.profile_action = "add"
                    st.session_state.selected_submenu = "profile_0"
                    st.rerun()
            with col2:
                if st.button("View All", key="quick_view_employees", use_container_width=True):
                    st.session_state.current_page = "profile"
                    st.session_state.profile_action = "view"
                    st.session_state.selected_submenu = "profile_1"
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
    
    with quick_col2:
        with st.container(border=True):
            st.markdown('<div class="fixed-height-card">', unsafe_allow_html=True)
            st.markdown("### Leave")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Pending", key="quick_pending_leaves", use_container_width=True):
                    st.session_state.current_page = "leave"
                    st.rerun()
            with col2:
                if st.button("All", key="quick_all_leaves", use_container_width=True):
                    st.session_state.current_page = "leave"
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
    
    with quick_col3:
        with st.container(border=True):
            st.markdown('<div class="fixed-height-card">', unsafe_allow_html=True)
            st.markdown("### Department")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Add New", key="quick_add_dept", use_container_width=True):
                    st.session_state.current_page = "department"
                    st.rerun()
            with col2:
                if st.button("Manage", key="quick_manage_dept", use_container_width=True):
                    st.session_state.current_page = "department"
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
    
    with quick_col4:
        with st.container(border=True):
            st.markdown('<div class="fixed-height-card">', unsafe_allow_html=True)
            st.markdown("### Reports")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Generate", key="quick_generate_report", use_container_width=True):
                    st.session_state.current_page = "reports"
                    st.rerun()
            with col2:
                if st.button("Export", key="quick_export_data", use_container_width=True):
                    st.session_state.current_page = "import_export"
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Quick stats in cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div style="background-color: rgba(30, 30, 30, 0.7); border-radius: 10px; padding: 20px; text-align: center;">
            <h1 style="margin: 0; font-size: 2.5rem; color: #1E88E5;">{}</h1>
            <p style="margin: 5px 0 0 0;">Total Employees</p>
        </div>
        """.format(stats.get('total_employees', 0)), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background-color: rgba(30, 30, 30, 0.7); border-radius: 10px; padding: 20px; text-align: center;">
            <h1 style="margin: 0; font-size: 2.5rem; color: #FFC107;">{}</h1>
            <p style="margin: 5px 0 0 0;">Departments</p>
        </div>
        """.format(len(stats.get('departments', []))), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="background-color: rgba(30, 30, 30, 0.7); border-radius: 10px; padding: 20px; text-align: center;">
            <h1 style="margin: 0; font-size: 2.5rem; color: #4CAF50;">{}</h1>
            <p style="margin: 5px 0 0 0;">Pending Leaves</p>
        </div>
        """.format(stats.get('pending_leaves', 0)), unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div style="background-color: rgba(30, 30, 30, 0.7); border-radius: 10px; padding: 20px; text-align: center;">
            <h1 style="margin: 0; font-size: 2.5rem; color: #F44336;">{}</h1>
            <p style="margin: 5px 0 0 0;">Pending Inquiries</p>
        </div>
        """.format(stats.get('pending_inquiries', 0)), unsafe_allow_html=True)
    
    # Department distribution chart
    st.subheader("Employee Distribution by Department")
    
    if stats.get('departments'):
        df_dept = pd.DataFrame(stats['departments'])
        fig = px.pie(
            df_dept, 
            values='count', 
            names='name', 
            title='',
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig.update_layout(
            margin=dict(l=20, r=20, t=30, b=20),
            height=350
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No department data available")
    
    # Recent leave requests
    st.subheader("Recent Leave Requests")
    
    if stats.get('recent_leaves'):
        for leave in stats['recent_leaves']:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                status_color = 'green' if leave['status'] == 'approved' else 'orange' if leave['status'] == 'pending' else 'red'
                st.markdown(f"""
                <div style="background-color: rgba(30, 30, 30, 0.7); border-radius: 10px; padding: 15px; margin-bottom: 10px; border-left: 5px solid {status_color};">
                    <p><strong>{leave['employee_name']}</strong> • {leave['leave_type']}</p>
                    <p>Period: {leave['start_date']} to {leave['end_date']}</p>
                    <p>Status: <span style="color: {status_color};">{leave['status'].capitalize()}</span></p>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No recent leave requests")

def show_employee_dashboard(stats):
    """Display employee dashboard with personal information"""
    
    # Get employee profile and leave balance
    employee = database.get_employee_profile(st.session_state.user_id)
    
    if not employee:
        st.error("Employee profile not found")
        return
    
    # Welcome message
    st.markdown(f"""
    <div style="background-color: rgba(30, 30, 30, 0.7); border-radius: 10px; padding: 20px; margin-bottom: 20px;">
        <h2 style="margin-top: 0;">Welcome back, {employee['first_name']}!</h2>
        <p>Position: {employee['position'] or 'Not specified'}</p>
        <p>Department: {employee['department'] or 'Not specified'}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick Access Buttons
    st.subheader("Quick Access")
    
    # Create a grid of quick access buttons
    quick_col1, quick_col2, quick_col3 = st.columns(3)

    # CSS for fixed height cards (re-using style from admin dashboard)
    
    with quick_col1:
        with st.container(border=True):
            st.markdown('<div class="fixed-height-card">', unsafe_allow_html=True)
            st.markdown("### My Profile")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("View", key="quick_view_profile", use_container_width=True):
                    st.session_state.current_page = "profile"
                    st.rerun()
            with col2:
                if st.button("Edit", key="quick_edit_profile", use_container_width=True):
                    st.session_state.current_page = "profile"
                    st.session_state.edit_profile = True
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
    
    with quick_col2:
        with st.container(border=True):
            st.markdown('<div class="fixed-height-card">', unsafe_allow_html=True)
            st.markdown("### Leave")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Apply", key="quick_apply_leave", use_container_width=True):
                    st.session_state.current_page = "leave"
                    st.rerun()
            with col2:
                if st.button("History", key="quick_leave_history", use_container_width=True):
                    st.session_state.current_page = "leave"
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
    
    with quick_col3:
        with st.container(border=True):
            st.markdown('<div class="fixed-height-card">', unsafe_allow_html=True)
            st.markdown("### Inquiries")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("New", key="quick_new_inquiry", use_container_width=True):
                    st.session_state.current_page = "inquiries"
                    st.rerun()
            with col2:
                if st.button("View", key="quick_view_inquiries", use_container_width=True):
                    st.session_state.current_page = "inquiries"
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Display notifications
    notifications = database.get_notifications(st.session_state.user_id, unread_only=True)
    
    if notifications:
        st.subheader(f"Notifications ({len(notifications)})")
        
        for notification in notifications:
            with st.container(border=True):
                st.markdown(f"**{notification['title']}**")
                st.write(notification['message'])
                st.caption(f"Received: {notification['created_at']}")
                
                if st.button("Mark as Read", key=f"read_{notification['id']}"):
                    database.mark_notification_read(notification['id'])
                    st.rerun()
    
    # Show leave status
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Leave Balance")
        
        balance = database.get_employee_leave_balance(employee['id'])
        
        if balance:
            # Create a visual representation of leave balance
            leave_data = [
                {"type": "Annual Leave", "used": balance['annual_leave_used'], "total": balance['annual_leave_total']},
                {"type": "Sick Leave", "used": balance['sick_leave_used'], "total": balance['sick_leave_total']},
                {"type": "Personal Leave", "used": balance['personal_leave_used'], "total": balance['personal_leave_total']}
            ]
            
            for leave in leave_data:
                percentage = int((leave['used'] / leave['total']) * 100) if leave['total'] > 0 else 0
                remaining = leave['total'] - leave['used']
                
                # Progress bar for leave usage
                st.markdown(f"""
                <div style="margin-bottom: 15px;">
                    <p style="margin-bottom: 5px;">{leave['type']}: {remaining} days remaining</p>
                    <div style="background-color: rgba(50, 50, 50, 0.5); border-radius: 5px; height: 10px; width: 100%;">
                        <div style="background-color: {'#4CAF50' if percentage < 70 else '#FFC107' if percentage < 90 else '#F44336'}; 
                                    width: {percentage}%; height: 10px; border-radius: 5px;">
                        </div>
                    </div>
                    <p style="font-size: 0.8em; color: #AAA; margin-top: 2px;">Used {leave['used']} of {leave['total']} days</p>
                </div>
                """, unsafe_allow_html=True)
    
    with col2:
        st.subheader("My Requests")
        
        # Get pending leave requests
        leave_requests = database.get_leave_requests(employee_id=employee['id'], status="pending")
        
        if leave_requests:
            st.write(f"You have {len(leave_requests)} pending leave requests")
            
            for request in leave_requests:
                st.markdown(f"""
                <div style="background-color: rgba(30, 30, 30, 0.7); border-radius: 10px; padding: 10px; margin-bottom: 10px;">
                    <p><strong>{request['leave_type']}</strong></p>
                    <p>From {request['start_date']} to {request['end_date']}</p>
                    <p>Status: <span style="color: orange;">Pending</span></p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("You have no pending leave requests")
        
        # Get recent inquiries
        inquiries = database.get_inquiries(employee_id=employee['id'])
        
        if inquiries:
            recent_inquiries = inquiries[:3]  # Just show the 3 most recent
            
            st.write("Recent Inquiries")
            
            for inquiry in recent_inquiries:
                status_color = 'green' if inquiry['status'] == 'resolved' else 'orange'
                st.markdown(f"""
                <div style="background-color: rgba(30, 30, 30, 0.7); border-radius: 10px; padding: 10px; margin-bottom: 10px;">
                    <p><strong>{inquiry['subject']}</strong></p>
                    <p>Status: <span style="color: {status_color};">{inquiry['status'].capitalize()}</span></p>
                    <p style="font-size: 0.8em; color: #AAA;">Submitted on {inquiry['created_at'][:10]}</p>
                </div>
                """, unsafe_allow_html=True)
