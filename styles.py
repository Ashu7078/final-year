import streamlit as st

def apply_styles():
    """Apply custom CSS styles to the Streamlit app"""
    
    # Custom CSS to enhance the UI
    st.markdown("""
    <style>
    /* Global styles */
    .stApp {
        font-family: 'Roboto', sans-serif;
    }
    
    /* Header styles */
    h1, h2, h3 {
        color: #1E88E5;
        font-weight: 700;
    }
    
    /* Card-like container */
    .card {
        background-color: rgba(30, 30, 30, 0.7);
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1), 0 1px 3px rgba(0, 0, 0, 0.08);
        margin-bottom: 20px;
    }
    
    /* Button styles */
    .stButton > button {
        background-color: rgba(30, 30, 30, 0.7) !important;
        color: white !important;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background-color: rgba(50, 50, 50, 0.9) !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    
    /* Sidebar style */
    .css-1d391kg {
        background-color: rgba(30, 30, 30, 0.8);
    }
    
    /* Form input styling */
    .stTextInput > div > div > input {
        border-radius: 5px;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        font-weight: 600;
        color: #1E88E5;
    }
    
    /* Table styling */
    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
    }
    
    /* Metric styling */
    .stMetric {
        background-color: rgba(30, 30, 30, 0.6);
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 20px;
    }
    
    /* Animation for notification badge */
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.1); }
        100% { transform: scale(1); }
    }
    
    .notification-badge {
        color: #FF5252;
        animation: pulse 1.5s infinite;
    }
    
    /* Fixed footer - always at bottom of screen */
    footer {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background-color: rgba(30, 30, 30, 0.7);
        padding: 10px 15px;
        text-align: center;
        font-size: 0.9rem;
        color: #fff;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
        z-index: 999;
    }
    
    /* Add some bottom margin for content to prevent overlap with footer */
    .main-content {
        margin-bottom: 50px;
    }
    
    </style>
    """, unsafe_allow_html=True)
    
    # Apply dark background
    page_bg = '''
    <style>
    .stApp {
        background-image: linear-gradient(to bottom, rgba(0, 0, 0, 0.8), rgba(0, 0, 0, 0.6)), url("https://images.unsplash.com/photo-1497215842964-222b430dc094?ixlib=rb-1.2.1&auto=format&fit=crop&w=1950&q=80");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }
    </style>
    '''
    st.markdown(page_bg, unsafe_allow_html=True)
    
    # Add footer with "Made by Ashish"
    st.markdown(
        """
        <footer>
            Made by Ashish
        </footer>
        """,
        unsafe_allow_html=True
    )