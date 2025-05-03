import streamlit as st
import database

def show_navigation():
    """Display navigation sidebar and top bar"""
    
    # Add JavaScript to ensure page is fullscreen when nav buttons are clicked
    st.markdown(
        """
        <script>
        // Function to toggle fullscreen
        function toggleFullScreen() {
            if (!document.fullscreenElement) {
                document.documentElement.requestFullscreen().catch(err => {
                    console.log(`Error attempting to enable full-screen mode: ${err.message}`);
                });
            }
        }
        
        // Add click event listeners to navigation buttons after page loads
        document.addEventListener('DOMContentLoaded', function() {
            // Give DOM time to fully render
            setTimeout(function() {
                // Find all sidebar navigation buttons and add click handler
                const navButtons = document.querySelectorAll('button[data-testid="baseButton-secondary"]');
                navButtons.forEach(button => {
                    button.addEventListener('click', toggleFullScreen);
                });
            }, 1000);
        });
        </script>
        """,
        unsafe_allow_html=True
    )
    
    # Get unread notifications count
    unread_notifications = database.get_notifications(st.session_state.user_id, unread_only=True)
    notifications_count = len(unread_notifications)
    
    # Top navigation bar - no heading as requested
    # We only want the heading on login page, not here
    
    # Sidebar navigation
    st.sidebar.markdown("## Navigation")
    
    if st.session_state.user_role == 'admin':
        menu_options = {
            "Dashboard": {"icon": "📊", "page": "home", "desc": "View system overview and metrics"},
            "Employees": {"icon": "👥", "page": "profile", "desc": "Manage employee profiles and settings", "submenu": ["Add Employee", "View Employees", "Download Data"]},
            "Leave": {"icon": "📅", "page": "leave", "desc": "Approve and manage leave requests"},
            "Department": {"icon": "🏢", "page": "department", "desc": "Manage departments and teams"},
            "Notification": {"icon": "🔔", "page": "notification", "desc": "Send notifications to employees"},
            "Payroll": {"icon": "💰", "page": "payroll", "desc": "Manage salaries and payments"},
            "Inquiries": {"icon": "📬", "page": "inquiries", "desc": "Handle employee inquiries"},
            "Reports": {"icon": "📈", "page": "reports", "desc": "Generate and view reports"},
            "Import/Export": {"icon": "📤", "page": "import_export", "desc": "Import and export system data"}
        }
    else:
        menu_options = {
            "Dashboard": {"icon": "📊", "page": "home", "desc": "View your dashboard"},
            "My Profile": {"icon": "👤", "page": "profile", "desc": "Manage your profile information"},
            "Leave": {"icon": "📅", "page": "leave", "desc": "Apply for leave and view requests"},
            "My Inquiries": {"icon": "📬", "page": "inquiries", "desc": "Submit and view your inquiries"},
            "Notification": {"icon": "🔔", "page": "notification", "desc": "View your notifications"}
        }
    
    for option_label, option_data in menu_options.items():
        icon = option_data["icon"]
        page = option_data["page"]
        desc = option_data["desc"]
        
        # Highlight current page
        if st.session_state.current_page == page:
            st.sidebar.markdown(
                f"""
                <div style="background-color: rgba(30, 136, 229, 0.2); padding: 10px; border-radius: 5px; margin-bottom: 5px; cursor: pointer;" title="{desc}">
                    <span style="font-size: 1.2rem;"><strong>{option_label}</strong></span>
                    <div style="font-size: 0.8rem; color: #AAA; margin-top: 5px;">{desc}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Show submenu if available and the option is selected
            if "submenu" in option_data and len(option_data["submenu"]) > 0:
                st.sidebar.markdown("<div style='margin-left: 20px;'>", unsafe_allow_html=True)
                for i, submenu_item in enumerate(option_data["submenu"]):
                    if 'selected_submenu' not in st.session_state:
                        st.session_state.selected_submenu = None
                    
                    # Highlight the selected submenu
                    if st.session_state.selected_submenu == f"{page}_{i}":
                        st.sidebar.markdown(
                            f"""
                            <div style="background-color: rgba(30, 136, 229, 0.1); padding: 5px 10px; border-radius: 5px; margin-bottom: 5px; border-left: 3px solid #1E88E5;">
                                <span style="font-size: 0.9rem;"><strong>{submenu_item}</strong></span>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                    else:
                        if st.sidebar.button(f"{submenu_item}", key=f"submenu_{page}_{i}", use_container_width=True):
                            st.session_state.selected_submenu = f"{page}_{i}"
                            # Additional actions based on which submenu was selected
                            if page == "profile" and i == 0:  # Add Employee
                                st.session_state.profile_action = "add"
                            elif page == "profile" and i == 1:  # View Employees
                                st.session_state.profile_action = "view"
                            elif page == "profile" and i == 2:  # Download Data
                                st.session_state.profile_action = "download"
                            st.rerun()
                st.sidebar.markdown("</div>", unsafe_allow_html=True)
                
        else:
            if st.sidebar.button(f"{option_label}", help=desc, key=f"nav_{page}", use_container_width=True):
                st.session_state.current_page = page
                # Reset page-specific state variables
                if 'selected_inquiry' in st.session_state:
                    del st.session_state.selected_inquiry
                if 'view_leave_details' in st.session_state:
                    del st.session_state.view_leave_details
                if 'selected_submenu' in st.session_state:
                    del st.session_state.selected_submenu
                st.rerun()
    
    # Show notifications in sidebar
    if notifications_count > 0:
        with st.sidebar.expander(f"Notifications ({notifications_count})", expanded=False):
            for notification in unread_notifications:
                st.markdown(
                    f"""
                    <div style="background-color: rgba(30, 30, 30, 0.7); border-radius: 5px; padding: 10px; margin-bottom: 5px;">
                        <strong>{notification['title']}</strong>
                        <p style="margin: 5px 0;">{notification['message']}</p>
                        <p style="font-size: 0.8rem; color: #AAA; margin: 0;">{notification['created_at']}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                if st.button("Mark as Read", key=f"mark_read_{notification['id']}"):
                    database.mark_notification_read(notification['id'])
                    st.rerun()
    
    # Display user role info
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"Logged in as: **{st.session_state.user_role.capitalize()}**")
    
    # Logout button at the bottom of sidebar
    st.sidebar.markdown("---")
    col1, col2, col3 = st.sidebar.columns([1, 2, 1])
    with col2:
        if st.button("🔒 Logout", key="sidebar_logout", use_container_width=True):
            for key in st.session_state.keys():
                del st.session_state[key]
            st.rerun()
