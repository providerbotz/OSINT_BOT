#IMPORTING STARTED HERE 
import logging
import asyncio
import aiohttp
import json
import os
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatMember
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    CallbackQueryHandler,
    filters
)
from telegram.error import TelegramError

from config import *
from database import Database #IMPORT END HERE

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize database
db = Database(DATABASE_NAME)

# Add admin to database
db.add_admin(ADMIN_ID)

# Global set to track all chat IDs with persistent storage
ACTIVE_CHATS = set()
ACTIVE_CHATS_FILE = "active_chats.json"

# ==========================================
# PERSISTENT STORAGE FUNCTIONS
# ==========================================

def load_active_chats():
    """Load active chats from file"""
    global ACTIVE_CHATS
    try:
        if os.path.exists(ACTIVE_CHATS_FILE):
            with open(ACTIVE_CHATS_FILE, 'r') as f:
                data = json.load(f)
                ACTIVE_CHATS = set(data)
                logger.info(f"✅ Loaded {len(ACTIVE_CHATS)} active chats from file")
        else:
            logger.info("📝 No active chats file found, starting fresh")
    except Exception as e:
        logger.error(f"Error loading active chats: {e}")
        ACTIVE_CHATS = set()

def save_active_chats():
    """Save active chats to file"""
    try:
        with open(ACTIVE_CHATS_FILE, 'w') as f:
            json.dump(list(ACTIVE_CHATS), f)
        logger.info(f"💾 Saved {len(ACTIVE_CHATS)} active chats to file")
    except Exception as e:
        logger.error(f"Error saving active chats: {e}")

def track_chat(chat_id: int):
    """Track chat ID in global set and save to file"""
    ACTIVE_CHATS.add(chat_id)
    # Save to file every time we track a new chat
    save_active_chats()

# ==========================================
# HELPER FUNCTIONS
# ==========================================

