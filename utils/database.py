import os
import json
import datetime
from typing import List, Dict, Any, Optional
import pandas as pd

class Database:
    """
    Simple file-based database for storing scraped video data
    """
    
    def __init__(self, db_file: str = "video_data.json"):
        """
        Initialize the database
        
        Args:
            db_file: Path to the database file
        """
        self.db_file = db_file
        self.data = self._load_data()
    
    def _load_data(self) -> Dict[str, Any]:
        """Load data from the database file"""
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {'videos': [], 'last_update': None}
        else:
            return {'videos': [], 'last_update': None}
    
    def _save_data(self):
        """Save data to the database file"""
        with open(self.db_file, 'w', encoding='utf-8') as f:
            self.data['last_update'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    def save_videos(self, videos: List[Dict[str, Any]]):
        """
        Save videos to the database
        
        Args:
            videos: List of video dictionaries
        """
        # Get existing video IDs
        existing_ids = [v.get('id') for v in self.data['videos']]
        
        # Add only new videos
        new_videos = []
        for video in videos:
            if video.get('id') not in existing_ids:
                video['added_at'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                new_videos.append(video)
            else:
                # Update existing video
                for i, existing_video in enumerate(self.data['videos']):
                    if existing_video.get('id') == video.get('id'):
                        # Update with new data while preserving original added_at
                        video['added_at'] = existing_video.get('added_at')
                        self.data['videos'][i] = video
        
        # Add new videos to the database
        self.data['videos'].extend(new_videos)
        
        # Save the updated database
        self._save_data()
        
        return len(new_videos)
    
    def get_videos(self) -> List[Dict[str, Any]]:
        """
        Get all videos from the database
        
        Returns:
            List of video dictionaries
        """
        return sorted(self.data['videos'], key=lambda v: v.get('added_at', ''), reverse=True)
    
    def get_videos_by_platform(self, platform: str) -> List[Dict[str, Any]]:
        """
        Get videos that mention a specific platform
        
        Args:
            platform: Platform name to filter by
            
        Returns:
            List of video dictionaries
        """
        result = []
        for video in self.data['videos']:
            platforms = video.get('platforms', [])
            if any(p.lower() == platform.lower() for p in platforms):
                result.append(video)
        
        return result
    
    def get_platform_statistics(self) -> pd.DataFrame:
        """
        Get statistics about mentioned platforms
        
        Returns:
            DataFrame with platform counts
        """
        platform_counts = {}
        
        for video in self.data['videos']:
            platforms = video.get('platforms', [])
            for platform in platforms:
                if platform in platform_counts:
                    platform_counts[platform] += 1
                else:
                    platform_counts[platform] = 1
        
        # Convert to DataFrame
        if platform_counts:
            df = pd.DataFrame({'platform': list(platform_counts.keys()), 
                               'count': list(platform_counts.values())})
            df = df.sort_values('count', ascending=False)
            return df
        else:
            return pd.DataFrame()
    
    def get_messaging_group_statistics(self) -> List[Dict[str, Any]]:
        """
        Get statistics about messaging groups
        
        Returns:
            List of messaging group dictionaries
        """
        messaging_groups = []
        
        for video in self.data['videos']:
            groups = video.get('messaging_groups', [])
            for group in groups:
                # Check if the group is already in the list
                if not any(g.get('link') == group.get('link') for g in messaging_groups):
                    group['video_id'] = video.get('id')
                    group['video_title'] = video.get('title')
                    messaging_groups.append(group)
        
        return messaging_groups
