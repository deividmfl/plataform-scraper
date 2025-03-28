import streamlit as st
import pandas as pd
import time
import datetime
import json
import os
import re
from urllib.parse import urlparse
import plotly.express as px
import plotly.graph_objects as go

# Import custom modules
from scrapers.youtube_scraper import YouTubeScraper
from scrapers.text_processor import TextProcessor
from scrapers.web_scraper import WebScraper
from assets.terminal_style import (
    apply_terminal_style, terminal_container, console_print, 
    typing_animation, glow_text, header, tooltip, 
    warning, success, blinking_cursor
)

# Configuration
st.set_page_config(
    page_title="Security Scanner - Plataform Monitor",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply terminal style
apply_terminal_style()

# Function to ensure data directory exists
def ensure_data_directory():
    """Ensure the data directory exists."""
    os.makedirs('data', exist_ok=True)

# Database functions
def load_videos():
    """Load videos from JSON file."""
    ensure_data_directory()
    try:
        if os.path.exists('data/videos.json'):
            with open('data/videos.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except Exception as e:
        st.error(f"Error loading videos: {str(e)}")
        return []

def save_videos(videos):
    """Save videos to JSON file."""
    ensure_data_directory()
    try:
        with open('data/videos.json', 'w', encoding='utf-8') as f:
            json.dump(videos, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"Error saving videos: {str(e)}")

# Data processing functions
def get_platform_statistics():
    """Get statistics about the most mentioned platforms."""
    videos = load_videos()
    
    # Count platform mentions
    platform_counts = {}
    for video in videos:
        for platform in video.get('platforms', []):
            if platform in platform_counts:
                platform_counts[platform] += 1
            else:
                platform_counts[platform] = 1
    
    # Convert to DataFrame for easier visualization
    platform_data = pd.DataFrame([
        {"platform": platform, "count": count}
        for platform, count in sorted(platform_counts.items(), key=lambda x: x[1], reverse=True)
    ])
    
    return platform_data

def get_messaging_group_statistics():
    """Get statistics about messaging groups."""
    videos = load_videos()
    
    # Collect all messaging groups
    groups = []
    for video in videos:
        for group in video.get('messaging_groups', []):
            groups.append(group)
    
    return groups

def get_website_statistics():
    """Get statistics about mentioned websites."""
    videos = load_videos()
    
    # Extract domain from URLs and count frequencies
    domain_counts = {}
    website_details = {}
    
    for video in videos:
        for url in video.get('links', []):
            try:
                # Parse URL to get domain
                parsed = urlparse(url)
                domain = parsed.netloc
                
                # Skip empty domains
                if not domain:
                    continue
                
                # Count domain frequency
                if domain in domain_counts:
                    domain_counts[domain] += 1
                    if url not in website_details[domain]['urls']:
                        website_details[domain]['urls'].append(url)
                    if video['id'] not in website_details[domain]['videos']:
                        website_details[domain]['videos'].append(video['id'])
                        website_details[domain]['video_titles'].append(video.get('title', 'Unknown'))
                else:
                    domain_counts[domain] = 1
                    website_details[domain] = {
                        'domain': domain,
                        'urls': [url],
                        'videos': [video['id']],
                        'video_titles': [video.get('title', 'Unknown')]
                    }
            except:
                # Skip invalid URLs
                continue
    
    # Convert to DataFrame for easier visualization
    website_data = pd.DataFrame([
        {"domain": domain, "count": count, "details": website_details[domain]}
        for domain, count in sorted(domain_counts.items(), key=lambda x: x[1], reverse=True)
    ])
    
    return website_data

def get_videos_by_platform(platform_name):
    """Get videos that mention a specific platform."""
    videos = load_videos()
    return [v for v in videos if platform_name in v.get('platforms', [])]

def start_scan(keywords, days_back, max_videos):
    """Start scanning for videos with the given keywords."""
    
    # Create progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Initialize scrapers
    youtube_scraper = YouTubeScraper()
    text_processor = TextProcessor()
    
    # Load existing videos
    existing_videos = load_videos()
    existing_ids = {v['id'] for v in existing_videos}
    
    # Track new videos
    new_videos = []
    keywords_list = [k.strip() for k in keywords.split(',')]
    
    # Track seen titles for grouping similar videos
    seen_titles = {}
    
    # Scan for each keyword
    for i, keyword in enumerate(keywords_list):
        status_text.text(f"[*] Searching for videos related to '{keyword}'...")
        progress = (i / len(keywords_list)) * 0.5
        progress_bar.progress(progress)
        
        # Search for videos
        videos = youtube_scraper.search_videos(keyword, days_back, max_videos // len(keywords_list))
        
        # Process each video
        for j, video in enumerate(videos):
            video_id = video['id']
            video_title = video['title'].lower()
            
            # Skip if we already have this video
            if video_id in existing_ids:
                continue
                
            # Check for similar titles - if we have a similar title, skip this video
            # We use a simplified approach: normalize the title and check if we've seen a similar one
            normalized_title = re.sub(r'[^\w\s]', '', video_title).strip()
            
            # Skip if we've seen a very similar title (> 80% similarity)
            skip_video = False
            for seen_title, seen_id in seen_titles.items():
                if seen_title == normalized_title or (
                    len(seen_title) > 10 and (
                        seen_title in normalized_title or 
                        normalized_title in seen_title or
                        (len(set(normalized_title.split()) & set(seen_title.split())) / 
                        max(len(set(normalized_title.split())), len(set(seen_title.split())))) > 0.8
                    )
                ):
                    skip_video = True
                    print(f"[!] Skipping similar video: {video_title} (similar to {seen_title})")
                    break
                    
            if skip_video:
                continue
                
            # Update progress
            sub_progress = progress + (j / len(videos)) * (0.5 / len(keywords_list))
            progress_bar.progress(sub_progress)
            status_text.text(f"[*] Processing video: {video['title']}")
            
            # Get video details
            video_details = youtube_scraper.get_video_details(video_id)
            if 'error' in video_details:
                continue
                
            # Combine basic info with details
            full_video = {**video, 'description': video_details.get('description', '')}
            
            # Process text to extract platforms, links, and messaging groups
            platforms, links, groups = text_processor.process_video(full_video)
            
            # Add extracted data to the video
            full_video['platforms'] = platforms
            full_video['links'] = links
            full_video['messaging_groups'] = groups
            full_video['scan_date'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Add to new videos list
            new_videos.append(full_video)
            existing_ids.add(video_id)
            
            # Remember this title
            seen_titles[normalized_title] = video_id
            
    # Save all videos
    all_videos = existing_videos + new_videos
    save_videos(all_videos)
    
    # Complete progress
    progress_bar.progress(1.0)
    status_text.text(f"[+] Scan complete! Found {len(new_videos)} new videos.")
    time.sleep(1)
    
    # Return success message
    return f"Scan completed successfully. Found {len(new_videos)} new videos."

def main():
    # Header
    header()
    
    # Sidebar
    with st.sidebar:
        terminal_container("TARGET CONFIGURATION", "")
        st.write("Configure your scan parameters below:")
        
        keywords = st.text_input(
            "Keywords:", 
            value="plataforma de investimento, pagamento instantâneo, prova de pagamento, multinível", 
            help="Enter comma-separated keywords to search for"
        )
        
        days_back = st.slider(
            "Days to look back:", 
            min_value=1, 
            max_value=30, 
            value=7,
            help="How many days to look back for videos"
        )
        
        max_videos = st.slider(
            "Max videos per keyword:", 
            min_value=5, 
            max_value=50,
            value=10,
            help="Maximum number of videos to scan per keyword"
        )
        
        # Scan options
        terminal_container("SCAN OPTIONS", "")
        
        col1, col2 = st.columns(2)
        with col1:
            youtube = st.checkbox("YouTube", value=True)
        with col2:
            facebook = st.checkbox("Facebook", value=False)
            
        col1, col2 = st.columns(2)
        with col1:
            tiktok = st.checkbox("TikTok", value=False)
        with col2:
            instagram = st.checkbox("Instagram", value=False)
        
        # Execute scan button
        st.markdown("")
        if st.button("▶ EXECUTE SCAN", use_container_width=True):
            if any([youtube, facebook, tiktok, instagram]):
                # Show a terminal animation
                console_content = st.empty()
                for i in range(5):
                    console_content.markdown(f"""
                    <div class="console-log">
                    root@scanner:~# ./security_scanner.sh --target "{keywords}" --days {days_back} --max {max_videos}
                    {'.' * (i+1)}
                    </div>
                    """, unsafe_allow_html=True)
                    time.sleep(0.5)
                
                # Start the scan
                result = start_scan(keywords, days_back, max_videos)
                console_content.markdown(f"""
                <div class="console-log">
                root@scanner:~# ./security_scanner.sh --target "{keywords}" --days {days_back} --max {max_videos}
                {result}
                </div>
                """, unsafe_allow_html=True)
            else:
                warning("Please select at least one platform to scan.")
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Statistics dashboard
        terminal_container("SCAN STATISTICS", "")
        
        # Load data
        videos = load_videos()
        platform_data = get_platform_statistics()
        messaging_groups = get_messaging_group_statistics()
        
        if videos:
            # Key metrics
            met1, met2, met3 = st.columns(3)
            with met1:
                st.metric("Total Videos", len(videos))
            with met2:
                platform_count = len(set(p for v in videos for p in v.get('platforms', [])))
                st.metric("Unique Platforms", platform_count)
            with met3:
                group_count = len(messaging_groups)
                st.metric("Messaging Groups", group_count)
                
            # Timeline visualization
            if len(videos) >= 3:
                dates = [datetime.datetime.strptime(v.get('scan_date', '2023-01-01 00:00:00'), "%Y-%m-%d %H:%M:%S").date() for v in videos]
                date_counts = {}
                for date in dates:
                    if date in date_counts:
                        date_counts[date] += 1
                    else:
                        date_counts[date] = 1
                
                date_df = pd.DataFrame([
                    {"date": date, "count": count}
                    for date, count in sorted(date_counts.items())
                ])
                
                fig = px.line(
                    date_df, 
                    x='date', 
                    y='count',
                    title="Videos Tracked Over Time",
                    labels={"date": "Date", "count": "Number of Videos"}
                )
                
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='#00ff00',
                    xaxis=dict(showgrid=False),
                    yaxis=dict(showgrid=False),
                    margin=dict(l=0, r=0, t=30, b=0)
                )
                
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available. Start a scan to collect statistics.")
    
    with col2:
        # Terminal output
        terminal_container("SECURITY TERMINAL", "")
        if videos:
            console_print(f"""
            $ ./status_check.sh
            [+] System initialized
            [+] Database connected
            [+] {len(videos)} videos in database
            [+] {len(set(p for v in videos for p in v.get('platforms', [])))} unique platforms detected
            [+] {len(messaging_groups)} messaging groups found
            [+] Scan engine ready
            """)
        else:
            console_print("""
            $ ./status_check.sh
            [+] System initialized
            [+] Database connected
            [!] No data available
            [+] Scan engine ready
            """)
    
    # Create tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["Videos", "Platforms", "Messaging Groups", "Websites"])
    
    with tab1:
        # Videos tab
        terminal_container("VIDEO ANALYSIS", "")
        if videos:
            # Show videos in a table
            video_df = pd.DataFrame([
                {
                    "Title": v.get('title', 'Unknown'),
                    "Channel": v.get('channel_name', 'Unknown'),
                    "Published": v.get('publish_date', 'Unknown'),
                    "Platforms": ", ".join(v.get('platforms', [])),
                    "Groups": len(v.get('messaging_groups', [])),
                    "Links": len(v.get('links', [])),
                    "ID": v.get('id', '')
                }
                for v in videos
            ])
            
            st.dataframe(video_df, use_container_width=True)
            
            # Video details
            st.markdown("### Video Details")
            
            # Select a video to view details
            selected_video_id = st.selectbox("Select a video to view details:", 
                                            options=[v.get('id', '') for v in videos],
                                            format_func=lambda x: next((v.get('title', 'Unknown') for v in videos if v.get('id', '') == x), 'Unknown'))
            
            if selected_video_id:
                # Find the selected video
                selected_video = next((v for v in videos if v.get('id', '') == selected_video_id), None)
                
                if selected_video:
                    # Display video details in a terminal-like container
                    content = f"""
                    <span style="color: #4cd964;">Title:</span> {selected_video.get('title', 'Unknown')}
                    <span style="color: #4cd964;">Channel:</span> {selected_video.get('channel_name', 'Unknown')}
                    <span style="color: #4cd964;">Published:</span> {selected_video.get('publish_date', 'Unknown')}
                    <span style="color: #4cd964;">Views:</span> {selected_video.get('view_count', 'Unknown')}
                    <span style="color: #4cd964;">URL:</span> https://youtube.com/watch?v={selected_video.get('id', '')}
                    
                    <span style="color: #4cd964;">Detected Platforms:</span>
                    {", ".join(selected_video.get('platforms', ['None detected']))}
                    
                    <span style="color: #4cd964;">Links Found:</span>
                    {", ".join(selected_video.get('links', ['None detected']))}
                    
                    <span style="color: #4cd964;">Messaging Groups:</span>
                    {", ".join([f"{g.get('platform', 'Unknown')}: {g.get('name', 'Unknown')}" for g in selected_video.get('messaging_groups', []) if 'platform' in g]) or 'None detected'}
                    """
                    
                    terminal_container(f"VIDEO: {selected_video.get('id', '')}", content)
        else:
            st.info("No videos have been scanned yet. Start a scan to track investment videos.")
    
    with tab2:
        # Platforms tab
        terminal_container("PLATFORM ANALYSIS", "")
        
        if not platform_data.empty if isinstance(platform_data, pd.DataFrame) else False:
            # Platform bar chart
            fig = px.bar(
                platform_data,
                x='count',
                y='platform',
                orientation='h',
                title="Detected Investment Platforms",
                color='count',
                color_continuous_scale=['#00ff00', '#ffff00', '#ff0000']
            )
            
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#00ff00',
                xaxis=dict(title="Mentions", showgrid=False),
                yaxis=dict(title="", showgrid=False),
                margin=dict(l=0, r=0, t=30, b=0)
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Platform details
            for idx, row in platform_data.iterrows():
                platform = row['platform']
                count = row['count']
                with st.expander(f"{platform} ({count} mentions)"):
                    platform_videos = get_videos_by_platform(platform)
                    for video in platform_videos:
                        st.markdown(f"- [{video.get('title', 'Unknown')}](https://youtube.com/watch?v={video.get('id', '')})")
        else:
            st.info("No platform data available. Start a scan to track investment platforms.")
    
    with tab3:
        # Messaging groups tab
        terminal_container("MESSAGING GROUP ANALYSIS", "")
        
        if isinstance(messaging_groups, list) and len(messaging_groups) > 0:
            # Count by platform
            platform_counts = {}
            for group in messaging_groups:
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
                color_discrete_sequence=['#00ff00', '#ff0000', '#0000ff', '#ffff00']
            )
            
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#00ff00',
                margin=dict(l=0, r=0, t=30, b=0)
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # List all groups
            st.markdown("### Detected Groups")
            
            # Group by platform
            whatsapp_groups = [g for g in messaging_groups if g.get('platform') == 'WhatsApp']
            telegram_groups = [g for g in messaging_groups if g.get('platform') == 'Telegram']
            
            if whatsapp_groups:
                with st.expander(f"WhatsApp Groups ({len(whatsapp_groups)})", expanded=True):
                    for group in whatsapp_groups:
                        st.markdown(f"- {group.get('name', 'Unknown Group')}: [{group.get('link', '#')}]({group.get('link', '#')})")
            
            if telegram_groups:
                with st.expander(f"Telegram Groups ({len(telegram_groups)})", expanded=True):
                    for group in telegram_groups:
                        st.markdown(f"- {group.get('name', 'Unknown Group')}: [{group.get('link', '#')}]({group.get('link', '#')})")
        else:
            st.info("No messaging groups detected yet. Start a scan to find investment-related groups.")
    
    with tab4:
        # Websites tab
        terminal_container("WEBSITE ANALYSIS", "")
        
        # Add option to analyze specific website
        with st.expander("Analyze specific website", expanded=False):
            website_url = st.text_input("Enter website URL to analyze:", 
                                         placeholder="https://example.com")
            analyze_col1, analyze_col2 = st.columns([1, 3])
            with analyze_col1:
                if st.button("Analyze Website", use_container_width=True):
                    if website_url:
                        with analyze_col2:
                            with st.spinner(f"Analyzing {website_url}..."):
                                # Initialize web scraper
                                web_scraper = WebScraper()
                                
                                # Extract content
                                title, content = web_scraper.get_website_text_content(website_url)
                                
                                if title and content:
                                    st.success(f"Successfully analyzed: {title}")
                                    
                                    # Show content in terminal-like container
                                    terminal_container(
                                        f"CONTENT: {title}", 
                                        content[:2000] + ("..." if len(content) > 2000 else "")
                                    )
                                    
                                    # Process text to find potential platforms and messaging groups
                                    text_processor = TextProcessor()
                                    platforms = text_processor.extract_platforms(content)
                                    links = text_processor.extract_links(content)
                                    groups = text_processor.extract_messaging_groups(content)
                                    
                                    # Display findings
                                    if platforms:
                                        st.markdown("#### Detected Platforms:")
                                        st.write(", ".join(platforms))
                                    
                                    if groups:
                                        st.markdown("#### Detected Messaging Groups:")
                                        for group in groups:
                                            st.markdown(f"- {group.get('platform')}: {group.get('link')}")
                                else:
                                    st.error(f"Failed to extract content from {website_url}")
                    else:
                        st.warning("Please enter a valid URL")
        
        # Get website statistics
        website_data = get_website_statistics()
        
        if not website_data.empty if isinstance(website_data, pd.DataFrame) else False:
            # Website domain count chart
            if len(website_data) > 0:
                # Limit to top 15 domains for readability
                top_domains = website_data.head(15)
                
                fig = px.bar(
                    top_domains,
                    x='count',
                    y='domain',
                    orientation='h',
                    title="Most Referenced Websites",
                    color='count',
                    color_continuous_scale=['#00ff00', '#ffff00', '#ff0000']
                )
                
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='#00ff00',
                    xaxis=dict(title="Mentions", showgrid=False),
                    yaxis=dict(title="", showgrid=False),
                    margin=dict(l=0, r=0, t=30, b=0)
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Domain details in expandable sections
                st.markdown("### Website Details")
                
                for idx, row in website_data.iterrows():
                    domain = row['domain']
                    count = row['count']
                    details = row['details']
                    
                    with st.expander(f"{domain} ({count} mentions)"):
                        # Show unique URLs for this domain
                        st.markdown("#### URLs:")
                        for url in details['urls']:
                            st.markdown(f"- [{url}]({url})")
                        
                        # Show videos that mentioned this domain
                        st.markdown("#### Mentioned in videos:")
                        for vid_id, vid_title in zip(details['videos'], details['video_titles']):
                            st.markdown(f"- [{vid_title}](https://youtube.com/watch?v={vid_id})")
            else:
                st.info("No website data to display.")
        else:
            st.info("No website data available. Start a scan to track websites mentioned in videos.")

if __name__ == "__main__":
    main()