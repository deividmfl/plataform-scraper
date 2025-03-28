import streamlit as st
import pandas as pd
import time
import os
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler

# Import components
from components.dashboard import render_dashboard
from components.video_list import render_video_list
from components.settings import render_settings

# Import scrapers and utilities
from scrapers.youtube_scraper import search_youtube_videos
from utils.text_extraction import extract_platforms_and_links
from utils.data_storage import load_videos, save_videos
from utils.notification import send_notification

# Set page configuration
st.set_page_config(
    page_title="Matrix Investment Tracker",
    page_icon="🕵️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS to match Matrix theme
def add_custom_css():
    with open("assets/custom.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Initialize session states
if 'videos' not in st.session_state:
    st.session_state.videos = load_videos()
if 'last_scan' not in st.session_state:
    st.session_state.last_scan = None
if 'scanning' not in st.session_state:
    st.session_state.scanning = False
if 'scan_results' not in st.session_state:
    st.session_state.scan_results = {"new": 0, "total": 0}
if 'notification_email' not in st.session_state:
    st.session_state.notification_email = ""

# Add background images and styling
def add_background():
    st.markdown(
        """
        <div class="matrix-overlay"></div>
        """,
        unsafe_allow_html=True
    )

# Function to run the scan
def run_scan():
    st.session_state.scanning = True
    
    # Get search parameters from settings
    search_days = st.session_state.get('search_days', 30)
    keywords = st.session_state.get('keywords', [
        'plataforma de investimento', 
        'pagamento instantâneo', 
        'prova de pagamento', 
        'multinível'
    ])
    
    # Calculate search period
    search_period = (datetime.now() - timedelta(days=search_days)).strftime('%Y-%m-%d')
    
    # Get existing video IDs to avoid duplicates
    existing_ids = set([v['id'] for v in st.session_state.videos])
    
    # Initialize counters
    new_videos = 0
    
    # Search YouTube for each keyword
    for keyword in keywords:
        try:
            videos = search_youtube_videos(keyword, search_period)
            
            # Process each video
            for video in videos:
                if video['id'] not in existing_ids:
                    # Extract platforms, links and groups
                    platforms, links, groups = extract_platforms_and_links(video)
                    video['platforms'] = platforms
                    video['links'] = links
                    video['groups'] = groups
                    video['scan_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    
                    # Add to session state
                    st.session_state.videos.append(video)
                    new_videos += 1
                    
                    # Send notification if configured
                    if st.session_state.notification_email:
                        send_notification(st.session_state.notification_email, video)
        
        except Exception as e:
            st.error(f"Error scanning for keyword '{keyword}': {str(e)}")
    
    # Save videos to storage
    save_videos(st.session_state.videos)
    
    # Update scan results
    st.session_state.scan_results = {
        "new": new_videos,
        "total": len(st.session_state.videos)
    }
    
    st.session_state.last_scan = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    st.session_state.scanning = False
    st.rerun()

# Main application
def main():
    # Add custom styling
    add_custom_css()
    add_background()
    
    # Sidebar with matrix-style header
    st.sidebar.markdown("""
    <div class="matrix-header">
        <h1>MATRIX <span class="red-text">INVESTMENT</span> <br>TRACKER</h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation in sidebar
    nav = st.sidebar.radio(
        "Navigation",
        ["Dashboard", "Video List", "Settings"]
    )
    
    # Scan button in sidebar
    if st.sidebar.button("🔍 Scan Now", disabled=st.session_state.scanning):
        run_scan()
    
    # Show scanning status
    if st.session_state.scanning:
        st.sidebar.markdown("""
        <div class="scanning-text">SCANNING...</div>
        """, unsafe_allow_html=True)
    
    # Show last scan time
    if st.session_state.last_scan:
        st.sidebar.markdown(f"""
        <div class="last-scan">Last scan: {st.session_state.last_scan}</div>
        """, unsafe_allow_html=True)
    
    # Display appropriate component based on navigation
    if nav == "Dashboard":
        render_dashboard()
    elif nav == "Video List":
        render_video_list()
    elif nav == "Settings":
        render_settings()
    
    # Matrix-style footer
    st.sidebar.markdown("""
    <div class="matrix-footer">
        FOLLOW THE WHITE RABBIT
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    # Initialize the scheduler
    scheduler = BackgroundScheduler()
    
    # Schedule a scan every 12 hours
    @scheduler.scheduled_job('interval', hours=12)
    def scheduled_scan():
        if not st.session_state.scanning:
            run_scan()
    
    # Start the scheduler
    scheduler.start()
    
    # Run the main application
    main()
