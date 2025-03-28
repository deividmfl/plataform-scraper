import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_notification(email_address, video):
    """
    Send an email notification about a new video with platform mentions.
    
    Args:
        email_address (str): Recipient email address.
        video (dict): Video data to include in the notification.
    
    Returns:
        bool: True if sent successfully, False otherwise.
    """
    try:
        # Get SMTP settings from environment variables
        smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        smtp_username = os.getenv("SMTP_USERNAME", "")
        smtp_password = os.getenv("SMTP_PASSWORD", "")
        
        # If SMTP credentials are not configured, just log and return
        if not smtp_username or not smtp_password:
            print(f"SMTP not configured, would send notification to {email_address} about video {video['id']}")
            return False
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = smtp_username
        msg['To'] = email_address
        msg['Subject'] = f"New Investment Video: {video['title']}"
        
        # Build the email content
        body = f"""
        <html>
        <body style="font-family: monospace; background-color: #0e0e0e; color: #00ff41; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; border: 1px solid #00ff41; padding: 20px;">
                <h1 style="color: #00ff41;">Matrix Investment Tracker Alert</h1>
                <p>A new video has been detected with potential investment platform mentions:</p>
                
                <h2 style="color: #ff0000;">{video['title']}</h2>
                <p><strong>Channel:</strong> {video['channel']}</p>
                <p><strong>Published:</strong> {video['publish_date']}</p>
                <p><strong>URL:</strong> <a href="{video['url']}" style="color: #00ff41;">{video['url']}</a></p>
                
                <h3 style="color: #00ff41;">Platforms Mentioned:</h3>
                <ul>
        """
        
        # Add platforms
        if video.get('platforms') and len(video['platforms']) > 0:
            for platform in video['platforms']:
                body += f"<li>{platform}</li>"
        else:
            body += "<li>No specific platforms detected</li>"
        
        body += "</ul><h3 style='color: #00ff41;'>Links Found:</h3><ul>"
        
        # Add links
        if video.get('links') and len(video['links']) > 0:
            for link in video['links']:
                body += f"<li><a href='{link['url']}' style='color: #00ff41;'>{link['domain']}</a></li>"
        else:
            body += "<li>No links detected</li>"
        
        # Add groups
        body += "</ul><h3 style='color: #00ff41;'>Messaging Groups:</h3><ul>"
        
        whatsapp_groups = video.get('groups', {}).get('whatsapp', [])
        telegram_groups = video.get('groups', {}).get('telegram', [])
        
        if whatsapp_groups:
            for group in whatsapp_groups:
                body += f"<li>WhatsApp: <a href='{group['url']}' style='color: #00ff41;'>{group['url']}</a></li>"
        
        if telegram_groups:
            for group in telegram_groups:
                body += f"<li>Telegram: <a href='{group['url']}' style='color: #00ff41;'>{group['username']}</a></li>"
        
        if not whatsapp_groups and not telegram_groups:
            body += "<li>No messaging groups detected</li>"
        
        body += """
                </ul>
                <p style="margin-top: 30px; font-size: 12px; color: #666;">
                    This is an automated notification from the Matrix Investment Tracker.
                    Follow the white rabbit.
                </p>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        # Connect to server and send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
        
        print(f"Notification sent to {email_address} about video {video['id']}")
        return True
        
    except Exception as e:
        print(f"Error sending notification: {str(e)}")
        return False
