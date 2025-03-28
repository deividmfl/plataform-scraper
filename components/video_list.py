import streamlit as st
import pandas as pd
from datetime import datetime

def render_video_list():
    """Render the video list page with filtering and detailed information."""
    st.markdown("""
    <div class="matrix-title">
        <h1>VIDEO <span class="red-text">DATABASE</span></h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Get videos from session state
    videos = st.session_state.videos
    
    if not videos:
        st.info("No videos found in the database. Run a scan to collect data.")
        return
    
    # Filters sidebar
    st.sidebar.markdown("""
    <div class="filter-section">
        <h3>FILTERS</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Date filter
    date_filter = st.sidebar.selectbox(
        "Time Period",
        ["All Time", "Last 24 Hours", "Last 7 Days", "Last 30 Days"]
    )
    
    # Get unique keywords from videos
    all_keywords = set()
    for video in videos:
        if 'search_keyword' in video:
            all_keywords.add(video['search_keyword'])
    
    # Keyword filter
    keyword_filter = st.sidebar.multiselect(
        "Search Keywords",
        options=sorted(list(all_keywords)),
        default=[]
    )
    
    # Platform filter
    has_platforms = st.sidebar.checkbox("Has Platform Mentions")
    has_links = st.sidebar.checkbox("Has Website Links")
    has_groups = st.sidebar.checkbox("Has Messaging Groups")
    
    # Apply filters
    filtered_videos = videos.copy()
    
    # Date filtering
    if date_filter != "All Time":
        now = datetime.now()
        if date_filter == "Last 24 Hours":
            cutoff = (now - datetime.timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
        elif date_filter == "Last 7 Days":
            cutoff = (now - datetime.timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S')
        elif date_filter == "Last 30 Days":
            cutoff = (now - datetime.timedelta(days=30)).strftime('%Y-%m-%d %H:%M:%S')
        
        filtered_videos = [v for v in filtered_videos if 'scan_date' in v and v['scan_date'] >= cutoff]
    
    # Keyword filtering
    if keyword_filter:
        filtered_videos = [v for v in filtered_videos if 'search_keyword' in v and v['search_keyword'] in keyword_filter]
    
    # Platform, links, groups filtering
    if has_platforms:
        filtered_videos = [v for v in filtered_videos if 'platforms' in v and len(v['platforms']) > 0]
    
    if has_links:
        filtered_videos = [v for v in filtered_videos if 'links' in v and len(v['links']) > 0]
    
    if has_groups:
        filtered_videos = [v for v in filtered_videos if 
                          ('groups' in v and 
                          (('whatsapp' in v['groups'] and len(v['groups']['whatsapp']) > 0) or
                           ('telegram' in v['groups'] and len(v['groups']['telegram']) > 0)))]
    
    # Display filter summary
    st.markdown(f"""
    <div class="filter-summary">
        Showing {len(filtered_videos)} of {len(videos)} videos
    </div>
    """, unsafe_allow_html=True)
    
    # Sort videos by scan date (most recent first)
    filtered_videos = sorted(
        filtered_videos,
        key=lambda x: x.get('scan_date', ''),
        reverse=True
    )
    
    # Display videos
    for video in filtered_videos:
        with st.expander(f"{video.get('title', 'Untitled Video')}"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"""
                <div class="video-info">
                    <h3 class="video-title">{video.get('title', 'Untitled')}</h3>
                    <p><span class="label">Channel:</span> {video.get('channel', 'Unknown')}</p>
                    <p><span class="label">Published:</span> {video.get('publish_date', 'Unknown date')}</p>
                    <p><span class="label">Views:</span> {video.get('view_count', 0):,}</p>
                    <p><span class="label">Likes:</span> {video.get('like_count', 0):,}</p>
                    <p><span class="label">Video URL:</span> <a href="{video.get('url', '#')}" target="_blank">{video.get('url', 'N/A')}</a></p>
                </div>
                """, unsafe_allow_html=True)
                
                # Display description (truncated)
                description = video.get('description', '')
                if description:
                    st.markdown(f"""
                    <div class="video-description">
                        <h4>Description:</h4>
                        <div class="description-text">{description[:500]}{'...' if len(description) > 500 else ''}</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            with col2:
                # Display platforms
                platforms = video.get('platforms', [])
                st.markdown(f"""
                <div class="video-metadata">
                    <h4 class="metadata-title">Platforms Mentioned ({len(platforms)})</h4>
                    <ul class="metadata-list">
                """, unsafe_allow_html=True)
                
                if platforms:
                    for platform in platforms:
                        st.markdown(f"<li>{platform}</li>", unsafe_allow_html=True)
                else:
                    st.markdown("<li>None detected</li>", unsafe_allow_html=True)
                
                st.markdown("</ul>", unsafe_allow_html=True)
                
                # Display links
                links = video.get('links', [])
                st.markdown(f"""
                <div class="video-metadata">
                    <h4 class="metadata-title">Website Links ({len(links)})</h4>
                    <ul class="metadata-list">
                """, unsafe_allow_html=True)
                
                if links:
                    for link in links:
                        st.markdown(f"""
                        <li><a href="{link.get('url', '#')}" target="_blank">{link.get('domain', 'Unknown domain')}</a></li>
                        """, unsafe_allow_html=True)
                else:
                    st.markdown("<li>None found</li>", unsafe_allow_html=True)
                
                st.markdown("</ul>", unsafe_allow_html=True)
                
                # Display groups
                groups = video.get('groups', {})
                whatsapp_groups = groups.get('whatsapp', [])
                telegram_groups = groups.get('telegram', [])
                
                st.markdown(f"""
                <div class="video-metadata">
                    <h4 class="metadata-title">Messaging Groups ({len(whatsapp_groups) + len(telegram_groups)})</h4>
                    <ul class="metadata-list">
                """, unsafe_allow_html=True)
                
                if whatsapp_groups:
                    for group in whatsapp_groups:
                        st.markdown(f"""
                        <li>WhatsApp: <a href="{group.get('url', '#')}" target="_blank">Join Group</a></li>
                        """, unsafe_allow_html=True)
                
                if telegram_groups:
                    for group in telegram_groups:
                        st.markdown(f"""
                        <li>Telegram: <a href="{group.get('url', '#')}" target="_blank">@{group.get('username', 'Unknown')}</a></li>
                        """, unsafe_allow_html=True)
                
                if not whatsapp_groups and not telegram_groups:
                    st.markdown("<li>None found</li>", unsafe_allow_html=True)
                
                st.markdown("</ul>", unsafe_allow_html=True)
