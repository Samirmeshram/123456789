import os

class Config:
    # Bot Configuration (Your provided credentials)
    API_ID = 29895250
    API_HASH = "29ca1e2311efdf950eea03a6ae2bc8ee"
    BOT_TOKEN = "8467505471:AAGcQ53WlAe6XAWSMxVg93hOn1V94Cv3x0Q"
    
    # Database Configuration
    DATABASE_URL = "mongodb+srv://Dpcinema:Dpcinema@atlascluster.mcfyzy4.mongodb.net/?retryWrites=true&w=majority&appName=AtlasCluster"
    DATABASE_NAME = "Dpcinema"
    
    # Channel Configuration
    DATABASE_CHANNEL = -1002191746646
    FORCE_SUB_CHANNEL = -1002481039236
    
    # Owner
    OWNER_ID = 2017335429
    ADMINS = [2017335429]  # Owner as admin
    
    # Verification Settings
    MIN_VERIFICATION_TIME = 30
    VERIFICATION_TIMEOUT = 300
    
    # Blogger Pages Configuration - YOUR BLOGGER LINK
    BLOGGER_BASE_URL = "https://dpcinemafiles.blogspot.com/2025/10/Redirect.html"
    BOT_USERNAME = "ALEX_STAR_MY_LOVE_BOT"  # YOUR BOT USERNAME
    
    # File Settings - UNLIMITED
    MAX_FILE_SIZE = 0  # 0 means unlimited
    ALLOWED_EXTENSIONS = ['*']  # All extensions allowed
    
    # Batch Settings - UNLIMITED
    MAX_BATCH_FILES = 0  # 0 means unlimited
    BATCH_MAX_SIZE = 0   # 0 means unlimited

config = Config()
