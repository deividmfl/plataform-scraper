import json
import os
from datetime import datetime

# File path for video storage
DATA_DIRECTORY = "data"
VIDEOS_FILE = os.path.join(DATA_DIRECTORY, "videos.json")

def ensure_data_directory():
    """Ensure the data directory exists."""
    if not os.path.exists(DATA_DIRECTORY):
        os.makedirs(DATA_DIRECTORY)

def load_videos():
    """Load videos from JSON file."""
    ensure_data_directory()
    
    if not os.path.exists(VIDEOS_FILE):
        return []
    
    try:
        with open(VIDEOS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading videos: {str(e)}")
        return []

def save_videos(videos):
    """Save videos to JSON file."""
    ensure_data_directory()
    
    try:
        with open(VIDEOS_FILE, 'w', encoding='utf-8') as f:
            json.dump(videos, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Error saving videos: {str(e)}")
        return False

def get_video_stats():
    """Get statistics about the videos in the database."""
    videos = load_videos()
    
    if not videos:
        return {
            "total": 0,
            "youtube": 0,
            "platforms_mentioned": 0,
            "links_found": 0,
            "groups_found": 0,
            "recent_videos": 0
        }
    
    # Count videos by platform
    platform_counts = {}
    for video in videos:
        platform = video.get('platform', 'unknown')
        platform_counts[platform] = platform_counts.get(platform, 0) + 1
    
    # Count videos with platforms, links, and groups
    platforms_mentioned = sum(1 for v in videos if v.get('platforms') and len(v['platforms']) > 0)
    links_found = sum(1 for v in videos if v.get('links') and len(v['links']) > 0)
    
    groups_found = sum(1 for v in videos if 
                       (v.get('groups', {}).get('whatsapp') and len(v['groups']['whatsapp']) > 0) or
                       (v.get('groups', {}).get('telegram') and len(v['groups']['telegram']) > 0))
    
    # Count recent videos (last 7 days)
    seven_days_ago = (datetime.now() - datetime.timedelta(days=7)).strftime('%Y-%m-%d')
    recent_videos = sum(1 for v in videos if 
                        'scan_date' in v and 
                        v['scan_date'] >= seven_days_ago)
    
    return {
        "total": len(videos),
        "youtube": platform_counts.get('YouTube', 0),
        "platforms_mentioned": platforms_mentioned,
        "links_found": links_found,
        "groups_found": groups_found,
        "recent_videos": recent_videos
    }

def get_top_platforms(limit=10):
    """Get the most mentioned platform names."""
    videos = load_videos()
    platform_counts = {}
    
    for video in videos:
        if not video.get('platforms'):
            continue
        
        for platform in video['platforms']:
            platform_counts[platform] = platform_counts.get(platform, 0) + 1
    
    # Sort by count (descending) and take top N
    top_platforms = sorted(platform_counts.items(), key=lambda x: x[1], reverse=True)[:limit]
    return top_platforms

def get_top_domains(limit=10):
    """Get the most mentioned website domains."""
    videos = load_videos()
    domain_counts = {}
    
    for video in videos:
        if not video.get('links'):
            continue
        
        for link in video['links']:
            domain = link.get('domain', '')
            if domain:
                domain_counts[domain] = domain_counts.get(domain, 0) + 1
    
    # Sort by count (descending) and take top N
    top_domains = sorted(domain_counts.items(), key=lambda x: x[1], reverse=True)[:limit]
    return top_domains
