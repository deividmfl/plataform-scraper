import streamlit as st

def apply_terminal_style():
    """
    Apply a terminal/hacker-style to the Streamlit app
    """
    
    # CSS for terminal/hacker style
    st.markdown("""
    <style>
    /* Base styles */
    .stApp {
        font-family: 'Courier New', monospace !important;
    }
    
    /* Custom terminal container */
    .terminal-container {
        background-color: #0c1419;
        border: 1px solid #00ff00;
        border-radius: 5px;
        padding: 15px;
        color: #00ff00;
        font-family: 'Courier New', monospace;
        margin-bottom: 20px;
        position: relative;
    }
    
    /* Terminal header */
    .terminal-header {
        border-bottom: 1px solid #00ff00;
        padding-bottom: 8px;
        margin-bottom: 10px;
        display: flex;
        justify-content: space-between;
    }
    
    /* Terminal content */
    .terminal-content {
        overflow-x: auto;
        white-space: pre-wrap;
    }
    
    /* Terminal dots */
    .terminal-dots {
        display: flex;
        align-items: center;
        gap: 5px;
    }
    
    .dot {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        display: inline-block;
    }
    
    .dot-red {
        background-color: #ff3b30;
    }
    
    .dot-yellow {
        background-color: #ffcc00;
    }
    
    .dot-green {
        background-color: #4cd964;
    }
    
    /* Sidebar styling */
    .css-1aumxhk, .css-1r6slb0 {
        background-color: #1a1e25 !important;
        border-right: 1px solid #00ff00 !important;
    }
    
    /* Button styling */
    .stButton>button, div.stDownloadButton > button {
        background-color: #111822 !important;
        color: #00ff00 !important;
        border: 1px solid #00ff00 !important;
        border-radius: 5px !important;
        font-family: 'Courier New', monospace !important;
        transition: all 0.3s !important;
    }
    
    .stButton>button:hover, div.stDownloadButton > button:hover {
        background-color: #00ff00 !important;
        color: #111822 !important;
    }
    
    /* Input fields */
    .stTextInput>div>div>input, .stNumberInput>div>div>input {
        background-color: #111822 !important;
        color: #00ff00 !important;
        border: 1px solid #00ff00 !important;
        border-radius: 5px !important;
        font-family: 'Courier New', monospace !important;
    }
    
    /* Dropdown and Selectbox */
    .stSelectbox>div>div, .stMultiSelect>div>div {
        background-color: #111822 !important;
        color: #00ff00 !important;
        border: 1px solid #00ff00 !important;
        border-radius: 5px !important;
        font-family: 'Courier New', monospace !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #111822 !important;
        border-radius: 5px !important;
        gap: 5px !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #111822 !important;
        color: #00ff00 !important;
        border: 1px solid #00ff00 !important;
        border-radius: 5px !important;
        font-family: 'Courier New', monospace !important;
        padding: 5px 10px !important;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #00ff00 !important;
        color: #111822 !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: #111822 !important;
        color: #00ff00 !important;
        border: 1px solid #00ff00 !important;
        border-radius: 5px !important;
        font-family: 'Courier New', monospace !important;
    }
    
    /* Progress bar */
    .stProgress > div > div > div > div {
        background-color: #00ff00 !important;
    }
    
    /* Checkbox */
    .stCheckbox label span {
        color: #00ff00 !important;
    }
    
    /* Typing animation */
    @keyframes typing {
        from { width: 0 }
        to { width: 100% }
    }
    
    @keyframes blink-caret {
        from, to { border-color: transparent }
        50% { border-color: #00ff00; }
    }
    
    .typing-animation {
        overflow: hidden;
        white-space: nowrap;
        border-right: .15em solid #00ff00;
        margin: 0 auto;
        animation: 
            typing 3.5s steps(40, end),
            blink-caret .75s step-end infinite;
    }
    
    /* Glow effect */
    .glow-text {
        text-shadow: 0 0 5px #00ff00, 0 0 10px #00ff00;
    }
    
    /* Console log text */
    .console-log {
        font-family: 'Courier New', monospace;
        color: #00ff00;
        background-color: #0a0f15;
        padding: 10px;
        border-radius: 5px;
        border-left: 3px solid #00ff00;
        white-space: pre-wrap;
        font-size: 14px;
        line-height: 1.5;
        overflow-x: auto;
    }
    
    /* Tooltip */
    .tooltip {
        position: relative;
        display: inline-block;
        cursor: pointer;
    }

    .tooltip .tooltiptext {
        visibility: hidden;
        width: 200px;
        background-color: #111822;
        color: #00ff00;
        text-align: center;
        border-radius: 6px;
        border: 1px solid #00ff00;
        padding: 5px;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        margin-left: -100px;
        opacity: 0;
        transition: opacity 0.3s;
    }

    .tooltip:hover .tooltiptext {
        visibility: visible;
        opacity: 1;
    }
    
    /* Warning message */
    .warning-message {
        color: #ff3b30;
        border-left: 3px solid #ff3b30;
        padding-left: 10px;
    }
    
    /* Success message */
    .success-message {
        color: #4cd964;
        border-left: 3px solid #4cd964;
        padding-left: 10px;
    }
    
    /* Special header style */
    .header-text {
        font-size: 40px;
        font-weight: bold;
        text-align: center;
        color: #00ff00;
        text-shadow: 0 0 10px #00ff00, 0 0 20px #00ff00;
        letter-spacing: 2px;
        margin-bottom: 20px;
    }
    
    /* Subheader style */
    .subheader-text {
        font-size: 16px;
        text-align: center;
        color: #cccccc;
        margin-bottom: 30px;
    }
    
    /* Blinking cursor */
    .blinking-cursor {
        animation: blink 1s step-end infinite;
    }
    
    @keyframes blink {
        from, to { opacity: 1; }
        50% { opacity: 0; }
    }
    
    </style>
    """, unsafe_allow_html=True)

