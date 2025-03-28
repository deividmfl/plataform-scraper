import streamlit as st
import pandas as pd
import time
import os
import datetime
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import requests
from io import BytesIO

from scrapers.youtube_scraper import YouTubeScraper
from scrapers.text_processor import TextProcessor
from utils.database import Database
from utils.notification import EmailNotifier
from utils.scheduler import Scheduler
from assets.matrix_style import apply_matrix_style

# Apply Matrix-inspired styling
apply_matrix_style()

# Initialize session state
if 'scan_running' not in st.session_state:
    st.session_state.scan_running = False
if 'last_scan' not in st.session_state:
    st.session_state.last_scan = None
if 'video_count' not in st.session_state:
    st.session_state.video_count = 0
if 'platforms_detected' not in st.session_state:
    st.session_state.platforms_detected = 0
if 'messaging_groups' not in st.session_state:
    st.session_state.messaging_groups = 0

# Initialize database
db = Database()
# Initialize text processor
text_processor = TextProcessor()
# Initialize notifier
email_notifier = EmailNotifier()

# Function to initiate scan
def start_scan(keywords, days_back, max_videos):
    st.session_state.scan_running = True
    
    # Initialize scraper
    youtube_scraper = YouTubeScraper()
    
    # Get videos
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Perform search for each keyword
    all_videos = []
    for i, keyword in enumerate(keywords):
        status_text.text(f"Scanning YouTube for: {keyword}")
        videos = youtube_scraper.search_videos(keyword, days_back, max_videos // len(keywords))
        all_videos.extend(videos)
        progress_bar.progress((i + 1) / len(keywords) * 0.5)
    
    # Process videos
    processed_videos = []
    for i, video in enumerate(all_videos):
        status_text.text(f"Processing video {i+1}/{len(all_videos)}: {video['title']}")
        
        # Extract description and metadata
        video_details = youtube_scraper.get_video_details(video['id'])
        
        # Process description for platforms, links and messaging groups
        if 'description' in video_details:
            platforms = text_processor.extract_platforms(video_details['description'])
            links = text_processor.extract_links(video_details['description'])
            messaging_groups = text_processor.extract_messaging_groups(video_details['description'])
            
            video_details['platforms'] = platforms
            video_details['links'] = links
            video_details['messaging_groups'] = messaging_groups
            
            processed_videos.append(video_details)
        
        progress_bar.progress(0.5 + (i + 1) / len(all_videos) * 0.5)
    
    # Save to database
    db.save_videos(processed_videos)
    
    # Update statistics
    st.session_state.video_count = len(processed_videos)
    st.session_state.platforms_detected = sum(len(v.get('platforms', [])) for v in processed_videos)
    st.session_state.messaging_groups = sum(len(v.get('messaging_groups', [])) for v in processed_videos)
    st.session_state.last_scan = datetime.datetime.now()
    
    # Send notification if new videos were found
    if processed_videos:
        email_notifier.send_notification(f"Found {len(processed_videos)} new investment videos", processed_videos)
    
    status_text.text("Scan completed!")
    st.session_state.scan_running = False

# Main app layout
st.title("Investment Platform Tracker")
st.markdown("<div style='text-align:center;'><h3 style='color:#00ff00;'>Matrix-Inspired Video Intelligence System</h3></div>", unsafe_allow_html=True)

# Sidebar - Configuration and Controls
with st.sidebar:
    # Load background images
    try:
        # Attempt to load image from URL
        response = requests.get("https://images.unsplash.com/photo-1606606767399-01e271823a2e")
        matrix_bg = Image.open(BytesIO(response.content))
        st.image(matrix_bg, use_column_width=True)
    except:
        st.write("Matrix Code Visualization")
    
    st.header("Scan Parameters")
    
    # Input keywords
    keywords_input = st.text_area("Keywords (one per line)", 
                                "plataforma de investimento\npagamento instantâneo\nprova de pagamento\nmultinível")
    keywords = [k.strip() for k in keywords_input.split("\n") if k.strip()]
    
    # Days to look back
    days_back = st.slider("Days to look back", 1, 30, 7)
    
    # Max videos to retrieve
    max_videos = st.slider("Maximum videos to scan", 10, 200, 50)
    
    # Email notification settings
    st.header("Notifications")
    email = st.text_input("Email for notifications", "user@example.com")
    
    # Scan button
    if st.button("Start Scan"):
        if not st.session_state.scan_running:
            start_scan(keywords, days_back, max_videos)
    
    # Display last scan time
    if st.session_state.last_scan:
        st.write(f"Last scan: {st.session_state.last_scan.strftime('%Y-%m-%d %H:%M')}")

# Main dashboard area
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Videos Tracked", st.session_state.video_count)

with col2:
    st.metric("Platforms Detected", st.session_state.platforms_detected)

with col3:
    st.metric("Messaging Groups", st.session_state.messaging_groups)

# Tabs for different views
tab1, tab2, tab3 = st.tabs(["Videos", "Platforms", "Messaging Groups"])

with tab1:
    # Display video data
    videos = db.get_videos()
    if videos:
        # Create a dataframe for display
        video_df = pd.DataFrame(videos)
        
        for i, video in enumerate(videos):
            with st.expander(f"{i+1}. {video.get('title', 'Untitled')}"):
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    if 'thumbnail' in video:
                        st.image(video['thumbnail'], use_column_width=True)
                    st.write(f"**Channel:** {video.get('channel_name', 'Unknown')}")
                    st.write(f"**Published:** {video.get('publish_date', 'Unknown')}")
                    st.write(f"**Views:** {video.get('view_count', 'Unknown')}")
                    st.write(f"**Watch:** [Open on YouTube](https://youtube.com/watch?v={video.get('id', '')})")
                
                with col2:
                    st.write("**Description:**")
                    st.write(video.get('description', 'No description available')[:300] + "...")
                    
                    st.write("**Detected Platforms:**")
                    if 'platforms' in video and video['platforms']:
                        for platform in video['platforms']:
                            st.write(f"- {platform}")
                    else:
                        st.write("No investment platforms detected")
                    
                    st.write("**Detected Links:**")
                    if 'links' in video and video['links']:
                        for link in video['links']:
                            st.write(f"- [{link}]({link})")
                    else:
                        st.write("No links detected")
                    
                    st.write("**Messaging Groups:**")
                    if 'messaging_groups' in video and video['messaging_groups']:
                        for group in video['messaging_groups']:
                            st.write(f"- {group['platform']}: {group['link']}")
                    else:
                        st.write("No messaging groups detected")
    else:
        st.info("No videos have been scanned yet. Start a scan to track investment videos.")

with tab2:
    # Platform statistics
    platform_data = db.get_platform_statistics()
    if platform_data:
        st.subheader("Most Mentioned Investment Platforms")
        
        # Create bar chart
        fig = px.bar(
            platform_data, 
            x='count', 
            y='platform', 
            orientation='h',
            color='count',
            color_continuous_scale=['#00ff00', '#ff0000'],
            title="Platform Mentions"
        )
        
        fig.update_layout(
            plot_bgcolor='black',
            paper_bgcolor='black',
            font_color='#00ff00',
            yaxis_title="",
            xaxis_title="Mention Count"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Platform details
        for platform, count in platform_data.items():
            with st.expander(f"{platform} - {count} mentions"):
                videos = db.get_videos_by_platform(platform)
                for video in videos:
                    st.write(f"- [{video.get('title', 'Untitled')}](https://youtube.com/watch?v={video.get('id', '')})")
    else:
        st.info("No platform data available. Start a scan to track investment platforms.")

with tab3:
    # Messaging group statistics
    groups_data = db.get_messaging_group_statistics()
    if groups_data:
        st.subheader("Detected Messaging Groups")
        
        # Group by platform (WhatsApp, Telegram, etc.)
        platform_counts = {}
        for group in groups_data:
            platform = group.get('platform', 'Unknown')
            if platform in platform_counts:
                platform_counts[platform] += 1
            else:
                platform_counts[platform] = 1
        
        # Create pie chart
        fig = px.pie(
            names=list(platform_counts.keys()),
            values=list(platform_counts.values()),
            title="Messaging Groups by Platform",
            color_discrete_sequence=['#00ff00', '#ff0000', '#ffffff', '#00ffff']
        )
        
        fig.update_layout(
            plot_bgcolor='black',
            paper_bgcolor='black',
            font_color='#00ff00'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # List all groups
        st.subheader("All Detected Groups")
        for group in groups_data:
            st.write(f"- {group.get('platform', 'Unknown')}: [{group.get('name', 'Unnamed Group')}]({group.get('link', '#')})")
    else:
        st.info("No messaging groups detected yet. Start a scan to find investment-related groups.")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:#00ff00;'>"
    "MATRIX-INSPIRED INVESTMENT PLATFORM TRACKER | FOLLOW THE WHITE RABBIT"
    "</div>", 
    unsafe_allow_html=True
)
