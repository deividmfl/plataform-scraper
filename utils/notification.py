import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Any

class EmailNotifier:
    """
    Send email notifications about newly discovered videos
    """
    
    def __init__(self):
        """Initialize the email notifier"""
        # Get SMTP settings from environment variables with defaults
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.sender_email = os.getenv("SENDER_EMAIL", self.smtp_username)
    
    def send_notification(self, subject: str, videos: List[Dict[str, Any]], recipient_email: str = None) -> bool:
        """
        Send email notification with information about new videos
        
        Args:
            subject: Email subject
            videos: List of video dictionaries
            recipient_email: Email recipient (uses RECIPIENT_EMAIL env var if not provided)
            
        Returns:
            Boolean indicating success
        """
        if not self.smtp_username or not self.smtp_password:
            print("SMTP credentials not configured. Skipping email notification.")
            return False
        
        recipient = recipient_email or os.getenv("RECIPIENT_EMAIL", "")
        if not recipient:
            print("Recipient email not provided. Skipping email notification.")
            return False
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = self.sender_email
        msg['To'] = recipient
        msg['Subject'] = subject
        
        # Create HTML content
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; color: #333; }}
                .video {{ margin-bottom: 20px; border: 1px solid #ccc; padding: 10px; }}
                .platform {{ color: #00aa00; font-weight: bold; }}
                h2 {{ color: #0066cc; }}
                .link {{ color: #0066cc; }}
            </style>
        </head>
        <body>
            <h1>New Investment Videos Detected</h1>
            <p>The Matrix-Inspired Video Intelligence System has detected {len(videos)} new investment-related videos.</p>
        """
        
        # Add video information
        for video in videos[:10]:  # Limit to 10 videos
            platforms = ', '.join(video.get('platforms', []))
            if not platforms:
                platforms = "None detected"
            
            links = video.get('links', [])
            link_html = ""
            if links:
                link_html = "<ul>"
                for link in links:
                    link_html += f"<li><a href='{link}' class='link'>{link}</a></li>"
                link_html += "</ul>"
            else:
                link_html = "<p>No links detected</p>"
            
            html += f"""
            <div class='video'>
                <h2>{video.get('title', 'Untitled')}</h2>
                <p><strong>Channel:</strong> {video.get('channel_name', 'Unknown')}</p>
                <p><strong>Published:</strong> {video.get('publish_date', 'Unknown')}</p>
                <p><strong>Link:</strong> <a href='https://youtube.com/watch?v={video.get('id', '')}' class='link'>View on YouTube</a></p>
                <p><strong>Platforms Detected:</strong> <span class='platform'>{platforms}</span></p>
                <p><strong>External Links:</strong></p>
                {link_html}
            </div>
            """
        
        # Add footer
        html += """
            <p>This is an automated message from the Matrix-Inspired Video Intelligence System.</p>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(html, 'html'))
        
        try:
            # Connect to SMTP server
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            
            # Send email
            server.send_message(msg)
            server.quit()
            return True
        
        except Exception as e:
            print(f"Error sending email notification: {str(e)}")
            return False
