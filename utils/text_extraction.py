import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

# Download NLTK resources
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

# Regular expressions for finding links and platform names
WEBSITE_PATTERN = r'https?://(?:www\.)?([a-zA-Z0-9][-a-zA-Z0-9]{0,62}(?:\.[a-zA-Z0-9][-a-zA-Z0-9]{0,62})+)'
WHATSAPP_GROUP_PATTERN = r'https?://(?:chat\.)?whatsapp\.com/(?:invite/)?([a-zA-Z0-9]+)'
TELEGRAM_GROUP_PATTERN = r'https?://t\.me/([a-zA-Z0-9_]+)'

# Common investment platform keywords (in Portuguese)
PLATFORM_KEYWORDS = [
    'investimento', 'plataforma', 'trader', 'trading', 'forex', 'bitcoin', 'cripto',
    'criptomoeda', 'multinível', 'mlm', 'pagamento', 'rendimento', 'renda', 'lucro',
    'ganho', 'retorno', 'dividendo', 'rentabilidade', 'roi', 'juros'
]

def extract_platforms_and_links(video):
    """
    Extract platform names, website links, and messaging app groups from video data.
    
    Args:
        video (dict): Video data containing title and description.
        
    Returns:
        tuple: (platforms, links, groups) - Lists of extracted data.
    """
    text = f"{video['title']} {video['description']}"
    
    # Extract web links
    links = extract_links(text)
    
    # Extract messaging app groups
    groups = {
        'whatsapp': extract_whatsapp_groups(text),
        'telegram': extract_telegram_groups(text)
    }
    
    # Extract platform names
    platforms = extract_platform_names(text)
    
    return platforms, links, groups

def extract_links(text):
    """Extract website links from text."""
    links = []
    matches = re.finditer(WEBSITE_PATTERN, text)
    for match in matches:
        domain = match.group(1)
        full_url = match.group(0)
        links.append({
            'domain': domain,
            'url': full_url
        })
    return links

def extract_whatsapp_groups(text):
    """Extract WhatsApp group links from text."""
    groups = []
    matches = re.finditer(WHATSAPP_GROUP_PATTERN, text)
    for match in matches:
        invite_code = match.group(1)
        full_url = match.group(0)
        groups.append({
            'invite_code': invite_code,
            'url': full_url
        })
    return groups

def extract_telegram_groups(text):
    """Extract Telegram group links from text."""
    groups = []
    matches = re.finditer(TELEGRAM_GROUP_PATTERN, text)
    for match in matches:
        username = match.group(1)
        full_url = match.group(0)
        groups.append({
            'username': username,
            'url': full_url
        })
    return groups

def extract_platform_names(text):
    """
    Extract potential investment platform names from text.
    Uses a combination of pattern matching and keyword proximity.
    """
    platforms = []
    
    # Tokenize text
    try:
        tokens = word_tokenize(text.lower())
        stop_words = set(stopwords.words('portuguese'))
        
        # Find potential platform name candidates
        for i, token in enumerate(tokens):
            # Skip stop words and short tokens
            if token in stop_words or len(token) < 3:
                continue
            
            # Check if the token is near a platform keyword
            context_range = 5  # Words before and after to check
            start = max(0, i - context_range)
            end = min(len(tokens), i + context_range + 1)
            context = tokens[start:end]
            
            if any(keyword in context for keyword in PLATFORM_KEYWORDS):
                # Capitalize first letter of each word for better display
                platform_name = token.title()
                if platform_name not in platforms:
                    platforms.append(platform_name)
        
        # Look for platform names that might be in quotes
        quote_pattern = r'["\']([\w\s]{3,30})["\']'
        quote_matches = re.finditer(quote_pattern, text)
        for match in quote_matches:
            potential_name = match.group(1).strip()
            if len(potential_name.split()) <= 3:  # Limit to 3 words max
                platforms.append(potential_name)
    
    except Exception as e:
        print(f"Error in platform name extraction: {str(e)}")
    
    return list(set(platforms))  # Remove duplicates
