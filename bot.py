import os
import time
import logging
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait, UserNotParticipant

from config import config
from database import DatabaseManager
from verification_manager import VerificationManager
from blogger_generator import BloggerPageGenerator
from premium_manager import PremiumManager
from batch_processor import BatchProcessor
from auto_delete import AutoDeleteManager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize components
db = DatabaseManager(config.DATABASE_URL, config.DATABASE_NAME)
verification_mgr = VerificationManager(db)
blogger_gen = BloggerPageGenerator()
premium_mgr = PremiumManager(db)
batch_processor = BatchProcessor(db, premium_mgr)
auto_delete_mgr = AutoDeleteManager(db)

# Initialize bot
app = Client(
    "dp_cinema_bot",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    bot_token=config.BOT_TOKEN
)

# Store bot username globally
BOT_USERNAME = None

# Start auto-delete task
@app.on_start()
async def start_auto_delete():
    asyncio.create_task(auto_delete_mgr.start_auto_delete_task(app))

async def force_subscribe(client, user_id):
    """Check if user is subscribed to force channel"""
    try:
        user = await client.get_chat_member(config.FORCE_SUB_CHANNEL, user_id)
        if user.status in ["left", "kicked"]:
            return False
        return True
    except Exception as e:
        logger.error(f"Force sub check error: {e}")
        return True

# ==================== COMMAND HANDLERS ====================

@app.on_message(filters.command("start"))
async def start_command(client, message: Message):
    user_id = message.from_user.id
    
    # Check force subscription
    if not await force_subscribe(client, user_id):
        await message.reply_text(
            f"**Please join our channel first!**\n\n"
            f"Join: @{await get_force_channel_username(client)}\n\n"
            "After joining, send /start again.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{await get_force_channel_username(client)}")
            ]])
        )
        return
    
    # Add user to database
    user_data = {
        'user_id': user_id,
        'username': message.from_user.username,
        'first_name': message.from_user.first_name,
        'last_name': message.from_user.last_name
    }
    db.add_user(user_data)
    
    # Check if message has file parameter
    if len(message.command) > 1:
        file_id = message.command[1]
        await handle_file_download(client, message, file_id)
    else:
        # Show main menu
        is_premium = premium_mgr.is_premium_user(user_id)
        premium_status = "✅ PREMIUM USER" if is_premium else "❌ STANDARD USER"
        
        await message.reply_text(
            f"🎬 **DP Cinema File Store**\n\n"
            f"**Status:** {premium_status}\n\n"
            "**Commands:**\n"
            "/upload - Upload a file\n"
            "/batch - Generate multiple links\n" 
            "/link - Get link of file\n"
            "/myfiles - View your files\n"
            "/addpremium - Add premium (Admin)\n"
            "/removepremium - Remove premium (Admin)\n"
            "/help - Get help\n\n"
            "**Features:**\n"
            "✅ Unlimited file size\n"
            "✅ Unlimited batch processing\n"
            "✅ Token verification\n"
            "✅ Permanent links\n"
            "✅ Auto-delete old files",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("📤 Upload File", callback_data="upload_file"),
                InlineKeyboardButton("📥 My Files", callback_data="my_files")
            ], [
                InlineKeyboardButton("🔄 Batch Process", callback_data="batch_help"),
                InlineKeyboardButton("⭐ Go Premium", callback_data="premium_info")
            ]])
        )

@app.on_message(filters.command("addpremium"))
async def add_premium_command(client, message: Message):
    user_id = message.from_user.id
    
    if user_id not in config.ADMINS:
        await message.reply_text("❌ Admin access required.")
        return
    
    if len(message.command) < 2:
        await message.reply_text("Usage: /addpremium <user_id> [days]\nExample: /addpremium 123456789 30")
        return
    
    try:
        target_user_id = int(message.command[1])
        days = int(message.command[2]) if len(message.command) > 2 else 30
        
        premium_mgr.add_premium_user(target_user_id, days)
        await message.reply_text(f"✅ User {target_user_id} added as premium for {days} days.")
        
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")

@app.on_message(filters.command("removepremium"))
async def remove_premium_command(client, message: Message):
    user_id = message.from_user.id
    
    if user_id not in config.ADMINS:
        await message.reply_text("❌ Admin access required.")
        return
    
    if len(message.command) < 2:
        await message.reply_text("Usage: /removepremium <user_id>\nExample: /removepremium 123456789")
        return
    
    try:
        target_user_id = int(message.command[1])
        premium_mgr.remove_premium_user(target_user_id)
        await message.reply_text(f"✅ User {target_user_id} removed from premium.")
        
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")

