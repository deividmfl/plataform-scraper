import time
import json
import re
import os
import datetime
import random
import requests
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
import trafilatura
from urllib.parse import quote, urlparse


class YouTubeScraper:
    """
    Scraper for YouTube videos with investment-related keywords
    """
    
    def __init__(self):
        """Initialize the YouTube scraper"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"'
        })
        print("[+] YouTube scraper initialized")
    
    def search_videos(self, keyword: str, days_back: int = 7, max_videos: int = 10) -> List[Dict[str, Any]]:
        """
        Search for YouTube videos with the given keyword
        
        Args:
            keyword: The search keyword
            days_back: How many days to look back
            max_videos: Maximum number of videos to retrieve
            
        Returns:
            List of dictionaries containing video information
        """
        print(f"[*] Searching YouTube for '{keyword}', looking back {days_back} days")
        
        # Properly encode the keyword for URL
        encoded_keyword = quote(keyword)
        
        # Build YouTube search URL (sorted by upload date)
        search_url = f"https://www.youtube.com/results?search_query={encoded_keyword}&sp=CAI%253D"
        
        try:
            # Make the request
            response = self.session.get(search_url, timeout=10)
            
            if response.status_code != 200:
                print(f"[!] Failed to get search results. Status code: {response.status_code}")
                return []
            
            # Parse the response
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # YouTube uses JavaScript to load content, so we need to extract the JSON data
            # that's embedded in the initial page
            pattern = r'var ytInitialData = (.+?);</script>'
            matches = re.search(pattern, response.text)
            
            videos = []
            
            if not matches:
                # Try alternative method using trafilatura and regex
                videos = self._extract_videos_from_html(response.text, max_videos)
                if videos:
                    return videos
                
                print("[!] Could not extract video data from YouTube's initial data")
                return []
            
            # Parse the JSON data
            try:
                data = json.loads(matches.group(1))
                
                # Navigate through the complex JSON structure to find video results
                contents = data.get('contents', {}).get('twoColumnSearchResultsRenderer', {}).get('primaryContents', {})
                section_list = contents.get('sectionListRenderer', {}).get('contents', [])
                
                for section in section_list:
                    if 'itemSectionRenderer' in section:
                        items = section.get('itemSectionRenderer', {}).get('contents', [])
                        for item in items:
                            if 'videoRenderer' in item:
                                video_data = item.get('videoRenderer', {})
                                video_id = video_data.get('videoId', '')
                                
                                # Extract the title
                                title = "Unknown Title"
                                title_runs = video_data.get('title', {}).get('runs', [])
                                if title_runs:
                                    title = ''.join([run.get('text', '') for run in title_runs])
                                
                                # Extract channel name
                                channel_name = "Unknown Channel"
                                owner_text = video_data.get('ownerText', {}).get('runs', [])
                                if owner_text:
                                    channel_name = owner_text[0].get('text', 'Unknown Channel')
                                
                                # Extract publish time
                                publish_date = "Unknown Date"
                                publish_time = video_data.get('publishedTimeText', {}).get('simpleText', '')
                                if publish_time:
                                    publish_date = publish_time
                                
                                # Extract view count
                                view_count = "Unknown Views"
                                view_count_text = video_data.get('viewCountText', {}).get('simpleText', '')
                                if view_count_text:
                                    view_count = view_count_text
                                
                                # Extract thumbnail
                                thumbnail = ""
                                thumbnails = video_data.get('thumbnail', {}).get('thumbnails', [])
                                if thumbnails:
                                    thumbnail = thumbnails[-1].get('url', '')
                                
                                videos.append({
                                    "id": video_id,
                                    "title": title,
                                    "channel_name": channel_name,
                                    "publish_date": publish_date,
                                    "view_count": view_count,
                                    "thumbnail": thumbnail
                                })
                                
                                if len(videos) >= max_videos:
                                    break
                
                if videos:
                    print(f"[+] Found {len(videos)} videos on YouTube")
                    return videos
                else:
                    # Fallback to alternative method
                    return self._extract_videos_from_html(response.text, max_videos)
            
            except (json.JSONDecodeError, KeyError) as e:
                print(f"[!] Error parsing YouTube data: {str(e)}")
                # Try backup method
                return self._extract_videos_from_html(response.text, max_videos)
                
        except Exception as e:
            print(f"[!] Error searching YouTube: {str(e)}")
            return []
    
    def _extract_videos_from_html(self, html_content, max_videos=10):
        """Backup method to extract videos from HTML using regex patterns"""
        print("[*] Using backup HTML extraction method")
        video_results = []
        
        # Extract video IDs using regex
        video_id_pattern = r'watch\?v=([A-Za-z0-9_-]{11})'
        video_ids = re.findall(video_id_pattern, html_content)
        
        # Remove duplicates while preserving order
        unique_ids = []
        for video_id in video_ids:
            if video_id not in unique_ids:
                unique_ids.append(video_id)
        
        # Extract title and other info for each video
        for video_id in unique_ids[:max_videos]:
            # Try to find title and other details
            title_pattern = rf'title="(.*?)".*?href="/watch\?v={video_id}'
            title_match = re.search(title_pattern, html_content)
            title = title_match.group(1) if title_match else f"Video {video_id}"
            
            # Add basic info (we'll get complete details when we fetch each video)
            video_results.append({
                "id": video_id,
                "title": title,
                "channel_name": "YouTube Channel",
                "publish_date": "Recent",
                "view_count": "Multiple views",
                "thumbnail": f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"
            })
            
            if len(video_results) >= max_videos:
                break
        
        if video_results:
            print(f"[+] Found {len(video_results)} videos using backup method")
        else:
            print("[!] Could not extract any videos from YouTube")
            
        return video_results
    
    def get_video_details(self, video_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific video
        
        Args:
            video_id: The YouTube video ID
            
        Returns:
            Dictionary with video details
        """
        print(f"[*] Fetching details for YouTube video ID: {video_id}")
        
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        
        try:
            # Get the video page
            response = self.session.get(video_url, timeout=10)
            
            if response.status_code != 200:
                print(f"[!] Failed to get video details. Status code: {response.status_code}")
                return {"id": video_id, "error": f"HTTP Error: {response.status_code}"}
            
            # First, use trafilatura to extract clean text content from the page
            downloaded = response.text
            text_content = trafilatura.extract(downloaded, include_comments=True, include_tables=False)
            
            # Use BeautifulSoup to parse the HTML for more structured extraction
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Try to extract the title
            title = "Unknown Title"
            title_element = soup.select_one('meta[property="og:title"]')
            if title_element and 'content' in title_element.attrs:
                title = title_element['content']
            
            # Try to extract description
            description = ""
            description_element = soup.select_one('meta[property="og:description"]')
            if description_element and 'content' in description_element.attrs:
                description = description_element['content']
            
            # If description is too short, use trafilatura's extracted content
            if len(description) < 100 and text_content:
                description = text_content
            
            # Try to extract like count
            likes = "Unknown Likes"
            like_pattern = r'"likeCount":"([0-9,]+)"'
            like_match = re.search(like_pattern, response.text)
            if like_match:
                likes = like_match.group(1)
            
            # Extract comments (this is challenging without JavaScript)
            comments = []
            comment_pattern = r'"authorDisplayName":"(.*?)","authorProfileImageUrl":".*?","authorEndpoint":.*?"contentText":{"simpleText":"(.*?)"}'
            comment_matches = re.findall(comment_pattern, response.text)
            
            for author, text in comment_matches[:10]:  # Limit to 10 comments
                if author and text:
                    comments.append({
                        "author": author,
                        "text": text.replace('\\n', ' ').replace('\\', '')
                    })
            
            print(f"[+] Successfully extracted details for video: {title}")
            
            return {
                "id": video_id,
                "title": title,
                "description": description,
                "likes": likes,
                "comments": comments
            }
            
        except Exception as e:
            print(f"[!] Error getting video details: {str(e)}")
            return {"id": video_id, "error": str(e)}
            
    def extract_links(self, text: str) -> List[str]:
        """
        Extract URLs from text content
        
        Args:
            text: Text to scan for URLs
            
        Returns:
            List of extracted URLs
        """
        # URL pattern matching
        url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[/\w\.-]*(?:\?[/\w\.-=&]*)?'
        urls = re.findall(url_pattern, text)
        
        # Filter out YouTube URLs
        filtered_urls = []
        for url in urls:
            domain = urlparse(url).netloc
            if "youtube.com" not in domain and "youtu.be" not in domain:
                filtered_urls.append(url)
                
        return filtered_urls

    def extract_whatsapp_links(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract WhatsApp group links
        
        Args:
            text: Text to scan for WhatsApp links
            
        Returns:
            List of dictionaries with platform and link
        """
        whatsapp_pattern = r'https?://(?:chat\.)?whatsapp\.com/(?:invite/)?(?:[-\w]*)'
        links = re.findall(whatsapp_pattern, text)
        
        return [{"platform": "WhatsApp", "name": f"WhatsApp Group {i+1}", "link": link} 
                for i, link in enumerate(links)]
                
    def extract_telegram_links(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract Telegram group/channel links
        
        Args:
            text: Text to scan for Telegram links
            
        Returns:
            List of dictionaries with platform and link
        """
        telegram_pattern = r'https?://(?:t\.me|telegram\.me|telegram\.dog)/(?:joinchat/)?(?:[-\w]*)'
        links = re.findall(telegram_pattern, text)
        
        return [{"platform": "Telegram", "name": f"Telegram Channel {i+1}", "link": link} 
                for i, link in enumerate(links)]