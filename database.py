from pymongo import MongoClient
from datetime import datetime
import json

class DatabaseManager:
    def __init__(self, db_url, db_name):
        self.client = MongoClient(db_url)
        self.db = self.client[db_name]
        self.init_collections()
    
    def init_collections(self):
        """Initialize database collections"""
        collections = ['files', 'users', 'premium_users', 'verification_sessions', 'bot_config']
        
        for collection in collections:
            if collection not in self.db.list_collection_names():
                self.db.create_collection(collection)
    
    # File management methods
    def add_file(self, file_data):
        """Add file to database"""
        file_data['upload_date'] = datetime.now()
        file_data['download_count'] = 0
        file_data['is_active'] = True
        
        return self.db.files.insert_one(file_data)
    
    def get_file(self, file_id):
        """Get file by file_id"""
        return self.db.files.find_one({'file_id': file_id, 'is_active': True})
    
    def get_user_files(self, user_id):
        """Get all files uploaded by user"""
        return list(self.db.files.find({'uploader_id': user_id, 'is_active': True}).sort('upload_date', -1))
    
    def increment_download_count(self, file_id):
        """Increment download count for file"""
        return self.db.files.update_one(
            {'file_id': file_id}, 
            {'$inc': {'download_count': 1}}
        )
    
    # User management methods
    def add_user(self, user_data):
        """Add user to database"""
        user_data['joined_date'] = datetime.now()
        user_data['total_uploads'] = 0
        user_data['total_downloads'] = 0
        user_data['is_verified'] = False
        
        return self.db.users.update_one(
            {'user_id': user_data['user_id']},
            {'$set': user_data},
            upsert=True
        )
    
    def update_user_stats(self, user_id, uploads=0, downloads=0):
        """Update user statistics"""
        update_data = {}
        if uploads:
            update_data['$inc'] = {'total_uploads': uploads}
        if downloads:
            if '$inc' not in update_data:
                update_data['$inc'] = {}
            update_data['$inc']['total_downloads'] = downloads
        
        return self.db.users.update_one({'user_id': user_id}, update_data)
    
    # Premium users methods
    def add_premium_user(self, user_id, duration_days=30):
        """Add user to premium"""
        premium_until = datetime.now().timestamp() + (duration_days * 24 * 60 * 60)
        
        return self.db.premium_users.update_one(
            {'user_id': user_id},
            {'$set': {
                'is_premium': True,
                'premium_since': datetime.now(),
                'premium_until': datetime.fromtimestamp(premium_until)
            }},
            upsert=True
        )
    
    def remove_premium_user(self, user_id):
        """Remove user from premium"""
        return self.db.premium_users.update_one(
            {'user_id': user_id},
            {'$set': {'is_premium': False}}
        )
    
    def is_premium_user(self, user_id):
        """Check if user is premium"""
        user = self.db.premium_users.find_one({
            'user_id': user_id, 
            'is_premium': True,
            '$or': [
                {'premium_until': {'$exists': False}},
                {'premium_until': {'$gt': datetime.now()}}
            ]
        })
        return user is not None
    
    # Bot configuration methods
    def get_bot_username(self):
        """Get bot username from database"""
        config = self.db.bot_config.find_one({'key': 'bot_username'})
        return config['value'] if config else None
    
    def set_bot_username(self, username):
        """Set bot username in database"""
        return self.db.bot_config.update_one(
            {'key': 'bot_username'},
            {'$set': {'value': username}},
            upsert=True
        )
    
    # Verification sessions
    def add_verification_session(self, session_data):
        """Add verification session"""
        session_data['created_at'] = datetime.now()
        return self.db.verification_sessions.insert_one(session_data)
    
    def get_verification_session(self, session_id):
        """Get verification session"""
        return self.db.verification_sessions.find_one({'session_id': session_id})
    
    def update_verification_session(self, session_id, update_data):
        """Update verification session"""
        return self.db.verification_sessions.update_one(
            {'session_id': session_id},
            {'$set': update_data}
  )