@app.on_message(filters.command("batch"))
async def batch_command(client, message: Message):
    # Force subscription check
    if not await force_subscribe(client, message.from_user.id):
        await message.reply_text("Please subscribe to our channel first using /start")
        return
        
    if len(message.command) < 3:
        await message.reply_text(
            "📦 **Batch File Processor**\n\n"
            "Generate multiple file links at once!\n\n"
            "**Usage:**\n"
            "`/batch <first_post_link> <last_post_link>`\n\n"
            "**Example:**\n"
            "`/batch https://t.me/channel/123 https://t.me/channel/145`\n\n"
            "**Requirements:**\n"
            "• Bot must be admin in your channel\n"
            "• No limits on file count or size\n"
            "• Supports all file types"
        )
        return
    
    first_link = message.command[1]
    last_link = message.command[2]
    
    result = await batch_processor.process_batch(client, message, first_link, last_link)
    
    if result is not True:
        await message.reply_text(result)

@app.on_message(filters.command("link"))
async def link_command(client, message: Message):
    # Force subscription check
    if not await force_subscribe(client, message.from_user.id):
        await message.reply_text("Please subscribe to our channel first using /start")
        return
        
    if not message.reply_to_message:
        await message.reply_text(
            "🔗 **Get File Link**\n\n"
            "Reply to a file with this command to get its shareable link.\n\n"
            "**Usage:**\n"
            "1. Send a file to bot\n" 
            "2. Reply to that file with `/link`\n"
            "3. Get permanent shareable link"
        )
        return
    
    replied_message = message.reply_to_message
    user_id = message.from_user.id
    
    # Extract file from replied message
    file_data = await extract_file_from_message(replied_message, user_id)
    
    if not file_data:
        await message.reply_text("❌ No supported file found in the replied message.")
        return
    
    # Save to database
    db.add_file(file_data)
    db.update_user_stats(user_id, uploads=1)
    
    # Generate permanent link
    bot_username = await get_bot_username(client)
    permanent_link = f"https://t.me/{bot_username}?start={file_data['file_id']}"
    
    # Generate blogger page for permanent link
    blogger_page_url = await generate_blogger_page(client, file_data['file_id'], file_data['file_name'], file_data['file_size'])
    
    await message.reply_text(
        f"✅ **Permanent Link Generated!**\n\n"
        f"📁 **File:** {file_data['file_name']}\n"
        f"💾 **Size:** {format_size(file_data['file_size'])}\n\n"
        f"🔗 **Direct Link:**\n`{permanent_link}`\n\n"
        f"🌐 **Blogger Page:**\n{blogger_page_url}\n\n"
        "Share either link to allow downloads with verification.",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔗 Copy Link", callback_data=f"copy_{file_data['file_id']}"),
            InlineKeyboardButton("🌐 Open Page", url=blogger_page_url)
        ]])
    )

@app.on_message(filters.command("myfiles"))
async def myfiles_command(client, message: Message):
    user_id = message.from_user.id
    user_files = db.get_user_files(user_id)
    
    if not user_files:
        await message.reply_text("📭 You haven't uploaded any files yet.")
        return
    
    files_text = "📁 **Your Files**\n\n"
    
    for i, file in enumerate(user_files[:10], 1):
        file_name = file.get('file_name', 'Unknown')
        file_size = file.get('file_size', 0)
        downloads = file.get('download_count', 0)
        file_id = file.get('file_id', 'Unknown')
        
        files_text += f"{i}. **{file_name}**\n"
        files_text += f"   📦 {format_size(file_size)} | 📥 {downloads} downloads\n"
        files_text += f"   🆔 `{file_id}`\n\n"
    
    if len(user_files) > 10:
        files_text += f"📋 ... and {len(user_files) - 10} more files\n\n"
    
    files_text += "Use `/link` command on any file to get its shareable link."
    
    await message.reply_text(files_text)

@app.on_message(filters.command("upload"))
async def upload_command(client, message: Message):
    # Force subscription check
    if not await force_subscribe(client, message.from_user.id):
        await message.reply_text("Please subscribe to our channel first using /start")
        return
        
    await message.reply_text(
        "📤 **Upload a File**\n\n"
        "Simply send me any file and I'll store it permanently!\n\n"
        "**Features:**\n"
        "✅ Unlimited file size\n" 
        "✅ All file types supported\n"
        "✅ Permanent storage\n"
        "✅ Shareable links\n"
        "✅ Download tracking\n\n"
        "Just send any file now..."
    )

# ==================== FILE UPLOAD HANDLER ====================

