import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import List, Dict, Any

def create_platform_chart(platform_data: pd.DataFrame) -> go.Figure:
    """
    Create a bar chart displaying platform mentions
    
    Args:
        platform_data: DataFrame with platform and count columns
        
    Returns:
        Plotly figure object
    """
    if platform_data.empty:
        return None
    
    fig = px.bar(
        platform_data, 
        x='count', 
        y='platform', 
        orientation='h',
        color='count',
        color_continuous_scale=['#00ff00', '#ff0000'],
        title="Investment Platform Mentions"
    )
    
    fig.update_layout(
        plot_bgcolor='black',
        paper_bgcolor='black',
        font_color='#00ff00',
        yaxis_title="",
        xaxis_title="Mention Count"
    )
    
    return fig

def create_messaging_pie_chart(groups_data: List[Dict[str, Any]]) -> go.Figure:
    """
    Create a pie chart showing distribution of messaging app groups
    
    Args:
        groups_data: List of messaging group dictionaries
        
    Returns:
        Plotly figure object
    """
    if not groups_data:
        return None
    
    # Count groups by platform
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
    
    return fig

def create_timeline_chart(videos: List[Dict[str, Any]]) -> go.Figure:
    """
    Create a timeline chart showing videos over time
    
    Args:
        videos: List of video dictionaries
        
    Returns:
        Plotly figure object
    """
    if not videos:
        return None
    
    # Process dates
    dates = []
    counts = []
    date_counts = {}
    
    for video in videos:
        added_at = video.get('added_at', '')
        if added_at:
            date_str = added_at.split(' ')[0]  # Extract just the date part
            if date_str in date_counts:
                date_counts[date_str] += 1
            else:
                date_counts[date_str] = 1
    
    # Sort by date
    for date_str, count in sorted(date_counts.items()):
        dates.append(date_str)
        counts.append(count)
    
    # Create line chart
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=dates,
        y=counts,
        mode='lines+markers',
        name='Videos',
        line=dict(color='#00ff00', width=2),
        marker=dict(color='#00ff00', size=8)
    ))
    
    fig.update_layout(
        title="Videos Detected Over Time",
        xaxis_title="Date",
        yaxis_title="Number of Videos",
        plot_bgcolor='black',
        paper_bgcolor='black',
        font_color='#00ff00',
        xaxis=dict(
            gridcolor='#333333',
            tickfont=dict(color='#00ff00')
        ),
        yaxis=dict(
            gridcolor='#333333',
            tickfont=dict(color='#00ff00')
        )
    )
    
    return fig
