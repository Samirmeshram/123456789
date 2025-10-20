async def generate_blogger_page(client, file_id, file_name, file_size):
    """Generate blogger page URL for file"""
    from blogger_generator import BloggerPageGenerator
    
    blogger_gen = BloggerPageGenerator()
    blogger_url = blogger_gen.generate_blogger_url(file_id, file_name, file_size)
    
    return blogger_url

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
    
    # Generate blogger page URL
    blogger_page_url = await generate_blogger_page(
        client, 
        file_data['file_id'], 
        file_data['file_name'], 
        file_data['file_size']
    )
    
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
