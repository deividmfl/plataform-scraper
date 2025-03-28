import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils.data_storage import get_video_stats, get_top_platforms, get_top_domains

def render_dashboard():
    """Render the main dashboard with statistics and visualizations."""
    st.markdown("""
    <div class="matrix-title">
        <h1>MATRIX <span class="red-text">DASHBOARD</span></h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Display dashboard header images
    col1, col2, col3 = st.columns(3)
    with col1:
        st.image("https://images.unsplash.com/photo-1524114051012-0a2aa8dae4e1", use_column_width=True)
    with col2:
        st.image("https://images.unsplash.com/photo-1606606767399-01e271823a2e", use_column_width=True)
    with col3:
        st.image("https://images.unsplash.com/photo-1551288049-bebda4e38f71", use_column_width=True)
    
    # Get statistics
    stats = get_video_stats()
    
    # Display key metrics in Matrix-style cards
    st.markdown("""
    <div class="matrix-subtitle">
        <h2>SYSTEM <span class="red-text">METRICS</span></h2>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="matrix-card">
            <div class="matrix-card-title">VIDEOS TRACKED</div>
            <div class="matrix-card-value">{stats['total']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="matrix-card">
            <div class="matrix-card-title">PLATFORMS DETECTED</div>
            <div class="matrix-card-value">{stats['platforms_mentioned']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="matrix-card">
            <div class="matrix-card-title">LINKS FOUND</div>
            <div class="matrix-card-value">{stats['links_found']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="matrix-card">
            <div class="matrix-card-title">MESSAGING GROUPS</div>
            <div class="matrix-card-value">{stats['groups_found']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Display charts
    st.markdown("""
    <div class="matrix-subtitle">
        <h2>DATA <span class="red-text">VISUALIZATION</span></h2>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Top platforms bar chart
        top_platforms = get_top_platforms()
        if top_platforms:
            df_platforms = pd.DataFrame(top_platforms, columns=['Platform', 'Count'])
            
            fig = px.bar(
                df_platforms,
                x='Platform',
                y='Count',
                title='Top Investment Platforms Mentioned',
                color='Count',
                color_continuous_scale=['#004d00', '#00ff41']
            )
            
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(10,10,10,0.95)',
                font=dict(family="monospace", color="#00ff41"),
                xaxis=dict(showgrid=False, showline=True, linecolor="#00ff41"),
                yaxis=dict(showgrid=True, gridcolor="rgba(0,255,65,0.2)", showline=True, linecolor="#00ff41"),
                margin=dict(l=10, r=10, t=50, b=30),
                coloraxis_showscale=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No platform data available yet.")
    
    with col2:
        # Top domains bar chart
        top_domains = get_top_domains()
        if top_domains:
            df_domains = pd.DataFrame(top_domains, columns=['Domain', 'Count'])
            
            fig = px.bar(
                df_domains,
                x='Domain',
                y='Count',
                title='Top Website Domains Found',
                color='Count',
                color_continuous_scale=['#4d0000', '#ff0000']
            )
            
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(10,10,10,0.95)',
                font=dict(family="monospace", color="#00ff41"),
                xaxis=dict(showgrid=False, showline=True, linecolor="#00ff41"),
                yaxis=dict(showgrid=True, gridcolor="rgba(0,255,65,0.2)", showline=True, linecolor="#00ff41"),
                margin=dict(l=10, r=10, t=50, b=30),
                coloraxis_showscale=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No domain data available yet.")
    
    # Display recent activity
    st.markdown("""
    <div class="matrix-subtitle">
        <h2>SYSTEM <span class="red-text">ACTIVITY</span></h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Get videos and sort by scan date
    videos = st.session_state.videos
    if videos:
        # Create a dataframe with recent videos (last 10)
        recent_videos = sorted(
            [v for v in videos if 'scan_date' in v],
            key=lambda x: x['scan_date'],
            reverse=True
        )[:10]
        
        if recent_videos:
            df_recent = pd.DataFrame([
                {
                    'Date': v.get('scan_date', ''),
                    'Title': v.get('title', '')[:40] + '...',
                    'Platform': v.get('platform', ''),
                    'Platforms': len(v.get('platforms', [])),
                    'Links': len(v.get('links', [])),
                    'Groups': len(v.get('groups', {}).get('whatsapp', [])) + len(v.get('groups', {}).get('telegram', []))
                }
                for v in recent_videos
            ])
            
            st.dataframe(
                df_recent,
                use_container_width=True,
                height=300
            )
        else:
            st.info("No recent activity available.")
    else:
        st.info("No video data available yet. Run a scan to collect data.")