@app.on_message(filters.document | filters.video | filters.audio | filters.photo)
async def handle_file_upload(client, message: Message):
    user_id = message.from_user.id
    
    # Force subscription check
    if not await force_subscribe(client, user_id):
        await message.reply_text("Please subscribe to our channel first using /start")
        return
    
    # Extract file information
    file_data = await extract_file_from_message(message, user_id)
    
    if not file_data:
        await message.reply_text("❌ Unsupported file type.")
        return
    
    # Save to database
    db.add_file(file_data)
    db.update_user_stats(user_id, uploads=1)
    
    # Generate shareable links
    bot_username = await get_bot_username(client)
    direct_link = f"https://t.me/{bot_username}?start={file_data['file_id']}"
    blogger_page_url = await generate_blogger_page(client, file_data['file_id'], file_data['file_name'], file_data['file_size'])
    
    is_premium = premium_mgr.is_premium_user(user_id)
    premium_badge = " ⭐" if is_premium else ""
    
    await message.reply_text(
        f"✅ **File Uploaded Successfully!**{premium_badge}\n\n"
        f"📁 **File:** {file_data['file_name']}\n"
        f"💾 **Size:** {format_size(file_data['file_size'])}\n"
        f"📊 **Type:** {file_data['mime_type']}\n\n"
        f"🔗 **Direct Link:**\n`{direct_link}`\n\n"
        f"🌐 **Permanent Page:**\n{blogger_page_url}\n\n"
        "Share either link for secure downloads.",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔗 Copy Link", callback_data=f"copy_{file_data['file_id']}"),
            InlineKeyboardButton("🌐 Open Page", url=blogger_page_url)
        ], [
            InlineKeyboardButton("📤 Share", switch_inline_query=file_data['file_id'])
        ]])
    )

# ==================== HELPER FUNCTIONS ====================

async def extract_file_from_message(message, user_id):
    """Extract file data from message"""
    if message.document:
        file = message.document
    elif message.video:
        file = message.video
    elif message.audio:
        file = message.audio
    elif message.photo:
        file = message.photo[-1]  # Largest photo
        file.file_name = f"photo_{file.file_id}.jpg"
        file.mime_type = "image/jpeg"
    else:
        return None
    
    # Generate unique file ID
    import hashlib
    import secrets
    file_id_data = f"{user_id}_{file.file_id}_{int(time.time())}_{secrets.token_urlsafe(8)}"
    unique_file_id = f"FILE_{hashlib.md5(file_id_data.encode()).hexdigest()[:12].upper()}"
    
    return {
        'file_id': unique_file_id,
        'telegram_file_id': file.file_id,
        'file_name': getattr(file, 'file_name', f"file_{file.file_id}"),
        'file_size': file.file_size,
        'mime_type': getattr(file, 'mime_type', 'application/octet-stream'),
        'uploader_id': user_id,
        'message_id': message.id
    }

async def generate_blogger_page(client, file_id, file_name, file_size):
    """Generate blogger page for file"""
    bot_username = await get_bot_username(client)
    page_filename = blogger_gen.save_page(file_id, file_name, file_size, bot_username)
    return f"{config.BLOGGER_BASE_URL}/{page_filename}"

async def get_bot_username(client):
    """Get bot username"""
    global BOT_USERNAME
    if not BOT_USERNAME:
        bot_info = await client.get_me()
        BOT_USERNAME = bot_info.username
        db.set_bot_username(BOT_USERNAME)
    return BOT_USERNAME

async def get_force_channel_username(client):
    """Get force channel username"""
    try:
        chat = await client.get_chat(config.FORCE_SUB_CHANNEL)
        return chat.username if chat.username else str(chat.id).replace('-100', '')
    except:
        return "DpCinemaChannel"

def format_size(size_bytes):
    """Convert bytes to human readable format"""
    if not size_bytes:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.2f} {size_names[i]}"

# ==================== CALLBACK HANDLERS ====================

@app.on_callback_query()
async def handle_callbacks(client, callback_query):
    data = callback_query.data
    user_id = callback_query.from_user.id
    
    if data == "upload_file":
        await callback_query.message.edit_text(
            "📤 **Upload a File**\n\nSimply send me any file now...\n\n"
            "✅ Unlimited size\n✅ All formats\n✅ Permanent storage"
        )
    
    elif data == "my_files":
        user_files = db.get_user_files(user_id)
        if not user_files:
            await callback_query.message.edit_text("📭 You haven't uploaded any files yet.")
            return
        
        files_text = "📁 **Your Files**\n\n"
        for i, file in enumerate(user_files[:5], 1):
            files_text += f"{i}. **{file.get('file_name')}**\n"
            files_text += f"   📦 {format_size(file.get('file_size'))}\n"
            files_text += f"   📥 {file.get('download_count', 0)} downloads\n\n"
        
        await callback_query.message.edit_text(files_text)
    
    elif data.startswith("copy_"):
        file_id = data.split("_")[1]
        await callback_query.answer("Link copied to clipboard!", show_alert=True)

# Start the bot
if __name__ == "__main__":
    logger.info("Starting DP Cinema File Store Bot...")
    app.run()
