import streamlit as st
import pandas as pd
import time
import plotly.express as px
import database
import utilities

def show_inquiries():
    """Display employee inquiries management interface"""
    st.title("Employee Inquiries")
    
    
    # Get all inquiries
    inquiries = database.get_inquiries()
    
    tab1, tab2, tab3 = st.tabs(["All Inquiries", "Analytics", "Settings"])
    
    with tab1:
        if not inquiries:
            st.info("No inquiries found")
            return
        
        # Filter options
        col1, col2 = st.columns([2, 1])
        with col1:
            status_filter = st.selectbox("Filter by Status", ["All", "Pending", "Resolved"])
        with col2:
            search_term = st.text_input("Search by Subject or Employee")
        
        filtered_inquiries = inquiries
        if status_filter != "All":
            filtered_inquiries = [inq for inq in inquiries if inq['status'].lower() == status_filter.lower()]
        
        if search_term:
            filtered_inquiries = [inq for inq in filtered_inquiries if 
                                search_term.lower() in inq['subject'].lower() or 
                                search_term.lower() in inq['employee_name'].lower()]
        
        if not filtered_inquiries:
            st.info(f"No {status_filter.lower()} inquiries found with the given search term")
            return
        
        # Convert to DataFrame for easier handling
        df = pd.DataFrame(filtered_inquiries)
        
        # Add export option
        st.markdown(utilities.get_table_download_link(df, "Export Inquiries", "inquiries.csv"), unsafe_allow_html=True)
        
        # Display inquiries in card format
        st.subheader(f"Showing {len(filtered_inquiries)} inquiries")
        
        # Use columns for card layout (3 columns)
        cols = st.columns(3)
        
        for i, inquiry in enumerate(filtered_inquiries):
            with cols[i % 3]:
                # Card with status color
                status_color = 'green' if inquiry['status'].lower() == 'resolved' else 'orange'
                
                # Card container with hover effect
                st.markdown(f"""
                <div style="
                    background-color: rgba(30, 30, 30, 0.7);
                    border-radius: 10px;
                    padding: 15px;
                    margin-bottom: 15px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                    border-left: 5px solid {status_color};
                    transition: transform 0.3s;
                    cursor: pointer;
                ">
                    <h4 style="margin-top: 0;">{inquiry['subject']}</h4>
                    <p style="margin-bottom: 5px;"><strong>From:</strong> {inquiry['employee_name']}</p>
                    <p style="margin-bottom: 5px;"><strong>Date:</strong> {inquiry['created_at'][:10]}</p>
                    <p style="margin-bottom: 0;"><strong>Status:</strong> <span style="color: {status_color};">{inquiry['status']}</span></p>
                </div>
                """, unsafe_allow_html=True)
                
                # Button to view details
                if st.button("View Details", key=f"view_{inquiry['id']}"):
                    st.session_state.selected_inquiry = inquiry['id']
                    
        # Display selected inquiry details
        if 'selected_inquiry' in st.session_state:
            inquiry_id = st.session_state.selected_inquiry
            inquiry = next((inq for inq in filtered_inquiries if inq['id'] == inquiry_id), None)
            
            if inquiry:
                st.markdown("### Inquiry Details")
                st.markdown("""<hr style="margin: 1rem 0;"/>""", unsafe_allow_html=True)
                
                # Back button for inquiry details
                if st.button("← Back to Inquiry List", key="back_to_inquiry_list"):
                    del st.session_state.selected_inquiry
                    st.rerun()
                
                # Display inquiry details in a nicer format
                col1, col2 = st.columns([2, 1])
                with col1:
                    with st.expander(f"{inquiry['subject']} - Full Details", expanded=True):
                        # Card layout for inquiry details
                        st.markdown(f"""
                        <div style="
                            background-color: rgba(30, 30, 30, 0.7);
                            border-radius: 10px;
                            padding: 15px;
                            margin: 5px 0px;
                            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                        ">
                            <p><strong>From:</strong> {inquiry['employee_name']}</p>
                            <p><strong>Subject:</strong> {inquiry['subject']}</p>
                            <p><strong>Status:</strong> <span style="color: {'green' if inquiry['status'].lower() == 'resolved' else 'orange'};">{inquiry['status']}</span></p>
                            <p><strong>Submitted:</strong> {inquiry['created_at']}</p>
                            <hr style="margin: 10px 0;"/>
                            <p><strong>Message:</strong></p>
                            <div style="background-color: rgba(50, 50, 50, 0.4); padding: 10px; border-radius: 5px;">
                                {inquiry['message']}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Display response if available
                        if inquiry['response']:
                            st.markdown(f"""
                            <div style="
                                background-color: rgba(30, 30, 30, 0.7);
                                border-radius: 10px;
                                padding: 15px;
                                margin: 15px 0px;
                                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                                border-left: 5px solid green;
                            ">
                                <p><strong>Response:</strong> ({inquiry['response_date']})</p>
                                <div style="background-color: rgba(50, 50, 50, 0.4); padding: 10px; border-radius: 5px;">
                                    {inquiry['response']}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                
                with col2:
                    # Response form (if inquiry is pending)
                    if inquiry['status'].lower() == 'pending':
                        with st.form(key=f"response_form_{inquiry_id}"):
                            st.subheader("Respond to Inquiry")
                            response = st.text_area("Your Response", height=150)
                            
                            if st.form_submit_button("Submit Response"):
                                if response:
                                    if database.respond_to_inquiry(inquiry_id, response):
                                        st.success("Response submitted successfully!")
                                        time.sleep(1)
                                        st.rerun()
                                    else:
                                        st.error("Failed to submit response. Please try again.")
                                else:
                                    st.warning("Please enter a response.")
    
    with tab2:
        st.subheader("Inquiry Analytics")
        
        if not inquiries:
            st.info("No data available for analytics.")
            return
        
        # Convert to DataFrame for analytics
        df = pd.DataFrame(inquiries)
        
        # Status distribution
        status_counts = df['status'].value_counts().reset_index()
        status_counts.columns = ['Status', 'Count']
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Status distribution pie chart
            fig1 = px.pie(
                status_counts, 
                values='Count', 
                names='Status', 
                title="Inquiry Status Distribution",
                color_discrete_sequence=px.colors.qualitative.Set3,
                hole=0.4
            )
            fig1.update_layout(
                margin=dict(l=20, r=20, t=30, b=20),
                height=300
            )
            st.plotly_chart(fig1, use_container_width=True)
        
        # If there are timestamps, create time-based visualizations
        if 'created_at' in df.columns:
            try:
                # Convert timestamps to datetime format
                df['created_date'] = pd.to_datetime(df['created_at'])
                df['month'] = df['created_date'].dt.strftime('%Y-%m')
                
                # Group by month and count
                monthly_counts = df.groupby('month').size().reset_index(name='count')
                
                with col2:
                    # Monthly trend line chart
                    fig2 = px.line(
                        monthly_counts, 
                        x='month', 
                        y='count', 
                        title="Monthly Inquiry Trends",
                        markers=True
                    )
                    fig2.update_layout(
                        xaxis_title="Month",
                        yaxis_title="Number of Inquiries",
                        margin=dict(l=20, r=20, t=30, b=20),
                        height=300
                    )
                    st.plotly_chart(fig2, use_container_width=True)
            except Exception as e:
                st.error(f"Error generating time-based analytics: {e}")
    
    with tab3:
        st.subheader("Inquiry Settings")
        st.info("This section is under development. It will include settings for categorization, auto-responses, and notification preferences.")

def show_employee_inquiries():
    """Display inquiries interface for employees"""
    st.title("My Inquiries")
    
    # Get employee profile and inquiries
    employee = database.get_employee_profile(st.session_state.user_id)
    
    if not employee:
        st.error("Employee profile not found.")
        return
    
    # Get all inquiries for this employee
    inquiries = database.get_inquiries(employee_id=employee['id'])
    
    tab1, tab2 = st.tabs(["My Inquiries", "Submit New Inquiry"])
    
    with tab1:
        if not inquiries:
            st.info("You haven't submitted any inquiries yet.")
        else:
            # Display inquiries
            st.subheader(f"You have {len(inquiries)} inquiries")
            
            # Filter options
            status_filter = st.selectbox("Filter by Status", ["All", "Pending", "Resolved"])
            
            filtered_inquiries = inquiries
            if status_filter != "All":
                filtered_inquiries = [inq for inq in inquiries if inq['status'].lower() == status_filter.lower()]
            
            if not filtered_inquiries:
                st.info(f"No {status_filter.lower()} inquiries found.")
            else:
                # Display inquiries as cards
                for inquiry in filtered_inquiries:
                    status_color = 'green' if inquiry['status'].lower() == 'resolved' else 'orange'
                    
                    with st.expander(f"{inquiry['subject']} ({inquiry['created_at'][:10]}) - {inquiry['status']}"):
                        st.markdown(f"""
                        <div style="margin-bottom: 10px;">
                            <p><strong>Status:</strong> <span style="color: {status_color};">{inquiry['status']}</span></p>
                            <p><strong>Message:</strong></p>
                            <div style="background-color: rgba(50, 50, 50, 0.4); padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                                {inquiry['message']}
                            </div>
                        """, unsafe_allow_html=True)
                        
                        # Display response if available
                        if inquiry['response']:
                            st.markdown(f"""
                            <p><strong>Response:</strong> ({inquiry['response_date']})</p>
                            <div style="background-color: rgba(50, 50, 50, 0.4); padding: 10px; border-radius: 5px;">
                                {inquiry['response']}
                            </div>
                            """, unsafe_allow_html=True)
                        
                        st.markdown("</div>", unsafe_allow_html=True)
    
    with tab2:
        st.subheader("Submit a New Inquiry")
        
        with st.form("new_inquiry_form"):
            subject = st.text_input("Subject")
            message = st.text_area("Message", height=150)
            
            submitted = st.form_submit_button("Submit Inquiry")
            
            if submitted:
                if not subject or not message:
                    st.error("Please provide both subject and message.")
                else:
                    result = database.add_inquiry(employee['id'], subject, message)
                    
                    if result:
                        st.success("Inquiry submitted successfully!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Failed to submit inquiry. Please try again.")