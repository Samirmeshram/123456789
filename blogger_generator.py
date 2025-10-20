import os
import json
from datetime import datetime

class BloggerPageGenerator:
    def __init__(self, templates_dir="templates"):
        self.templates_dir = templates_dir
        self.setup_templates()
    
    def setup_templates(self):
        """Setup HTML templates directory"""
        os.makedirs(self.templates_dir, exist_ok=True)
    
    def generate_blogger_url(self, file_id, file_name, file_size):
        """Generate blogger URL with parameters"""
        from config import config
        
        # URL encode parameters
        import urllib.parse
        encoded_name = urllib.parse.quote(file_name)
        
        blogger_url = f"{config.BLOGGER_BASE_URL}?file={file_id}&name={encoded_name}&size={file_size}"
        return blogger_url
    
    def generate_page_content(self, file_id, file_name, file_size, bot_username="ALEX_STAR_MY_LOVE_BOT"):
        """Generate complete blogger page HTML content"""
        
        html_content = f"""<!DOCTYPE html>
<html lang='en'>
<head>
    <meta charset='utf-8'/>
    <meta content='width=device-width, initial-scale=1' name='viewport'/>
    <title>Download {file_name} - DP Cinema</title>
    <b:skin><![CDATA[/* Blogger default styles */]]></b:skin>

    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }}

        .download-container {{
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
            max-width: 500px;
            width: 100%;
            text-align: center;
        }}

        .download-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px 20px;
        }}

        .download-header h1 {{
            font-size: 28px;
            margin-bottom: 10px;
        }}

        .download-content {{
            padding: 30px;
        }}

        .file-info {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            text-align: left;
        }}

        .info-row {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
            padding-bottom: 8px;
            border-bottom: 1px solid #e9ecef;
        }}

        .info-label {{
            font-weight: 600;
            color: #555;
        }}

        .info-value {{
            color: #333;
        }}

        .countdown {{
            font-size: 24px;
            font-weight: bold;
            color: #667eea;
            margin: 20px 0;
        }}

        .progress-bar {{
            width: 100%;
            height: 8px;
            background: #e9ecef;
            border-radius: 4px;
            margin: 20px 0;
            overflow: hidden;
        }}

        .progress {{
            height: 100%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            width: 0%;
            transition: width 0.3s ease;
        }}

        .download-btn {{
            display: none;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 30px;
            border-radius: 50px;
            text-decoration: none;
            font-weight: bold;
            font-size: 18px;
            margin: 20px 0;
            transition: transform 0.3s ease;
        }}

        .download-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.2);
        }}

        .security-badge {{
            display: inline-flex;
            align-items: center;
            background: #e8f5e8;
            color: #2e7d32;
            padding: 8px 15px;
            border-radius: 20px;
            font-size: 14px;
            margin: 10px 0;
        }}

        .instructions {{
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 10px;
            padding: 15px;
            margin: 20px 0;
            text-align: left;
        }}

        .instructions h4 {{
            color: #856404;
            margin-bottom: 10px;
        }}

        .instructions ol {{
            padding-left: 20px;
        }}

        .instructions li {{
            margin-bottom: 8px;
            color: #856404;
        }}

        @media (max-width: 768px) {{
            .download-container {{
                margin: 10px;
                border-radius: 15px;
            }}
            
            .download-header {{
                padding: 20px 15px;
            }}
            
            .download-header h1 {{
                font-size: 24px;
            }}
            
            .download-content {{
                padding: 20px;
            }}
            
            .countdown {{
                font-size: 20px;
            }}
        }}
    </style>
</head>

<body>
    <!-- BLOGGER DEFAULT CONTENT -->
    <b:section id='main' maxwidgets='1' showaddelement='no'>
    <b:widget id='Blog1' locked='true' title='Blog Posts' type='Blog'/>
    </b:section>

    <!-- CUSTOM DOWNLOAD PAGE CONTENT -->
    <div class="download-container">
        <div class="download-header">
            <h1>🎬 DP Cinema Files</h1>
            <p>Secure File Download</p>
        </div>
        
        <div class="download-content">
            <div class="security-badge">
                🔒 Secure & Verified Download
            </div>
            
            <div class="file-info">
                <h3>File Information</h3>
                <div class="info-row">
                    <span class="info-label">File Name:</span>
                    <span class="info-value" id="fileName">{file_name}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">File Size:</span>
                    <span class="info-value" id="fileSize">{self.format_size(file_size)}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">File ID:</span>
                    <span class="info-value" id="fileId">{file_id}</span>
                </div>
            </div>
            
            <div class="instructions">
                <h4>📋 Download Instructions</h4>
                <ol>
                    <li>Wait for the countdown to complete</li>
                    <li>Click the Telegram download button</li>
                    <li>Complete verification in the bot</li>
                    <li>Get your file instantly</li>
                </ol>
            </div>
            
            <div class="countdown" id="countdown">Starting in 5 seconds...</div>
            
            <div class="progress-bar">
                <div class="progress" id="progressBar"></div>
            </div>
            
            <a href="#" class="download-btn" id="downloadBtn">
                📲 Get File via Telegram
            </a>
            
            <div style="text-align: center; margin-top: 20px;">
                <small style="color: #666;">
                    © 2024 DP Cinema Files | Powered by @{bot_username}
                </small>
            </div>
        </div>
    </div>

    <script>
        // Get URL parameters
        function getUrlParameter(name) {{
            name = name.replace(/[\\[]/, '\\\\[').replace(/[\\]]/, '\\\\]');
            var regex = new RegExp('[\\\\?&]' + name + '=([^&#]*)');
            var results = regex.exec(location.search);
            return results === null ? '' : decodeURIComponent(results[1].replace(/\\+/g, ' '));
        }}

        // Configuration from URL parameters
        const urlFileId = getUrlParameter('file') || '{file_id}';
        const urlFileName = getUrlParameter('name') || '{file_name}';
        const urlFileSize = getUrlParameter('size') || '{file_size}';

        // BOT USERNAME - YOUR ACTUAL BOT USERNAME
        const botUsername = "{bot_username}";

        // Update page with file info
        document.getElementById('fileName').textContent = urlFileName;
        document.getElementById('fileSize').textContent = formatFileSize(urlFileSize);
        document.getElementById('fileId').textContent = urlFileId;

        // Format file size
        function formatFileSize(bytes) {{
            if (!bytes || bytes === '0') return '0 B';
            
            bytes = parseInt(bytes);
            const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
            const i = Math.floor(Math.log(bytes) / Math.log(1024));
            return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
        }}

        // Countdown function
        function startCountdown() {{
            const botLink = `https://t.me/${{botUsername}}?start=${{urlFileId}}`;
            let seconds = 5;
            
            const timer = setInterval(() => {{
                if (seconds > 0) {{
                    document.getElementById('countdown').textContent = `Download starts in ${{seconds}} seconds...`;
                    document.getElementById('progressBar').style.width = `${{100 - (seconds/5)*100}}%`;
                    seconds--;
                }} else {{
                    clearInterval(timer);
                    document.getElementById('countdown').innerHTML = '✅ <strong>Ready to Download!</strong>';
                    document.getElementById('progressBar').style.width = "100%";
                    document.getElementById('progressBar').style.background = "#4CAF50";
                    document.getElementById('downloadBtn').href = botLink;
                    document.getElementById('downloadBtn').style.display = 'inline-block';
                    
                    // Auto-click after 2 seconds for better UX
                    setTimeout(() => {{
                        document.getElementById('downloadBtn').click();
                    }}, 2000);
                }}
            }}, 1000);
        }}

        // Start countdown when page loads
        window.onload = startCountdown;
    </script>
</body>
</html>"""
        
        return html_content

    def format_size(self, size_bytes):
        """Format file size"""
        if not size_bytes: 
            return "0 B"
        
        try:
            size_bytes = int(size_bytes)
            size_names = ["B", "KB", "MB", "GB", "TB"]
            i = 0
            
            while size_bytes >= 1024 and i < len(size_names) - 1:
                size_bytes /= 1024.0
                i += 1
            
            return f"{size_bytes:.2f} {size_names[i]}"
        except:
            return "Unknown Size"
