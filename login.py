import streamlit as st
import database
import time

def show_login():
    """Display login screen"""
    # Title with filter effect
    st.markdown(
        """
        <style>
        .gradient-heading {
            font-size: 3rem;
            text-align: center;
            background: linear-gradient(90deg, #1E88E5, #5AB9EA, #1E88E5);
            background-size: 200% auto;
            color: transparent;
            background-clip: text;
            -webkit-background-clip: text;
            animation: gradient 3s linear infinite;
        }
        @keyframes gradient {
            0% { background-position: 0% center; }
            50% { background-position: 100% center; }
            100% { background-position: 0% center; }
        }
        </style>
        <div style="text-align: center; margin: 20px 0 30px 0;">
            <h1 class="gradient-heading">Employee Management System</h1>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # Create a centered login form with improved design
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.form("login_form"):
            st.markdown(
                """
                <style>
                div[data-testid="stForm"] {
                    background-color: rgba(30, 30, 30, 0.7);
                    border-radius: 10px;
                    padding: 20px 30px 30px 30px;
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
                    border-left: 4px solid #1E88E5;
                }
                </style>
                <h2 style='text-align: center; margin-bottom: 25px; color: #1E88E5;'>
                    <i class="fas fa-user-circle"></i> User Login
                </h2>
                """, 
                unsafe_allow_html=True
            )
            
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            
            col1, col2, col3 = st.columns([1, 3, 1])
            with col2:
                login_button = st.form_submit_button("Sign In", use_container_width=True)
            
            if login_button:
                if not username or not password:
                    st.error("Please enter both username and password")
                else:
                    with st.spinner("Logging in..."):
                        user = database.authenticate_user(username, password)
                        
                        if user:
                            st.session_state.logged_in = True
                            st.session_state.user_id = user['id']
                            st.session_state.user_role = user['role']
                            
                            # Add a success message before redirecting
                            st.success("Login successful! Redirecting to dashboard...")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("Invalid username or password")
        
        # Footer with author credits
        st.markdown(
            """
            <div style="position: fixed; bottom: 10px; left: 0; width: 100%; text-align: center; font-size: 0.8rem; color: #888;">
                Made by Ashish
            </div>
            """, 
            unsafe_allow_html=True
        )
