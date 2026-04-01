# 🚀 PROVIDER OSINT BOT - SETUP GUIDE

## 📦 Files Included:
1. `bot.py` - Main bot file
2. `config.py` - Configuration (APIs, messages, settings)
3. `database.py` - Database operations
4. `requirements.txt` - Python dependencies
5. `README.md` - This file

---

## 🔧 Installation Steps:

### 1. Upload to VPS
Upload all files to your VPS in a folder (e.g., `/root/provide_bot/`)

### 2. Install Python & Dependencies
```bash
# Install Python 3.10+ (if not installed)
sudo apt update
sudo apt install python3 python3-pip -y

# Navigate to bot folder
cd /root/provider_bot/

# Install requirements
pip3 install -r requirements.txt
```

### 3. Configure APIs
Open `config.py` and edit the API URLs:
```bash
nano config.py
```

**Replace these URLs with your actual APIs:**
```python
API_ENDPOINTS = {
    "num": "http://18.213.0.140:8000/search?mobile={query}",  # Already set
    "aadhar": "http://YOUR_API_URL/aadhar?number={query}",     # CHANGE THIS
    "email": "http://YOUR_API_URL/email?email={query}",        # CHANGE THIS
    # ... and so on for all commands
}
```

**Save:** Press `CTRL+X`, then `Y`, then `ENTER`

### 4. Run the Bot

**Option A: Direct Run (Testing)**
```bash
python3 bot.py
```

**Option B: Background Run (Production)**
```bash
nohup python3 bot.py > bot.log 2>&1 &
```

**Option C: Using Screen (Recommended)**
```bash
# Install screen
sudo apt install screen -y

# Create new screen session
screen -S provider_bot

# Run bot
python3 bot.py

# Detach: Press CTRL+A then D
# Reattach: screen -r provider_bot
```

**Option D: Using PM2 (Best for Production)**
```bash
# Install PM2
sudo npm install -g pm2

# Start bot
pm2 start bot.py --name provider_bot --interpreter python3

# Auto-restart on system reboot
pm2 startup
pm2 save

# Useful PM2 commands:
pm2 logs provider_bot    # View logs
pm2 restart provider_bot # Restart bot
pm2 stop provider_bot    # Stop bot
pm2 status            # Check status
```

---

## ⚙️ Bot Configuration

### Admin Commands (Only for User ID: 6987518006)

**Force Channel Management:**
```
/addchannel <invite_link> <channel_id>
Example: /addchannel https://t.me/yourchannel -1001234567890

/delchannel <channel_id>
/listchannels
```

**User Management:**
```
/blacklist <user_id>    - Ban user from bot
/unblacklist <user_id>  - Remove ban
/stats                  - View bot statistics
```

**Broadcasting:**
```
/broadcast <message>    - Send message to all users
/notify <message>       - Send formatted notification
```

### User Commands (Work in Groups Only)

**OSINT Commands:**
```
/start              - Show menu
/num 9876543210     - Mobile number lookup
/aadhar 123456789012 - Aadhaar lookup
/email test@email.com - Email breach check
... and 11 more commands
```

**Support Commands:**
```
/protectnum
/protectaadhar
/donate
/support
/makebot
/buyapi
/buydb
```
*These will show contact message: @TrustedXDeal*

---

## 📊 Database

The bot automatically creates `provider_bot.db` (SQLite) with these tables:
- **users** - User information & stats
- **force_channels** - Force join channels
- **search_logs** - All search history
- **admins** - Admin list
- **rate_limits** - Spam prevention
- **settings** - Bot configuration

**Location:** Same folder as bot.py

---

## 🔐 Security Features

1. **Rate Limiting:** 30 seconds between searches (configurable in config.py)
2. **Blacklist System:** Ban abusive users
3. **Force Join:** Users must join channels before using bot
4. **Group Only:** Bot won't work in private DMs
5. **Admin Protection:** Only authorized admin can use admin commands

---

## 🛠️ Customization

### Change Rate Limit:
Edit in `config.py`:
```python
RATE_LIMIT_SECONDS = 30  # Change to desired seconds
```

### Change Messages:
All messages are in `config.py` - edit them as needed!

### Add More Admins:
Edit `bot.py`, line 26:
```python
db.add_admin(ADMIN_ID)
db.add_admin(YOUR_NEW_ADMIN_ID)  # Add this line
```

---

## 📝 Testing Checklist

1. ✅ Add bot to a group
2. ✅ Send `/start` - Check if menu appears
3. ✅ Try `/num 9876543210` - Should ask to join channel (if force join enabled)
4. ✅ Add channel: `/addchannel https://t.me/yourchannel -1001234567890`
5. ✅ Join channel and try command again - Should work
6. ✅ Test admin commands: `/stats`, `/listchannels`
7. ✅ Test blacklist: `/blacklist <user_id>`
8. ✅ Test broadcast: `/broadcast Hello everyone!`

---

## 🐛 Troubleshooting

**Bot not responding?**
- Check if bot.py is running: `ps aux | grep bot.py`
- Check logs: `tail -f bot.log` or `pm2 logs provider_bot`

**API not working?**
- Verify API URLs in config.py
- Test API manually: `curl "YOUR_API_URL"`

**Force join not working?**
- Ensure channel ID starts with `-100` (for supergroups)
- Bot must be admin in channel to check membership
- Use correct invite link

**Database errors?**
- Delete `provider_bot.db` and restart bot (fresh database)

---

## 📞 Support

Contact: @Providerbotz

---

## 🎯 Quick Start Commands

```bash
# After uploading files to VPS:
cd /root/debax_bot/
pip3 install -r requirements.txt
nano config.py  # Edit API URLs
python3 bot.py  # Test run

# If working fine, use PM2:
pm2 start bot.py --name provider_bot --interpreter python3
pm2 save
```

---

## ✨ Features Summary

✅ Force Channel Join System
✅ User Tracking & Analytics
✅ Rate Limiting & Anti-Spam
✅ Blacklist System
✅ Broadcast & Notifications
✅ Admin Panel
✅ Group-Only Operations
✅ SQLite Database
✅ 14 OSINT Commands
✅ Error Handling
✅ Logging System

---

**Bot developed for @ProviderBot**
**Powered by PROVIDER OSINT**

🛡️ Use Responsibly | Respect Privacy | Stay Safe