async def is_user_in_channels(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> tuple[bool, str]:
    """Check if user is member of all force join channels"""
    channels = db.get_all_force_channels()
    
    if not channels:
        return True, ""
    
    for channel in channels:
        try:
            channel_id = channel["channel_id"]
            if not channel_id.startswith("-"):
                channel_id = f"-{channel_id}"
            
            member = await context.bot.get_chat_member(channel_id, user_id)
            
            if member.status not in [ChatMember.MEMBER, ChatMember.ADMINISTRATOR, ChatMember.OWNER]:
                return False, channel["invite_link"]
        except Exception as e:
            logger.error(f"Error checking membership: {e}")
            continue
    
    return True, ""

async def fetch_api(url: str) -> str:
    """Fetch API response"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=5) as response:
                if response.status == 200:
                    # Return raw response as text
                    return await response.text()
                else:
                    return None
    except Exception as e:
        logger.error(f"API Error: {e}")
        return None

def remove_duplicates(data):
    """Remove exact duplicate entries from list/dict while keeping unique ones"""
    if isinstance(data, list):
        seen = []
        unique_data = []
        
        for item in data:
            # Convert item to string for comparison (ignoring _id field)
            if isinstance(item, dict):
                # Create a copy without _id for comparison
                item_copy = {k: v for k, v in item.items() if k != '_id'}
                item_str = json.dumps(item_copy, sort_keys=True)
            else:
                item_str = str(item)
            
            # Only add if not seen before
            if item_str not in seen:
                seen.append(item_str)
                unique_data.append(item)
        
        return unique_data
    return data

def format_json_response(raw_response: str) -> str:
    """Format response as pretty JSON with duplicate removal"""
    try:
        # Try to parse as JSON
        json_data = json.loads(raw_response)
        
        # Remove duplicates if it's a list
        if isinstance(json_data, list):
            json_data = remove_duplicates(json_data)
        
        # Pretty format with indent
        pretty_json = json.dumps(json_data, indent=2, ensure_ascii=False)
        return f"```json{chr(10)}{pretty_json}{chr(10)}```"
    except:
        # If not JSON, return as code block
        return f"```{chr(10)}{raw_response}{chr(10)}```"

def is_group_chat(update: Update) -> bool:
    """Check if message is from group"""
    return update.effective_chat.type in ["group", "supergroup"]

async def notify_admin_new_user(context: ContextTypes.DEFAULT_TYPE, user_id: int, username: str, first_name: str):
    """Notify admin about new user"""
    try:
        message = f"👤 New User Alert!{chr(10)}{chr(10)}"
        message += f"User ID: `{user_id}`{chr(10)}"
        message += f"Username: @{username if username else 'None'}{chr(10)}"
        message += f"Name: {first_name}{chr(10)}"
        message += f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        await context.bot.send_message(ADMIN_ID, message, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Failed to notify admin: {e}")

async def notify_admin_bot_added(context: ContextTypes.DEFAULT_TYPE, chat_id: int, chat_title: str, added_by: int):
    """Notify admin when bot is added to group"""
    try:
        message = f"🎉 Bot Added to New Group!{chr(10)}{chr(10)}"
        message += f"Group ID: `{chat_id}`{chr(10)}"
        message += f"Group Name: {chat_title}{chr(10)}"
        message += f"Added By: {added_by}{chr(10)}"
        message += f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        await context.bot.send_message(ADMIN_ID, message, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Failed to notify admin: {e}")

# ==========================================
# COMMAND HANDLERS
# ==========================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    chat_id = update.effective_chat.id
    
    # Track this chat
    track_chat(chat_id)
    
    # Check if user exists in database
    existing_user = db.get_user(user.id)
    
    # Add user to database
    db.add_user(user.id, user.username, user.first_name)
    
    # Notify admin about new user (only first time)
    if not existing_user:
        await notify_admin_new_user(context, user.id, user.username, user.first_name)
    
    # Check if in private DM with admin
    if update.effective_chat.type == "private" and user.id == ADMIN_ID:
        # Show admin panel
        keyboard = []
        for row in ADMIN_PANEL_BUTTONS:
            keyboard.append([InlineKeyboardButton(btn, callback_data=f"admin_{btn}") for btn in row])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(ADMIN_PANEL_MESSAGE, reply_markup=reply_markup)
        return
    
    # Check if in group
    if not is_group_chat(update):
        await update.message.reply_text(NOT_IN_GROUP_MESSAGE)
        return
    
    # Track this group
    db.add_group(
        update.effective_chat.id,
        update.effective_chat.title,
        update.effective_chat.type
    )
    
    await update.message.reply_text(WELCOME_MESSAGE)

async def handle_search_command(update: Update, context: ContextTypes.DEFAULT_TYPE, command: str):
    """Generic handler for all search commands"""
    user = update.effective_user
    chat_id = update.effective_chat.id
    
    # Track this chat
    track_chat(chat_id)
    
    # Check if in group
    if not is_group_chat(update):
        await update.message.reply_text(NOT_IN_GROUP_MESSAGE)
        return
    
    # Check maintenance mode
    if db.is_maintenance_mode() and user.id != ADMIN_ID:
        await update.message.reply_text(MAINTENANCE_MODE_MESSAGE)
        return
    
    # Check blacklist
    if db.is_blacklisted(user.id):
        await update.message.reply_text(BLACKLISTED_MESSAGE)
        return
    
    # Check force join
    is_member, invite_link = await is_user_in_channels(user.id, context)
    if not is_member:
        await update.message.reply_text(FORCE_JOIN_MESSAGE.format(channel_link=invite_link))
        return
    
    # Check rate limit
    can_request, seconds_left = db.check_rate_limit(user.id, RATE_LIMIT_SECONDS)
    if not can_request:
        await update.message.reply_text(RATE_LIMIT_MESSAGE.format(seconds=seconds_left))
        return
    
    # Get query
    if not context.args:
        example = COMMAND_EXAMPLES.get(command, "value")
        error_msg = f"❌ Missing Query!{chr(10)}{chr(10)}"
        error_msg += f"Please provide the required information.{chr(10)}{chr(10)}"
        error_msg += f"📝 Example:{chr(10)}`/{command} {example}`"
        await update.message.reply_text(error_msg, parse_mode="Markdown")
        return
    
    query = " ".join(context.args)
    
    # Send processing message
    processing_msg = await update.message.reply_text(PROCESSING_MESSAGE)
    
    # Get API URL
    api_url = API_ENDPOINTS.get(command)
    if not api_url:
        await processing_msg.edit_text(f"⚠️ This feature is under maintenance!{chr(10)}Contact: {SUPPORT_USERNAME}")
        return
    
    # Format URL with query
    final_url = api_url.format(query=query)
    
    # Fetch API response
    response = await fetch_api(final_url)
    
    if response:
        # Log search
        db.log_search(
            user_id=user.id,
            username=user.username or "Unknown",
            group_id=update.effective_chat.id,
            group_name=update.effective_chat.title or "Unknown",
            command=command,
            query=query,
            success=True
        )
        
        # Update rate limit
        db.update_rate_limit(user.id)
        
        # Format response as pretty JSON
        formatted_response = format_json_response(response)
        
        # Create inline buttons
        keyboard = [
            [InlineKeyboardButton("➕ Add me to your group", url="https://t.me/ProviderOSINTBot?startgroup=true")],
            [InlineKeyboardButton("💬 Use me here", url="https://t.me/")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Send response with buttons
        await processing_msg.edit_text(
            f"✅ Result:{chr(10)}{chr(10)}{formatted_response}",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
        
        # Notify admin about search
        try:
            admin_notif = f"🔍 Search Alert{chr(10)}{chr(10)}"
            admin_notif += f"User: @{user.username or 'None'} ({user.id}){chr(10)}"
            admin_notif += f"Command: /{command}{chr(10)}"
            admin_notif += f"Query: {query}{chr(10)}"
            admin_notif += f"Group: {update.effective_chat.title}"
            await context.bot.send_message(ADMIN_ID, admin_notif)
        except:
            pass
    else:
        # Log failed search
        db.log_search(
            user_id=user.id,
            username=user.username or "Unknown",
            group_id=update.effective_chat.id,
            group_name=update.effective_chat.title or "Unknown",
            command=command,
            query=query,
            success=False
        )
        
        await processing_msg.edit_text(ERROR_MESSAGE)

# Individual command handlers
async def num_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await handle_search_command(update, context, "num")

async def aadhar_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await handle_search_command(update, context, "aadhar")

async def email_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await handle_search_command(update, context, "email")

async def familyinfo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await handle_search_command(update, context, "familyinfo")

async def dlinfo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await handle_search_command(update, context, "dlinfo")

async def vehicle_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await handle_search_command(update, context, "vehicle")

async def fastag_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await handle_search_command(update, context, "fastag")

async def vnum_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await handle_search_command(update, context, "vnum")

async def pak_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await handle_search_command(update, context, "pak")

async def cnic_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await handle_search_command(update, context, "cnic")

async def ration_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await handle_search_command(update, context, "ration")

async def upi2num_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await handle_search_command(update, context, "upi2num")

async def upiinfo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await handle_search_command(update, context, "upiinfo")

async def ifsc_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await handle_search_command(update, context, "ifsc")

async def emei_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await handle_search_command(update, context, "emei")

# New command handlers
async def tginfo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await handle_search_command(update, context, "tginfo")

async def tg2num_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await handle_search_command(update, context, "tg2num")

async def ip_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await handle_search_command(update, context, "ip")

async def ffinfo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await handle_search_command(update, context, "ffinfo")

async def fb2num_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await handle_search_command(update, context, "fb2num")

async def bomber_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await handle_search_command(update, context, "bomber")

# Business/Support Commands (DM Contact)
async def dm_contact_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle commands that need DM contact"""
    await update.message.reply_text(DM_CONTACT_MESSAGE)

# ==========================================
# ADMIN COMMANDS
# ==========================================

async def addchannel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add force join channel - Admin only"""
    user = update.effective_user
    
    if not db.is_admin(user.id):
        return
    
    if len(context.args) < 2:
        await update.message.reply_text(
            f"❌ Usage: /addchannel <invite_link> <channel_id>{chr(10)}{chr(10)}"
            f"Example: /addchannel https://t.me/yourchannel -1001234567890"
        )
        return
    
    invite_link = context.args[0]
    channel_id = context.args[1]
    
    if db.add_force_channel(channel_id, invite_link):
        await update.message.reply_text(f"✅ Channel added successfully!{chr(10)}{chr(10)}Channel ID: {channel_id}")
    else:
        await update.message.reply_text(f"⚠️ Channel already exists!")

async def delchannel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove force join channel - Admin only"""
    user = update.effective_user
    
    if not db.is_admin(user.id):
        return
    
    if not context.args:
        await update.message.reply_text(f"❌ Usage: /delchannel <channel_id>")
        return
    
    channel_id = context.args[0]
    db.remove_force_channel(channel_id)
    await update.message.reply_text(f"✅ Channel removed successfully!")

async def listchannels_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all force join channels - Admin only"""
    user = update.effective_user
    
    if not db.is_admin(user.id):
        return
    
    channels = db.get_all_force_channels()
    
    if not channels:
        await update.message.reply_text(f"📋 No force join channels added yet.")
        return
    
    message = f"📋 Force Join Channels:{chr(10)}{chr(10)}"
    for idx, channel in enumerate(channels, 1):
        message += f"{idx}. Channel ID: {channel['channel_id']}{chr(10)}"
        message += f"   Link: {channel['invite_link']}{chr(10)}{chr(10)}"
    
    await update.message.reply_text(message)

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show bot statistics - Admin only"""
    user = update.effective_user
    
    if not db.is_admin(user.id):
        return
    
    total_users = len(db.get_all_users())
    total_searches = db.get_total_searches()
    command_stats = db.get_command_stats()
    
    message = f"📊 Bot Statistics{chr(10)}{chr(10)}"
    message += f"👥 Total Users: {total_users}{chr(10)}"
    message += f"🔍 Total Searches: {total_searches}{chr(10)}"
    message += f"💬 Active Chats (Saved): {len(ACTIVE_CHATS)}{chr(10)}{chr(10)}"
    message += f"📈 Command Usage:{chr(10)}"
    
    for cmd, count in list(command_stats.items())[:10]:
        message += f"  /{cmd}: {count} searches{chr(10)}"
    
    await update.message.reply_text(message)

async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Broadcast message to all users and groups - Admin only - Works without database"""
    user = update.effective_user
    
    if not db.is_admin(user.id):
        return
    
    # Get the full message text after /broadcast command
    if update.message.text:
        # Remove the /broadcast command and get remaining text with line breaks preserved
        broadcast_text = update.message.text.replace('/broadcast', '', 1).strip()
    else:
        broadcast_text = ""
    
    if not broadcast_text:
        await update.message.reply_text(
            f"❌ Usage: /broadcast <message>{chr(10)}{chr(10)}"
            f"This will send message to ALL users and groups."
        )
        return
    
    # Get chat IDs from database and active chats
    try:
        chat_ids = db.get_all_chat_ids()
    except:
        chat_ids = []
    
    # Merge with active chats (from file)
    all_chat_ids = set(chat_ids) | ACTIVE_CHATS
    
    status_msg = await update.message.reply_text(
        f"📢 Broadcasting...{chr(10)}"
        f"Total chats: {len(all_chat_ids)}{chr(10)}"
        f"(DB: {len(chat_ids)} + Saved: {len(ACTIVE_CHATS)}){chr(10)}{chr(10)}"
        f"Please wait..."
    )
    
    success = 0
    failed = 0
    
    for chat_id in all_chat_ids:
        try:
            await context.bot.send_message(chat_id, broadcast_text)
            success += 1
            await asyncio.sleep(0.05)  # Rate limit prevention
        except Exception as e:
            failed += 1
            logger.error(f"Broadcast failed for {chat_id}: {e}")
    
    await status_msg.edit_text(
        f"✅ Broadcast Complete!{chr(10)}{chr(10)}"
        f"📤 Sent: {success}{chr(10)}"
        f"❌ Failed: {failed}"
    )

async def blacklist_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Blacklist a user - Admin only"""
    user = update.effective_user
    
    if not db.is_admin(user.id):
        return
    
    if not context.args:
        await update.message.reply_text(f"❌ Usage: /blacklist <user_id>")
        return
    
    target_id = int(context.args[0])
    db.blacklist_user(target_id)
    await update.message.reply_text(f"✅ User {target_id} has been blacklisted!")

async def unblacklist_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove user from blacklist - Admin only"""
    user = update.effective_user
    
    if not db.is_admin(user.id):
        return
    
    if not context.args:
        await update.message.reply_text(f"❌ Usage: /unblacklist <user_id>")
        return
    
    target_id = int(context.args[0])
    db.unblacklist_user(target_id)
    await update.message.reply_text(f"✅ User {target_id} has been removed from blacklist!")

async def notify_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send notification to all users and groups - Admin only - Works without database"""
    user = update.effective_user
    
    if not db.is_admin(user.id):
        return
    
    # Get the full message text after /notify command
    if update.message.text:
        # Remove the /notify command and get remaining text with line breaks preserved
        notification_text = update.message.text.replace('/notify', '', 1).strip()
    else:
        notification_text = ""
    
    if not notification_text:
        await update.message.reply_text(
            f"❌ Usage: /notify <message>{chr(10)}{chr(10)}"
            f"Sends formatted notification to all users and groups."
        )
        return
    
    formatted_message = f"🔔 NOTIFICATION{chr(10)}{chr(10)}{notification_text}{chr(10)}{chr(10)}— {SUPPORT_USERNAME}"
    
    # Get chat IDs from database and active chats
    try:
        chat_ids = db.get_all_chat_ids()
    except:
        chat_ids = []
    
    # Merge with active chats (from file)
    all_chat_ids = set(chat_ids) | ACTIVE_CHATS
    
    status_msg = await update.message.reply_text(
        f"🔔 Sending notifications...{chr(10)}"
        f"Total chats: {len(all_chat_ids)}{chr(10)}"
        f"(DB: {len(chat_ids)} + Saved: {len(ACTIVE_CHATS)}){chr(10)}{chr(10)}"
        f"Please wait..."
    )
    
    success = 0
    failed = 0
    
    for chat_id in all_chat_ids:
        try:
            await context.bot.send_message(chat_id, formatted_message)
            success += 1
            await asyncio.sleep(0.05)
        except Exception as e:
            failed += 1
    
    await status_msg.edit_text(
        f"✅ Notification Sent!{chr(10)}{chr(10)}"
        f"📤 Success: {success}{chr(10)}"
        f"❌ Failed: {failed}"
    )

# ==========================================
# ADMIN PANEL CALLBACK HANDLERS
# ==========================================

async def admin_panel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle admin panel button callbacks"""
    query = update.callback_query
    await query.answer()
    
    user = query.from_user
    
    # Check if admin
    if user.id != ADMIN_ID:
        await query.answer("⛔ Access Denied!", show_alert=True)
        return
    
    button_text = query.data.replace("admin_", "")
    
    # Statistics
    if button_text == "📊 Statistics":
        total_users = len(db.get_all_users())
        total_searches = db.get_total_searches()
        command_stats = db.get_command_stats()
        
        message = f"📊 Bot Statistics{chr(10)}{chr(10)}"
        message += f"👥 Total Users: {total_users}{chr(10)}"
        message += f"🔍 Total Searches: {total_searches}{chr(10)}"
        message += f"💬 Active Chats (Saved): {len(ACTIVE_CHATS)}{chr(10)}{chr(10)}"
        message += f"📈 Top Commands:{chr(10)}"
        
        for cmd, count in list(command_stats.items())[:10]:
            message += f"  /{cmd}: {count}{chr(10)}"
        
        await query.edit_message_text(message)
        
        # Back button
        keyboard = [[InlineKeyboardButton("🔙 Back to Panel", callback_data="admin_back")]]
        await query.edit_message_reply_markup(InlineKeyboardMarkup(keyboard))
    
    # User List
    elif button_text == "👥 User List":
        users = db.get_all_users()[:20]  # First 20 users
        
        message = f"👥 User List (Top 20){chr(10)}{chr(10)}"
        for idx, user_data in enumerate(users, 1):
            message += f"{idx}. @{user_data['username'] or 'None'} ({user_data['user_id']}){chr(10)}"
            message += f"   Searches: {user_data['total_searches']}{chr(10)}"
        
        await query.edit_message_text(message)
        keyboard = [[InlineKeyboardButton("🔙 Back to Panel", callback_data="admin_back")]]
        await query.edit_message_reply_markup(InlineKeyboardMarkup(keyboard))
    
    # Broadcast
    elif button_text == "📢 Broadcast":
        message = f"📢 Broadcast Message{chr(10)}{chr(10)}"
        message += f"To broadcast, use:{chr(10)}"
        message += f"`/broadcast Your message here`{chr(10)}{chr(10)}"
        message += f"This will send to all users."
        
        await query.edit_message_text(message, parse_mode="Markdown")
        keyboard = [[InlineKeyboardButton("🔙 Back to Panel", callback_data="admin_back")]]
        await query.edit_message_reply_markup(InlineKeyboardMarkup(keyboard))
    
    # Notification
    elif button_text == "🔔 Notification":
        message = f"🔔 Send Notification{chr(10)}{chr(10)}"
        message += f"To send notification, use:{chr(10)}"
        message += f"`/notify Your notification here`{chr(10)}{chr(10)}"
        message += f"Formatted with emoji."
        
        await query.edit_message_text(message, parse_mode="Markdown")
        keyboard = [[InlineKeyboardButton("🔙 Back to Panel", callback_data="admin_back")]]
        await query.edit_message_reply_markup(InlineKeyboardMarkup(keyboard))
    
    # Blacklist
    elif button_text == "🚫 Blacklist User":
        message = f"🚫 Blacklist User{chr(10)}{chr(10)}"
        message += f"To blacklist, use:{chr(10)}"
        message += f"`/blacklist user_id`{chr(10)}{chr(10)}"
        message += f"Example: `/blacklist 123456789`"
        
        await query.edit_message_text(message, parse_mode="Markdown")
        keyboard = [[InlineKeyboardButton("🔙 Back to Panel", callback_data="admin_back")]]
        await query.edit_message_reply_markup(InlineKeyboardMarkup(keyboard))
    
    # Unblacklist
    elif button_text == "✅ Unblacklist User":
        message = f"✅ Remove from Blacklist{chr(10)}{chr(10)}"
        message += f"To unblacklist, use:{chr(10)}"
        message += f"`/unblacklist user_id`"
        
        await query.edit_message_text(message, parse_mode="Markdown")
        keyboard = [[InlineKeyboardButton("🔙 Back to Panel", callback_data="admin_back")]]
        await query.edit_message_reply_markup(InlineKeyboardMarkup(keyboard))
    
    # Force Channels
    elif button_text == "📺 Force Channels":
        channels = db.get_all_force_channels()
        
        if not channels:
            message = f"📺 Force Join Channels{chr(10)}{chr(10)}No channels added yet."
        else:
            message = f"📺 Force Join Channels{chr(10)}{chr(10)}"
            for idx, ch in enumerate(channels, 1):
                message += f"{idx}. ID: {ch['channel_id']}{chr(10)}"
                message += f"   Link: {ch['invite_link']}{chr(10)}{chr(10)}"
        
        message += f"{chr(10)}Commands:{chr(10)}"
        message += f"`/addchannel <link> <id>`{chr(10)}"
        message += f"`/delchannel <id>`"
        
        await query.edit_message_text(message, parse_mode="Markdown")
        keyboard = [[InlineKeyboardButton("🔙 Back to Panel", callback_data="admin_back")]]
        await query.edit_message_reply_markup(InlineKeyboardMarkup(keyboard))
    
    # Search Logs
    elif button_text == "📋 Search Logs":
        message = f"📋 Recent Search Logs{chr(10)}{chr(10)}"
        message += f"View with: `/stats`{chr(10)}{chr(10)}"
        message += f"Database: `debax_bot.db`{chr(10)}"
        message += f"Table: `search_logs`"
        
        await query.edit_message_text(message, parse_mode="Markdown")
        keyboard = [[InlineKeyboardButton("🔙 Back to Panel", callback_data="admin_back")]]
        await query.edit_message_reply_markup(InlineKeyboardMarkup(keyboard))
    
    # Maintenance Mode Toggle
    elif button_text == "🔧 Maintenance Mode":
        current_mode = db.is_maintenance_mode()
        
        # Toggle mode
        db.set_maintenance_mode(not current_mode)
        new_mode = db.is_maintenance_mode()
        
        if new_mode:
            message = f"🔧 Maintenance Mode: ON ✅{chr(10)}{chr(10)}"
            message += f"Bot is now in maintenance mode.{chr(10)}"
            message += f"Users cannot use any commands except /start.{chr(10)}{chr(10)}"
            message += f"Click again to turn OFF."
        else:
            message = f"🔧 Maintenance Mode: OFF ❌{chr(10)}{chr(10)}"
            message += f"Bot is now operational.{chr(10)}"
            message += f"Users can use all commands.{chr(10)}{chr(10)}"
            message += f"Click again to turn ON."
        
        await query.edit_message_text(message)
        keyboard = [[InlineKeyboardButton("🔙 Back to Panel", callback_data="admin_back")]]
        await query.edit_message_reply_markup(InlineKeyboardMarkup(keyboard))
    
    # Back or Refresh
    elif button_text in ["🔄 Refresh Panel", "back"]:
        keyboard = []
        for row in ADMIN_PANEL_BUTTONS:
            keyboard.append([InlineKeyboardButton(btn, callback_data=f"admin_{btn}") for btn in row])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(ADMIN_PANEL_MESSAGE, reply_markup=reply_markup)

# ==========================================
# NEW MEMBER HANDLER (BOT ADDED TO GROUP)
# ==========================================

async def handle_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle when bot is added to group"""
    for member in update.message.new_chat_members:
        if member.id == context.bot.id:
            # Track this chat
            track_chat(update.effective_chat.id)
            
            # Bot was added to group - save to database
            db.add_group(
                update.effective_chat.id,
                update.effective_chat.title,
                update.effective_chat.type
            )
            
            # Notify admin
            await notify_admin_bot_added(
                context,
                update.effective_chat.id,
                update.effective_chat.title,
                update.message.from_user.id
            )
            
            # Send welcome message
            await update.message.reply_text(
                f"🎉 Thanks for adding me!{chr(10)}{chr(10)}"
                f"Use /start to see all commands.{chr(10)}{chr(10)}"
                f"⚡ Powered by: {SUPPORT_USERNAME}"
            )

# ==========================================
# MESSAGE HANDLER (Track all messages)
# ==========================================

async def track_all_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Track all chats where bot receives messages"""
    if update.effective_chat:
        track_chat(update.effective_chat.id)

# ==========================================
# ERROR HANDLER
# ==========================================

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log errors"""
    logger.error(f"Update {update} caused error {context.error}")

# ==========================================
# MAIN FUNCTION
# ==========================================

def main():
    """Start the bot"""
    print("🚀 Starting Provider OSINT Bot...")
    
    # Load active chats from file
    load_active_chats()
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Command handlers
    application.add_handler(CommandHandler("start", start_command))
    
    # Search commands
    application.add_handler(CommandHandler("num", num_command))
    application.add_handler(CommandHandler("aadhar", aadhar_command))
    application.add_handler(CommandHandler("email", email_command))
    application.add_handler(CommandHandler("familyinfo", familyinfo_command))
    application.add_handler(CommandHandler("dlinfo", dlinfo_command))
    application.add_handler(CommandHandler("vehicle", vehicle_command))
    application.add_handler(CommandHandler("fastag", fastag_command))
    application.add_handler(CommandHandler("vnum", vnum_command))
    application.add_handler(CommandHandler("pak", pak_command))
    application.add_handler(CommandHandler("cnic", cnic_command))
    application.add_handler(CommandHandler("ration", ration_command))
    application.add_handler(CommandHandler("upi2num", upi2num_command))
    application.add_handler(CommandHandler("upiinfo", upiinfo_command))
    application.add_handler(CommandHandler("ifsc", ifsc_command))
    application.add_handler(CommandHandler("emei", emei_command))
    
    # New command handlers
    application.add_handler(CommandHandler("tginfo", tginfo_command))
    application.add_handler(CommandHandler("tg2num", tg2num_command))
    application.add_handler(CommandHandler("ip", ip_command))
    application.add_handler(CommandHandler("ffinfo", ffinfo_command))
    application.add_handler(CommandHandler("fb2num", fb2num_command))
    application.add_handler(CommandHandler("bomber", bomber_command))

    # Business/Support commands (DM contact)
    application.add_handler(CommandHandler("protectnum", dm_contact_commands))
    application.add_handler(CommandHandler("protectaadhar", dm_contact_commands))
    application.add_handler(CommandHandler("donate", dm_contact_commands))
    application.add_handler(CommandHandler("support", dm_contact_commands))
    application.add_handler(CommandHandler("makebot", dm_contact_commands))
    application.add_handler(CommandHandler("buyapi", dm_contact_commands))
    application.add_handler(CommandHandler("buydb", dm_contact_commands))
    
    # Admin commands
    application.add_handler(CommandHandler("addchannel", addchannel_command))
    application.add_handler(CommandHandler("delchannel", delchannel_command))
    application.add_handler(CommandHandler("listchannels", listchannels_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("broadcast", broadcast_command))
    application.add_handler(CommandHandler("blacklist", blacklist_command))
    application.add_handler(CommandHandler("unblacklist", unblacklist_command))
    application.add_handler(CommandHandler("notify", notify_command))
    
    # Admin panel callback handler
    application.add_handler(CallbackQueryHandler(admin_panel_callback, pattern="^admin_"))
    
    # New member handler (bot added to group)
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, handle_new_member))
    
    # Track all messages to capture chat IDs
    application.add_handler(MessageHandler(filters.ALL, track_all_messages), group=999)
    
    # Error handler
    application.add_error_handler(error_handler)
    
    # Start bot
    print("✅ Bot is running!")
    print(f"Admin ID: {ADMIN_ID}")
    print(f"Support: {SUPPORT_USERNAME}")
    print(f"💾 Active Chats Loaded: {len(ACTIVE_CHATS)}")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
