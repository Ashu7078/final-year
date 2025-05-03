import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import database
import utilities
import time

def show_leave_application():
    """Display form for applying for leave"""
    st.title("Apply for Leave")
    
    # Get employee profile
    employee = database.get_employee_profile(st.session_state.user_id)
    
    if not employee:
        st.error("Employee profile not found")
        return
    
    # Create tabs for different sections
    tab1, tab2, tab3 = st.tabs(["Apply for Leave", "My Requests", "Leave Balance"])
    
    with tab1:
        st.subheader("Submit Leave Application")
        
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
            balance = database.get_employee_leave_balance(employee['id'])
            
            if balance:
                # Show available balance based on selected leave type
                if leave_type == "Annual Leave":
                    available = balance['annual_leave_total'] - balance['annual_leave_used']
                    st.info(f"Available balance: {available} days (used {balance['annual_leave_used']} of {balance['annual_leave_total']})", icon="ℹ️")
                elif leave_type == "Sick Leave":
                    available = balance['sick_leave_total'] - balance['sick_leave_used']
                    st.info(f"Available balance: {available} days (used {balance['sick_leave_used']} of {balance['sick_leave_total']})", icon="ℹ️")
                elif leave_type == "Personal Leave":
                    available = balance['personal_leave_total'] - balance['personal_leave_used']
                    st.info(f"Available balance: {available} days (used {balance['personal_leave_used']} of {balance['personal_leave_total']})", icon="ℹ️")
                elif leave_type == "Maternity/Paternity Leave":
                    available = balance['maternity_leave_total'] - balance['maternity_leave_used']
                    st.info(f"Available balance: {available} days (used {balance['maternity_leave_used']} of {balance['maternity_leave_total']})", icon="ℹ️")
            
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
                    result = database.submit_leave_request(
                        employee['id'],
                        leave_type,
                        start_date.strftime("%Y-%m-%d"),
                        end_date.strftime("%Y-%m-%d"),
                        reason
                    )
                    
                    if result:
                        st.success("Leave request submitted successfully!")
                        time.sleep(2)
                        st.rerun()
                    else:
                        st.error("Failed to submit leave request. Please try again.")
    
    with tab2:
        st.subheader("My Leave Requests")
        
        # Get all leave requests for this employee
        leave_requests = database.get_leave_requests(employee_id=employee['id'])
        
        if not leave_requests:
            st.info("You have no leave requests.")
        else:
            # Filter tabs
            filter_tab1, filter_tab2, filter_tab3, filter_tab4 = st.tabs(["All Requests", "Pending", "Approved", "Rejected"])
            
            with filter_tab1:
                show_leave_requests_table(leave_requests)
            
            with filter_tab2:
                pending_requests = [r for r in leave_requests if r['status'] == 'pending']
                if pending_requests:
                    show_leave_requests_table(pending_requests)
                else:
                    st.info("No pending leave requests.")
            
            with filter_tab3:
                approved_requests = [r for r in leave_requests if r['status'] == 'approved']
                if approved_requests:
                    show_leave_requests_table(approved_requests)
                else:
                    st.info("No approved leave requests.")
            
            with filter_tab4:
                rejected_requests = [r for r in leave_requests if r['status'] == 'rejected']
                if rejected_requests:
                    show_leave_requests_table(rejected_requests)
                else:
                    st.info("No rejected leave requests.")
    
    with tab3:
        st.subheader("Leave Balance")
        
        # Get current year's leave balance
        current_year = datetime.now().year
        balance = database.get_employee_leave_balance(employee['id'], current_year)
        
        if not balance:
            st.error("Failed to retrieve leave balance information.")
        else:
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

# Helper function to display leave requests in a table
def show_leave_requests_table(requests):
    """Display leave requests as a table with detailed view"""
    if not requests:
        st.info("No leave requests found.")
        return
        
    # Convert to DataFrame
    df = pd.DataFrame(requests)
    
    # Display as a table
    st.dataframe(
        df[['id', 'leave_type', 'start_date', 'end_date', 'days_count', 'status', 'created_at']].rename(
            columns={
                'id': 'ID',
                'leave_type': 'Leave Type',
                'start_date': 'Start Date',
                'end_date': 'End Date',
                'days_count': 'Days',
                'status': 'Status',
                'created_at': 'Applied On'
            }
        ),
        use_container_width=True
    )
    
    # Show detail view for selected leave request
    if len(df) > 0:
        selected_leave = st.selectbox(
            "Select Leave Request for Details", 
            options=df['id'].tolist(),
            format_func=lambda x: f"Request #{x} - {df[df['id']==x]['leave_type'].iloc[0]} ({df[df['id']==x]['start_date'].iloc[0]} to {df[df['id']==x]['end_date'].iloc[0]})"
        )
        
        if selected_leave:
            # Get the selected leave request
            leave_request = next((x for x in requests if x['id'] == selected_leave), None)
            
            if leave_request:
                st.write("### Leave Request Details")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Leave Type:** {leave_request['leave_type']}")
                    st.write(f"**Start Date:** {leave_request['start_date']}")
                    st.write(f"**End Date:** {leave_request['end_date']}")
                    st.write(f"**Total Days:** {leave_request['days_count']}")
                
                with col2:
                    st.write(f"**Status:** {leave_request['status'].capitalize()}")
                    st.write(f"**Applied On:** {leave_request['created_at']}")
                    
                    if 'approved_by' in leave_request and leave_request['approved_by']:
                        st.write(f"**Processed By:** {leave_request['approved_by']}")
                        
                    if 'response_date' in leave_request and leave_request['response_date']:
                        st.write(f"**Response Date:** {leave_request['response_date']}")
                
                st.write("**Reason:**")
                st.markdown(f"<div style='background-color: rgba(100,100,100,0.2); padding: 10px; border-radius: 5px;'>{leave_request['reason']}</div>", unsafe_allow_html=True)
                
                if leave_request['status'] == 'pending':
                    if st.button("Cancel Request", key=f"cancel_{selected_leave}", type="primary"):
                        # Cancel the leave request
                        conn = database.get_connection()
                        cursor = conn.cursor()
                        
                        try:
                            cursor.execute("UPDATE leave_requests SET status = 'cancelled', response_date = datetime('now') WHERE id = ?", (selected_leave,))
                            conn.commit()
                            st.success("Leave request cancelled")
                            time.sleep(2)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error cancelling request: {e}")
                        finally:
                            conn.close()