import streamlit as st
import pandas as pd
from datetime import datetime
import time
import base64
import io

def format_date(date_str):
    """Format date string for display"""
    if not date_str:
        return "Not specified"
    
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        return date_obj.strftime('%B %d, %Y')
    except:
        return date_str

def format_currency(amount):
    """Format currency for display"""
    if amount is None:
        return "$0.00"
    
    return f"${float(amount):,.2f}"

def show_loading(message="Loading..."):
    """Display a loading message with a progress bar"""
    with st.spinner(message):
        progress_bar = st.progress(0)
        for i in range(100):
            time.sleep(0.01)
            progress_bar.progress(i + 1)

def show_success_message(message, duration=1):
    """Show a success message that disappears after duration seconds"""
    success_container = st.empty()
    success_container.success(message)
    time.sleep(duration)
    success_container.empty()

def show_error_message(message, duration=2):
    """Show an error message that disappears after duration seconds"""
    error_container = st.empty()
    error_container.error(message)
    time.sleep(duration)
    error_container.empty()

def export_to_csv(df, filename="export.csv"):
    """Export DataFrame to CSV for download"""
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}" class="csv-download">Download CSV</a>'
    return href

def get_table_download_link(df, text="Download Data", filename="data.csv"):
    """Generates a link to download the DataFrame as a CSV file"""
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}" style="color:#4CAF50; text-decoration:none; padding:6px 12px; border:1px solid #4CAF50; border-radius:4px;">{text} 📥</a>'
    return href

def export_to_excel(df, filename="export.xlsx"):
    """Export DataFrame to Excel for download"""
    # This would require additional libraries like openpyxl
    # For now, just show a message that it's not implemented
    st.warning("Excel export not implemented in this version")
    return None

def validate_email(email):
    """Validate email format"""
    import re
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """Validate phone number format"""
    import re
    pattern = r'^\+?[\d\s\-\(\)]{10,15}$'
    return re.match(pattern, phone) is not None

def calculate_age(birth_date):
    """Calculate age from birth date"""
    if not birth_date:
        return None
    
    try:
        birth_date = datetime.strptime(birth_date, '%Y-%m-%d')
        today = datetime.now()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        return age
    except:
        return None

def get_current_month_year():
    """Get current month and year"""
    now = datetime.now()
    month = now.strftime('%B')
    year = now.year
    return month, year

def calculate_years_of_service(join_date):
    """Calculate years of service from join date"""
    if not join_date:
        return 0
    
    try:
        join_date = datetime.strptime(join_date, '%Y-%m-%d')
        today = datetime.now()
        years = today.year - join_date.year
        
        # Adjust if anniversary hasn't occurred yet this year
        if (today.month, today.day) < (join_date.month, join_date.day):
            years -= 1
            
        return years
    except:
        return 0