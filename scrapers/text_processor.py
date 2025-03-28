import re
import json
from typing import List, Dict, Any, Tuple
from urllib.parse import urlparse

class TextProcessor:
    """
    Process text from YouTube videos to extract investment platforms, links, and messaging groups
    """
    
    def __init__(self):
        """Initialize the text processor with common investment platform keywords"""
        # Common platform name keywords in Portuguese
        self.platform_keywords = [
            'plataforma', 'investimento', 'trading', 'broker', 'forex', 'opções binárias',
            'binário', 'criptomoeda', 'bitcoin', 'btc', 'bet', 'apostas', 'cassino',
            'dinheiro', 'renda extra', 'ganhar', 'lucro', 'roi', 'retorno',
            'day trade', 'trade', 'trader', 'pagamento', 'pix', 'depósito',
            'saque', 'bônus', 'multinível', 'pirâmide'
        ]
        
        # Common platform name prefixes/suffixes
        self.name_patterns = [
            r'\b[A-Z][a-z]*(?:Bet|Trade|Invest|Forex|Crypto|Pay|Cash|Earn|Money|FX|BTC)\b',
            r'\b(?:Bet|Trade|Invest|Forex|Crypto|Pay|Cash|Earn|Money|FX|BTC)[A-Z][a-z]*\b',
            r'\b[A-Z][a-z]*(?:Trader|Broker|Market|Exchange|Capital|Partners|Group|Bank)\b',
            r'\b[A-Z][a-zA-Z0-9]*(?:\.io|\.com|\.net|\.app)\b'
        ]
        
        print("[+] Text processor initialized")
    
    def extract_platforms(self, text: str) -> List[str]:
        """
        Extract potential investment platform names from text
        
        Args:
            text: The text to analyze
            
        Returns:
            List of detected platform names
        """
        if not text:
            return []
        
        # Lowercase for case-insensitive searching
        text_lower = text.lower()
        
        # Dictionary to store platform candidates with their scores
        platform_candidates = {}
        
        # Look for phrases like "a plataforma XYZ" or "plataforma de investimento XYZ"
        platform_phrases = re.findall(r'(?:a\s+)?plataforma\s+(?:de\s+investimento\s+)?([A-Za-z0-9]+[A-Za-z0-9\s]*)', text, re.IGNORECASE)
        for phrase in platform_phrases:
            name = phrase.strip()
            if name and len(name) > 2:
                # Higher score for explicit platform mentions
                platform_candidates[name] = platform_candidates.get(name, 0) + 5
        
        # Look for words that match the name patterns (like FxTrade, CryptoBTC, etc.)
        for pattern in self.name_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if match and len(match) > 2:
                    platform_candidates[match] = platform_candidates.get(match, 0) + 3
        
        # Look for capitalized words near keywords
        for keyword in self.platform_keywords:
            if keyword in text_lower:
                # Find the position of the keyword
                positions = [m.start() for m in re.finditer(re.escape(keyword), text_lower)]
                
                for pos in positions:
                    # Get a window of text around the keyword
                    start = max(0, pos - 50)
                    end = min(len(text), pos + 50 + len(keyword))
                    window = text[start:end]
                    
                    # Look for capitalized words in this window
                    cap_words = re.findall(r'\b[A-Z][a-zA-Z0-9]{2,15}\b', window)
                    for word in cap_words:
                        if word and word.lower() not in ['o', 'os', 'a', 'as', 'de', 'da', 'do', 'das', 'dos']:
                            platform_candidates[word] = platform_candidates.get(word, 0) + 2
        
        # Sort candidates by score and filter out low-scoring ones
        sorted_candidates = sorted(platform_candidates.items(), key=lambda x: x[1], reverse=True)
        platforms = [name for name, score in sorted_candidates if score >= 2]
        
        # Remove duplicates while preserving order
        unique_platforms = []
        for platform in platforms:
            # Skip very short names or common words
            if len(platform) <= 2 or platform.lower() in ['sim', 'não', 'pix', 'app', 'site', 'link']:
                continue
                
            # Check if it's a variation of an already added platform
            duplicate = False
            for existing in unique_platforms:
                if platform.lower() in existing.lower() or existing.lower() in platform.lower():
                    duplicate = True
                    break
            
            if not duplicate:
                unique_platforms.append(platform)
        
        print(f"[+] Extracted {len(unique_platforms)} potential platform names")
        return unique_platforms
    
    def extract_links(self, text: str) -> List[str]:
        """
        Extract web links from text
        
        Args:
            text: The text to analyze
            
        Returns:
            List of detected URLs
        """
        if not text:
            return []
        
        # URL pattern matching
        url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[/\w\.-]*(?:\?[/\w\.-=&]*)?'
        urls = re.findall(url_pattern, text)
        
        # Filter out YouTube and common URLs
        filtered_urls = []
        for url in urls:
            domain = urlparse(url).netloc
            if ("youtube.com" not in domain and 
                "youtu.be" not in domain and
                "google.com" not in domain and
                "facebook.com" not in domain and
                "instagram.com" not in domain):
                filtered_urls.append(url)
        
        print(f"[+] Extracted {len(filtered_urls)} URLs")
        return filtered_urls
    
    def extract_messaging_groups(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract messaging app group links (WhatsApp, Telegram)
        
        Args:
            text: The text to analyze
            
        Returns:
            List of dictionaries with platform type and link
        """
        if not text:
            return []
        
        groups = []
        
        # Extract WhatsApp groups
        whatsapp_pattern = r'https?://(?:chat\.)?whatsapp\.com/(?:invite/)?(?:[-\w]*)'
        whatsapp_links = re.findall(whatsapp_pattern, text)
        
        for i, link in enumerate(whatsapp_links):
            # Try to find a name near the link
            link_pos = text.find(link)
            if link_pos >= 0:
                start = max(0, link_pos - 100)
                end = min(len(text), link_pos + len(link) + 100)
                window = text[start:end]
                
                # Look for potential group names
                name_match = re.search(r'grupo\s+(?:do|de|da)?\s+([A-Za-z0-9\s]{3,30})', window, re.IGNORECASE)
                name = f"WhatsApp Group {i+1}"
                if name_match:
                    name = name_match.group(1).strip()
                
                groups.append({
                    "platform": "WhatsApp",
                    "name": name,
                    "link": link
                })
        
        # Extract Telegram groups/channels
        telegram_pattern = r'https?://(?:t\.me|telegram\.me|telegram\.dog)/(?:joinchat/)?(?:[-\w]*)'
        telegram_links = re.findall(telegram_pattern, text)
        
        for i, link in enumerate(telegram_links):
            # Try to find a name near the link
            link_pos = text.find(link)
            if link_pos >= 0:
                start = max(0, link_pos - 100)
                end = min(len(text), link_pos + len(link) + 100)
                window = text[start:end]
                
                # Look for potential group/channel names
                name_match = re.search(r'(?:canal|grupo|channel)\s+(?:do|de|da)?\s+([A-Za-z0-9\s]{3,30})', window, re.IGNORECASE)
                name = f"Telegram Channel {i+1}"
                if name_match:
                    name = name_match.group(1).strip()
                
                groups.append({
                    "platform": "Telegram",
                    "name": name,
                    "link": link
                })
        
        print(f"[+] Extracted {len(groups)} messaging groups/channels")
        return groups
    
    def process_video(self, video: Dict[str, Any]) -> Tuple[List[str], List[str], List[Dict[str, Any]]]:
        """
        Process a video to extract platforms, links, and messaging groups
        
        Args:
            video: Video dictionary containing title and description
            
        Returns:
            Tuple of (platforms, links, groups)
        """
        # Combine title and description
        title = video.get('title', '')
        description = video.get('description', '')
        combined_text = f"{title}\n\n{description}"
        
        # Extract data
        platforms = self.extract_platforms(combined_text)
        links = self.extract_links(combined_text)
        groups = self.extract_messaging_groups(combined_text)
        
        return platforms, links, groups