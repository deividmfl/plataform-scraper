import re
from typing import List, Dict, Any

class TextProcessor:
    """
    Process text from YouTube videos to extract investment platforms, links, and messaging groups
    """
    
    def __init__(self):
        """Initialize the text processor with common investment platform keywords"""
        # Common investment platform terms in Portuguese and English
        self.platform_keywords = [
            'investimento', 'investment', 'plataforma', 'platform', 'ganhos', 'earnings',
            'lucro', 'profit', 'renda', 'income', 'rendimento', 'yield', 'retorno', 'return',
            'pagamento', 'payment', 'dinheiro', 'money', 'financeiro', 'financial',
            'forex', 'trading', 'trade', 'trader', 'bitcoin', 'btc', 'crypto', 'cripto',
            'stake', 'apostas', 'betting', 'cassino', 'casino', 'sorteio', 'loteria', 'lottery',
            'multinível', 'multi-nível', 'multi level', 'mlm', 'marketing multinível',
            'pirâmide', 'pyramid', 'ponzi', 'hyip', 'high yield'
        ]
        
        # Known investment platform names
        self.known_platforms = [
            'blaze', 'bet365', 'binance', 'bitget', 'bybit', 'fox bet', 'betano',
            'sporting bet', 'sportingbet', 'kto', 'esporte da sorte', 'bet7k', 'betfair',
            'pixbet', 'betsson', 'parimatch', 'alphatrading', 'olymp trade', 'olymptrade',
            'iqoption', 'iq option', 'xp investimentos', 'xp', 'clear', 'rico', 'nubank',
            'atlas quantum', 'unick forex', 'trust investing', 'hehaka finance', 
            'g44', 'g 44', 'tigerbet', 'tiger bet', 'bet national', 'betnacional',
            'estrelabet', 'estrela bet', 'galerabet', 'galera bet'
        ]
    
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
        
        detected_platforms = []
        
        # Check for known platforms
        text_lower = text.lower()
        for platform in self.known_platforms:
            if platform.lower() in text_lower:
                if platform not in detected_platforms:
                    detected_platforms.append(platform)
        
        # Look for potential new platforms
        # Pattern: platform name followed by investment-related term
        patterns = [
            r'([A-Z][a-zA-Z0-9\s]{2,20})\s(?:' + '|'.join(self.platform_keywords) + ')',
            r'(?:plataforma|platform)\s(?:de\s)?(?:investimento|investment)?\s([A-Z][a-zA-Z0-9\s]{2,20})',
            r'(?:' + '|'.join(self.platform_keywords) + ')\s(?:na|no|pela|pelo|with|on|at)?\s([A-Z][a-zA-Z0-9\s]{2,20})'
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                platform_name = match.group(1).strip()
                if len(platform_name) >= 3 and platform_name.lower() not in [p.lower() for p in detected_platforms]:
                    detected_platforms.append(platform_name)
        
        return detected_platforms
    
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
        
        # URL pattern
        url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+(?:/[-\w%!./?=&+#]*)?'
        
        # Find all URLs
        urls = re.findall(url_pattern, text)
        
        # Clean URLs
        clean_urls = []
        for url in urls:
            # Filter out YouTube and common social media links
            if not any(domain in url.lower() for domain in ['youtube.com', 'youtu.be', 'instagram.com', 'facebook.com', 'twitter.com']):
                clean_urls.append(url)
        
        return clean_urls
    
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
        
        # WhatsApp group patterns
        whatsapp_patterns = [
            r'https?://(?:www\.)?chat\.whatsapp\.com/(?:[-\w%!./?=&+#]*)',
            r'https?://(?:www\.)?wa\.me/(?:[-\w%!./?=&+#]*)'
        ]
        
        # Telegram group patterns
        telegram_patterns = [
            r'https?://(?:www\.)?t\.me/(?:[-\w%!./?=&+#]*)',
            r'https?://(?:www\.)?telegram\.me/(?:[-\w%!./?=&+#]*)'
        ]
        
        # Extract WhatsApp groups
        for pattern in whatsapp_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                groups.append({
                    'platform': 'WhatsApp',
                    'link': match,
                    'name': 'WhatsApp Group'
                })
        
        # Extract Telegram groups
        for pattern in telegram_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                # Try to extract group name from link
                group_name = match.split('/')[-1]
                if group_name:
                    name = f"Telegram: {group_name}"
                else:
                    name = "Telegram Group"
                
                groups.append({
                    'platform': 'Telegram',
                    'link': match,
                    'name': name
                })
        
        return groups