def terminal_container(title, content="", expand=True):
    """
    Create a terminal-like container
    
    Args:
        title: Title of the terminal container
        content: HTML content to display
        expand: Whether to expand the container by default
    """
    header_html = f"""
    <div class="terminal-container">
        <div class="terminal-header">
            <div class="terminal-dots">
                <span class="dot dot-red"></span>
                <span class="dot dot-yellow"></span>
                <span class="dot dot-green"></span>
            </div>
            <div style="color: #00ff00; font-family: 'Courier New', monospace;">{title}</div>
            <div style="width: 60px;"></div>
        </div>
    """
    
    if content:
        content_html = f"""
        <div class="terminal-content">
            {content}
        </div>
        """
    else:
        content_html = ""
        
    footer_html = "</div>"
    
    terminal_html = header_html + content_html + footer_html
    
    if expand:
        st.markdown(terminal_html, unsafe_allow_html=True)
    else:
        with st.expander(title, expanded=False):
            st.markdown(terminal_html, unsafe_allow_html=True)

def console_print(text):
    """
    Create a console log style text
    
    Args:
        text: Text to display
    """
    st.markdown(f'<div class="console-log">{text}</div>', unsafe_allow_html=True)

def typing_animation(text):
    """
    Create a typing animation effect
    
    Args:
        text: Text to animate
    """
    st.markdown(f'<div class="typing-animation">{text}</div>', unsafe_allow_html=True)

def glow_text(text):
    """
    Create a glowing text effect
    
    Args:
        text: Text to glow
    """
    st.markdown(f'<div class="glow-text">{text}</div>', unsafe_allow_html=True)

def header():
    """Display the application header"""
    st.markdown('<div class="header-text">PLATFORM SCRAPER</div>', unsafe_allow_html=True)
    st.markdown('<div class="subheader-text">Advanced Web Platform Monitoring & Analysis</div>', unsafe_allow_html=True)

def tooltip(text, tooltip_text):
    """
    Create a tooltip element
    
    Args:
        text: Main visible text
        tooltip_text: Text to show in tooltip
    """
    st.markdown(f'''
    <div class="tooltip">{text}
        <span class="tooltiptext">{tooltip_text}</span>
    </div>
    ''', unsafe_allow_html=True)

def warning(text):
    """Display a warning message"""
    st.markdown(f'<div class="warning-message">{text}</div>', unsafe_allow_html=True)

def success(text):
    """Display a success message"""
    st.markdown(f'<div class="success-message">{text}</div>', unsafe_allow_html=True)

def blinking_cursor():
    """Display a blinking cursor"""
    st.markdown('<span class="blinking-cursor">█</span>', unsafe_allow_html=True)