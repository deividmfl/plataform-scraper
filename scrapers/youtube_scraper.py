import re
import time
import random
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import trafilatura

def setup_selenium():
    """Set up Selenium WebDriver with appropriate options."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def search_youtube_videos(keyword, from_date):
    """
    Search YouTube for videos matching the keyword and published after from_date.
    
    Args:
        keyword (str): Search keyword.
        from_date (str): Date string in YYYY-MM-DD format.
        
    Returns:
        list: List of dictionaries containing video information.
    """
    print(f"Searching YouTube for: {keyword} (from {from_date})")
    videos = []
    
    try:
        # Create encoded search URL with date filter
        encoded_keyword = keyword.replace(' ', '+')
        search_url = f"https://www.youtube.com/results?search_query={encoded_keyword}&sp=CAISBAgBEAE%253D"  # Recent uploads filter
        
        # Initialize Selenium
        driver = setup_selenium()
        driver.get(search_url)
        
        # Wait for search results to load
        time.sleep(3)
        
        # Scroll to load more videos (adjust number of scrolls as needed)
        for _ in range(5):
            driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
            time.sleep(1)
        
        # Get page source and parse with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Find video elements
        video_elements = soup.find_all('div', {'id': 'dismissible'})
        
        for element in video_elements[:20]:  # Limit to first 20 results
            try:
                # Extract video ID
                video_link_element = element.find('a', {'id': 'thumbnail'})
                if not video_link_element:
                    continue
                
                video_url = video_link_element.get('href', '')
                if not video_url or '/watch?v=' not in video_url:
                    continue
                
                video_id = video_url.split('/watch?v=')[1].split('&')[0]
                
                # Extract title
                title_element = element.find('h3')
                if not title_element:
                    continue
                title = title_element.text.strip()
                
                # Extract channel name
                channel_element = element.find('a', {'class': 'yt-simple-endpoint style-scope yt-formatted-string'})
                channel = channel_element.text.strip() if channel_element else "Unknown Channel"
                
                # Extract publish date (might be relative like "2 weeks ago")
                date_element = element.find('span', {'class': 'style-scope ytd-video-meta-block'})
                publish_date = date_element.text.strip() if date_element else "Unknown date"
                
                # Check if video is recent enough (this is approximate since YouTube shows relative dates)
                if "year" in publish_date or "month" in publish_date and int(publish_date.split()[0]) > 1:
                    continue  # Skip if older than a month
                
                # Get video page to extract description and more data
                video_full_url = f"https://www.youtube.com/watch?v={video_id}"
                driver.get(video_full_url)
                time.sleep(3)  # Wait for page to load
                
                # Extract description
                try:
                    show_more_button = WebDriverWait(driver, 3).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "tp-yt-paper-button#expand"))
                    )
                    show_more_button.click()
                    time.sleep(1)
                except Exception:
                    pass  # Description might already be expanded or not available
                
                description_element = driver.find_element(By.CSS_SELECTOR, "div#description-inner")
                description = description_element.text if description_element else ""
                
                # Extract view count and like count if available
                view_count_element = driver.find_element(By.CSS_SELECTOR, "span.view-count")
                view_count = view_count_element.text.split()[0] if view_count_element else "0"
                
                like_count_element = driver.find_element(By.XPATH, "//yt-formatted-string[@id='text' and contains(@class, 'ytd-toggle-button-renderer')]")
                like_count = like_count_element.text if like_count_element else "0"
                
                # Clean up the count values
                view_count = ''.join(filter(str.isdigit, view_count))
                like_count = ''.join(filter(str.isdigit, like_count))
                
                # Create video data object
                video_data = {
                    'id': video_id,
                    'platform': 'YouTube',
                    'title': title,
                    'channel': channel,
                    'publish_date': publish_date,
                    'url': video_full_url,
                    'description': description,
                    'view_count': int(view_count) if view_count.isdigit() else 0,
                    'like_count': int(like_count) if like_count.isdigit() else 0,
                    'search_keyword': keyword
                }
                
                videos.append(video_data)
                
                # Add a small random delay between processing videos to avoid rate limiting
                time.sleep(random.uniform(0.5, 1.5))
                
            except Exception as e:
                print(f"Error processing video element: {str(e)}")
                continue
        
        driver.quit()
        
    except Exception as e:
        print(f"Error in YouTube search: {str(e)}")
    
    return videos

def get_video_comments(video_id, max_comments=50):
    """Get comments for a YouTube video."""
    try:
        # Initialize Selenium
        driver = setup_selenium()
        driver.get(f"https://www.youtube.com/watch?v={video_id}")
        
        # Wait for page and scroll to comments
        time.sleep(3)
        driver.execute_script("window.scrollTo(0, window.innerHeight * 2);")
        time.sleep(2)
        
        # Scroll a few times to load more comments
        for _ in range(3):
            driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
            time.sleep(1)
        
        # Parse comments with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        comment_elements = soup.find_all('ytd-comment-renderer', limit=max_comments)
        
        comments = []
        for element in comment_elements:
            try:
                author_element = element.find('a', {'id': 'author-text'})
                content_element = element.find('yt-formatted-string', {'id': 'content-text'})
                
                if author_element and content_element:
                    comment = {
                        'author': author_element.text.strip(),
                        'text': content_element.text.strip()
                    }
                    comments.append(comment)
            except Exception:
                continue
        
        driver.quit()
        return comments
    
    except Exception as e:
        print(f"Error getting comments: {str(e)}")
        return []
