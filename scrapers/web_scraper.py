import trafilatura
import requests
from typing import Dict, Optional, Tuple

class WebScraper:
    """
    Simple web scraper for extracting content from websites
    """
    
    def __init__(self):
        """Initialize the web scraper"""
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
    
    def get_website_text_content(self, url: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Extract the main text content from a website
        
        Args:
            url: URL of the website to scrape
            
        Returns:
            Tuple of (title, text content)
        """
        try:
            # Send a request to the website
            downloaded = trafilatura.fetch_url(url)
            
            if not downloaded:
                return None, None
                
            # Extract the main content
            text = trafilatura.extract(downloaded)
            
            # Extract metadata
            metadata = trafilatura.extract_metadata(downloaded)
            title = metadata.title if metadata else None
            
            return title, text
        except Exception as e:
            print(f"[!] Error extracting content from {url}: {str(e)}")
            return None, None
    
    def get_website_metadata(self, url: str) -> Dict:
        """
        Extract metadata from a website
        
        Args:
            url: URL of the website to scrape
            
        Returns:
            Dictionary of metadata
        """
        try:
            # Send a request to the website
            downloaded = trafilatura.fetch_url(url)
            
            if not downloaded:
                return {}
                
            # Extract metadata
            metadata = trafilatura.extract_metadata(downloaded)
            
            if not metadata:
                return {}
                
            # Convert to dictionary
            return {
                "title": metadata.title,
                "author": metadata.author,
                "date": metadata.date,
                "description": metadata.description,
                "categories": metadata.categories,
                "tags": metadata.tags,
                "sitename": metadata.sitename
            }
        except Exception as e:
            print(f"[!] Error extracting metadata from {url}: {str(e)}")
            return {}