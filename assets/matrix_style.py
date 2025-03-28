import streamlit as st

def apply_matrix_style():
    """
    Apply Matrix-inspired styling to the Streamlit app
    """
    # Custom Matrix-inspired CSS
    matrix_css = """
    <style>
        /* Matrix green and black theme */
        .matrix-header {
            color: #00ff00 !important;
            font-family: monospace !important;
            text-shadow: 0 0 5px #00ff00, 0 0 10px #00ff00;
            animation: pulse 2s infinite;
        }
        
        /* Matrix-style animation for header */
        @keyframes pulse {
            0% { text-shadow: 0 0 5px #00ff00, 0 0 10px #00ff00; }
            50% { text-shadow: 0 0 10px #00ff00, 0 0 20px #00ff00, 0 0 30px #00ff00; }
            100% { text-shadow: 0 0 5px #00ff00, 0 0 10px #00ff00; }
        }
        
        /* Matrix-style text for details */
        .matrix-text {
            color: #00ff00 !important;
            font-family: monospace !important;
        }
        
        /* Matrix-style cards for video listings */
        .matrix-card {
            background-color: rgba(0, 0, 0, 0.8) !important;
            border: 1px solid #00ff00 !important;
            border-radius: 5px !important;
            padding: 10px !important;
            margin-bottom: 10px !important;
            box-shadow: 0 0 10px #00ff00 !important;
        }
        
        /* Matrix-style links */
        a {
            color: #ff0000 !important;
            text-decoration: none !important;
        }
        
        a:hover {
            color: #ffffff !important;
            text-shadow: 0 0 5px #ffffff, 0 0 10px #ffffff;
        }
        
        /* Matrix-style buttons */
        .stButton>button {
            color: #00ff00 !important;
            background-color: #000000 !important;
            border: 1px solid #00ff00 !important;
            box-shadow: 0 0 5px #00ff00 !important;
            font-family: monospace !important;
        }
        
        .stButton>button:hover {
            color: #000000 !important;
            background-color: #00ff00 !important;
            box-shadow: 0 0 10px #00ff00, 0 0 20px #00ff00 !important;
        }
        
        /* Matrix code rain animation for background */
        .matrix-container {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            z-index: -1;
            overflow: hidden;
            opacity: 0.1;
        }
    </style>
    
    <div class="matrix-container" id="matrix-rain"></div>
    
    <script>
    document.addEventListener("DOMContentLoaded", function() {
        // Matrix code rain effect
        const canvas = document.createElement('canvas');
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        canvas.style.position = 'fixed';
        canvas.style.top = '0';
        canvas.style.left = '0';
        canvas.style.zIndex = '-1';
        document.getElementById('matrix-rain').appendChild(canvas);
        
        const ctx = canvas.getContext('2d');
        
        // Matrix characters
        const matrix = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789$+-*/=%\"'#&_(),.;:?!\\|{}<>[]^~";
        
        // Converting the string into an array of single characters
        const characters = matrix.split("");
        
        const fontSize = 10;
        const columns = canvas.width/fontSize; // Number of columns for the rain
        
        // An array of drops - one per column
        const drops = [];
        
        // x below is the x coordinate
        // 1 = y coordinate of the drop(same for every drop initially)
        for(let x = 0; x < columns; x++)
            drops[x] = 1; 
        
        // Drawing the characters
        function draw() {
            // Black BG for the canvas
            // Translucent BG to show trail
            ctx.fillStyle = "rgba(0, 0, 0, 0.04)";
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            ctx.fillStyle = "#00ff00"; // Matrix green text
            ctx.font = fontSize + "px monospace";
            
            // Looping over drops
            for(let i = 0; i < drops.length; i++) {
                // A random character to print
                const text = characters[Math.floor(Math.random()*characters.length)];
                
                // x = i*fontSize, y = value of drops[i]*fontSize
                ctx.fillText(text, i*fontSize, drops[i]*fontSize);
                
                // Sending the drop back to the top randomly after it has crossed the screen
                // Adding a randomness to the reset to make the drops scattered on the Y axis
                if(drops[i]*fontSize > canvas.height && Math.random() > 0.975)
                    drops[i] = 0;
                
                // Incrementing Y coordinate
                drops[i]++;
            }
        }
        
        setInterval(draw, 35);
    });
    </script>
    """
    
    # Inject custom CSS
    st.markdown(matrix_css, unsafe_allow_html=True)
    
    # Apply Matrix-style headers to all h1, h2, h3 elements
    st.markdown("""
    <script>
    document.addEventListener("DOMContentLoaded", function() {
        // Apply matrix-header class to all heading elements
        const headings = document.querySelectorAll('h1, h2, h3');
        headings.forEach(heading => {
            heading.classList.add('matrix-header');
        });
    });
    </script>
    """, unsafe_allow_html=True)
