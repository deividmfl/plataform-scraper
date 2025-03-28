import time
import json
import re
import os
import datetime
from typing import List, Dict, Any, Optional
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup

class YouTubeScraper:
    """
    Scraper for YouTube videos with investment-related keywords
    """
    
    def __init__(self):
        """Initialize the YouTube scraper"""
        self.driver = None
        self.initialize_driver()
    
    def initialize_driver(self):
        """Set up the Selenium WebDriver"""
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--disable-notifications')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-infobars')
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36')
        
        self.driver = webdriver.Chrome(options=options)
    
    def __del__(self):
        """Clean up the driver when the object is destroyed"""
        if self.driver:
            self.driver.quit()
    
    def search_videos(self, keyword: str, days_back: int = 7, max_videos: int = 50) -> List[Dict[str, Any]]:
        """
        Search for YouTube videos with the given keyword
        
        Args:
            keyword: The search keyword
            days_back: How many days to look back
            max_videos: Maximum number of videos to retrieve
            
        Returns:
            List of dictionaries containing video information
        """
        # Calculate the date for filtering
        date_filter = (datetime.datetime.now() - datetime.timedelta(days=days_back)).strftime("%Y-%m-%d")
        
        # Construct search URL with date filter
        search_url = f"https://www.youtube.com/results?search_query={keyword.replace(' ', '+')}&sp=CAI%253D" # Sort by upload date
        
        try:
            self.driver.get(search_url)
            time.sleep(3)  # Wait for page to load
            
            # Scroll to load more videos
            videos_found = 0
            max_scrolls = 10  # Limit scrolling to prevent infinite loops
            
            for _ in range(max_scrolls):
                if videos_found >= max_videos:
                    break
                
                # Scroll down
                self.driver.execute_script("window.scrollBy(0, 1000);")
                time.sleep(2)
                
                # Get current video count
                video_elements = self.driver.find_elements(By.CSS_SELECTOR, "ytd-video-renderer")
                videos_found = len(video_elements)
            
            # Extract video information
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            videos = []
            video_elements = soup.select("ytd-video-renderer")
            
            for element in video_elements[:max_videos]:
                try:
                    # Extract video ID
                    video_url = element.select_one("a#thumbnail")["href"]
                    video_id = video_url.split("v=")[1].split("&")[0] if "v=" in video_url else video_url.split("/")[-1]
                    
                    # Extract title
                    title_element = element.select_one("#video-title")
                    title = title_element.text.strip() if title_element else "Unknown Title"
                    
                    # Extract channel name
                    channel_element = element.select_one("#channel-name a")
                    channel_name = channel_element.text.strip() if channel_element else "Unknown Channel"
                    
                    # Extract publish date
                    date_element = element.select_one("#metadata-line span:nth-child(2)")
                    publish_date = date_element.text.strip() if date_element else "Unknown Date"
                    
                    # Extract view count
                    view_element = element.select_one("#metadata-line span:nth-child(1)")
                    view_count = view_element.text.strip() if view_element else "Unknown Views"
                    
                    # Extract thumbnail
                    thumbnail_element = element.select_one("a#thumbnail img")
                    thumbnail = thumbnail_element["src"] if thumbnail_element and "src" in thumbnail_element.attrs else ""
                    
                    videos.append({
                        "id": video_id,
                        "title": title,
                        "channel_name": channel_name,
                        "publish_date": publish_date,
                        "view_count": view_count,
                        "thumbnail": thumbnail
                    })
                    
                except Exception as e:
                    print(f"Error extracting video info: {str(e)}")
                    continue
            
            return videos
        
        except Exception as e:
            print(f"Error searching YouTube: {str(e)}")
            return []
    
    def get_video_details(self, video_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific video
        
        Args:
            video_id: The YouTube video ID
            
        Returns:
            Dictionary with video details
        """
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        
        try:
            self.driver.get(video_url)
            time.sleep(3)  # Wait for video page to load
            
            # Click "Show more" button to expand description if available
            try:
                show_more_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "tp-yt-paper-button#expand"))
                )
                show_more_button.click()
                time.sleep(1)
            except:
                pass  # Description might already be expanded or button not available
            
            # Extract video information
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Get description
            description_element = soup.select_one("#description-inline-expander")
            description = description_element.text.strip() if description_element else ""
            
            # Get additional details
            title_element = soup.select_one("h1.title")
            title = title_element.text.strip() if title_element else "Unknown Title"
            
            like_element = soup.select_one("ytd-toggle-button-renderer #text")
            likes = like_element.text.strip() if like_element else "Unknown Likes"
            
            # Get comments if available
            comments = []
            comment_elements = soup.select("ytd-comment-thread-renderer")
            
            for comment_element in comment_elements[:10]:  # Limit to first 10 comments
                try:
                    author_element = comment_element.select_one("#author-text")
                    author = author_element.text.strip() if author_element else "Unknown Author"
                    
                    text_element = comment_element.select_one("#content-text")
                    text = text_element.text.strip() if text_element else ""
                    
                    comments.append({
                        "author": author,
                        "text": text
                    })
                except:
                    continue
            
            return {
                "id": video_id,
                "title": title,
                "description": description,
                "likes": likes,
                "comments": comments
            }
        
        except Exception as e:
            print(f"Error getting video details: {str(e)}")
            return {"id": video_id, "error": str(e)}
