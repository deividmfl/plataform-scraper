import streamlit as st

def render_settings():
    """Render the settings page for configuring the application."""
    st.markdown("""
    <div class="matrix-title">
        <h1>SYSTEM <span class="red-text">CONFIGURATION</span></h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize settings in session state if not present
    if 'search_days' not in st.session_state:
        st.session_state.search_days = 30
    
    if 'keywords' not in st.session_state:
        st.session_state.keywords = [
            'plataforma de investimento', 
            'pagamento instantâneo', 
            'prova de pagamento', 
            'multinível'
        ]
    
    # Create tabs for different settings
    tab1, tab2, tab3 = st.tabs(["Search Settings", "Notification Settings", "System Settings"])
    
    with tab1:
        st.markdown("""
        <div class="settings-section">
            <h3>SEARCH PARAMETERS</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Set search period
        search_days = st.slider(
            "Search Period (Days)",
            min_value=1,
            max_value=90,
            value=st.session_state.search_days,
            help="Maximum age of videos to search for (in days)"
        )
        
        # Keywords input
        st.markdown("### Search Keywords")
        st.markdown("Enter one keyword per line. These will be used for video searches.")
        
        keywords_text = st.text_area(
            "Keywords",
            value="\n".join(st.session_state.keywords),
            height=200,
            help="Enter search keywords, one per line"
        )
        
        # Save button
        if st.button("Save Search Settings"):
            st.session_state.search_days = search_days
            st.session_state.keywords = [k.strip() for k in keywords_text.split("\n") if k.strip()]
            st.success("Search settings saved successfully!")
    
    with tab2:
        st.markdown("""
        <div class="settings-section">
            <h3>NOTIFICATION SETTINGS</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Email notification settings
        st.markdown("### Email Notifications")
        notification_email = st.text_input(
            "Email Address",
            value=st.session_state.get('notification_email', ''),
            help="Email address to receive notifications"
        )
        
        # SMTP server settings
        st.markdown("### SMTP Server Configuration")
        st.markdown("These settings are required for sending email notifications.")
        
        smtp_server = st.text_input(
            "SMTP Server",
            value=st.session_state.get('smtp_server', 'smtp.gmail.com'),
            help="SMTP server address"
        )
        
        smtp_port = st.number_input(
            "SMTP Port",
            value=st.session_state.get('smtp_port', 587),
            help="SMTP server port"
        )
        
        smtp_username = st.text_input(
            "SMTP Username",
            value=st.session_state.get('smtp_username', ''),
            help="SMTP username (usually your email address)"
        )
        
        smtp_password = st.text_input(
            "SMTP Password",
            value=st.session_state.get('smtp_password', ''),
            type="password",
            help="SMTP password or app password"
        )
        
        # Save button
        if st.button("Save Notification Settings"):
            st.session_state.notification_email = notification_email
            st.session_state.smtp_server = smtp_server
            st.session_state.smtp_port = smtp_port
            st.session_state.smtp_username = smtp_username
            st.session_state.smtp_password = smtp_password
            
            # Set environment variables for SMTP configuration
            import os
            os.environ["SMTP_SERVER"] = smtp_server
            os.environ["SMTP_PORT"] = str(smtp_port)
            os.environ["SMTP_USERNAME"] = smtp_username
            os.environ["SMTP_PASSWORD"] = smtp_password
            
            st.success("Notification settings saved successfully!")
    
    with tab3:
        st.markdown("""
        <div class="settings-section">
            <h3>SYSTEM SETTINGS</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Scan frequency
        st.markdown("### Automatic Scanning")
        scan_frequency = st.selectbox(
            "Scan Frequency",
            options=["Manual Only", "Every 12 Hours", "Every 24 Hours"],
            index=1,  # Default to Every 12 Hours
            help="How often the system should automatically scan for new videos"
        )
        
        # Set environment variable for scan frequency
        if st.button("Save System Settings"):
            st.session_state.scan_frequency = scan_frequency
            st.success("System settings saved successfully!")
        
        # Reset database option
        st.markdown("### Database Management")
        
        if st.button("Clear Database", type="secondary"):
            confirmation = st.text_input(
                "Type 'RESET' to confirm database reset",
                key="reset_confirmation"
            )
            
            if confirmation == "RESET":
                st.session_state.videos = []
                from utils.data_storage import save_videos
                save_videos([])
                st.success("Database has been reset successfully!")
