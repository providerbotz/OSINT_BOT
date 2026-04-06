# ==========================================
# PROVIDERBOTZ OSINT BOT - CONFIGURATION FILE
# ==========================================
# Edit kar sakte ho easily - Sab URLs yaha hain
# ==========================================

# Bot Token
BOT_TOKEN = "ENTER_BOT_TOKEN" #DONT PASTE HERE 

# Admin User ID
ADMIN_ID = 7931847651 

# Support Contact
SUPPORT_USERNAME = "@" # YOUR USERNAME/ANY FRIEND USERNAME 

# ==========================================
# API ENDPOINTS - ENTER UR API IF U DONT NEED THIS 
# ==========================================

# PASTE YOUR ACTUAL APIS
API_ENDPOINTS = {

    # 📱 Indian Number Info
    "num": "https://dev-dark.vercel.app/api/phone-info?phone={query}&format=clean",

    # 🆔 Aadhaar
    "aadhar": "https://akash-addhar-info-api.vercel.app/search?aadharNumber={query}",

    # 📞 Call Trace
    "calltrace": "https://ab-calltraceapi.vercel.app/info?number={query}",

    # 🇵🇰 Pakistan SIM
    "pak": "https://blacksimdetail.vercel.app/public_apis/simdetailsapi.php?num={query}",

    # 🪪 PAN Card
    "pan": "https://pan2info-shatirownerrr.vercel.app/pan?key=demo&term={query}",

    # 💳 BIN Lookup
    "bin": "https://bin-info-ashy.vercel.app/bin/{query}",

    # 📮 PIN Code
    "pincode": "https://api.postalpincode.in/pincode/{query}",

    # 🌦 Weather
    "weather": "https://isalhacker.great-site.net/weather.php?location={query}",

    # 🌐 IP Info
    "ip": "http://ip-api.com/json/{query}",

    # 📱 Global Phone Info
    "pinfo": "https://api.yabes-desu.workers.dev/tools/phone-info?number={query}",

    # 📸 Instagram User
    "instagram": "https://akash-insta-info-api.vercel.app/api/insta?u={query}",

    # 🎮 Free Fire
    "ffinfo": "https://ff-info-deba.vercel.app/accinfo?uid={query}&key=DEBA",

    # 💬 Telegram User
    "tginfo": "https://akashhacker.gt.tc/telegram.php?username={query}",

    # 🧾 GST
    "gst": "https://osint-info.great-site.net/api/gst_lookup.php?gstNumber={query}",

    # 🚗 RC Info
    "rc": "https://reseller-host.vercel.app/api/rc?number={query}"
}

# ==========================================
# RATE LIMITING SETTINGS
# ==========================================
RATE_LIMIT_SECONDS = 5  # Har search ke beech minimum gap
MAX_SEARCHES_PER_DAY = 200  # Per user daily limit (optional) UPTO 1000 OTHERWISE BOT SLEEP WELL. .

# ==========================================
# DATABASE SETTINGS
# ==========================================
DATABASE_NAME = "provider_bot.db"  #NO NEED TO CHANGE

# ===========================================================
# MESSAGES - CUSTOMIZE KAR SAKTE HO WELCOME MESSAGE HAIN YE 
# ===========================================================

WELCOME_MESSAGE = f"""🚀 Welcome to Provider OSINT 🚀{chr(10)}{chr(10)}
📊 Daily Free Usage:{chr(10)}
• FREE searches every day{chr(10)}
• Works only in groups to protect your privacy{chr(10)}{chr(10)}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{chr(10)}
🔧 Available Commands:{chr(10)}{chr(10)}
/num — Find details linked to a 10-digit mobile number{chr(10)}
/aadhar — Lookup details of a 12-digit Aadhaar number{chr(10)}
/calltrace — Call trace & telecom information{chr(10)}
/pan — PAN card information lookup{chr(10)}
/bin — Bank BIN details lookup{chr(10)}
/pincode — Indian post office & PIN details{chr(10)}
/weather — Weather information by city{chr(10)}
/ip — IP address information lookup{chr(10)}
/pinfo — Global phone number information{chr(10)}
/instagram — Instagram user profile info{chr(10)}
/tginfo — Telegram username information{chr(10)}
/ffinfo — Free Fire UID information{chr(10)}
/gst — GST number details lookup{chr(10)}
/rc — Vehicle RC information{chr(10)}
/pak — Pakistan mobile number lookup{chr(10)}{chr(10)}
🛡️ Protection Services:{chr(10)}
/protectnum — Protect your mobile number from searches{chr(10)}
/protectaadhar — Protect your Aadhaar from searches{chr(10)}{chr(10)}
💰 Support & Credits:{chr(10)}
/donate — Support our services with donations{chr(10)}
/support — Contact support team for help{chr(10)}{chr(10)}
🔧 Business Services:{chr(10)}
/makebot — Order your own custom OSINT bot{chr(10)}
/buyapi — Buy private API access{chr(10)}
/buydb — Purchase premium databases{chr(10)}{chr(10)}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{chr(10)}
⚡ Powered by: @providerbotz{chr(10)}
🛡️ Stay Safe | Respect Privacy | Use Responsibly """

FORCE_JOIN_MESSAGE = f"⚠️ Access Denied!{chr(10)}{chr(10)}Please join our channel first to use this bot:{chr(10)}👉 {{channel_link}}{chr(10)}{chr(10)}After joining, try again! ✅"

NOT_IN_GROUP_MESSAGE = f"❌ This bot only works in groups!{chr(10)}{chr(10)}Add me to your group to use OSINT features.{chr(10)}Contact: {SUPPORT_USERNAME}"

RATE_LIMIT_MESSAGE = f"⏳ Slow down!{chr(10)}{chr(10)}Please wait {{seconds}} seconds before next search.{chr(10)}{chr(10)}This prevents spam and keeps service fast for everyone! 🚀"

BLACKLISTED_MESSAGE = f"🚫 Access Denied{chr(10)}{chr(10)}You have been blacklisted from using this bot.{chr(10)}Contact: {SUPPORT_USERNAME}"

PROCESSING_MESSAGE = "⏳ Processing your request...{chr(10)}Please wait..."

ERROR_MESSAGE = f"❌ Something went wrong!{chr(10)}{chr(10)}Please try again or contact: {SUPPORT_USERNAME}"

MAINTENANCE_MODE_MESSAGE = f"🔧 Maintenance Mode{chr(10)}{chr(10)}Bot is currently under maintenance.{chr(10)}Please try again later!{chr(10)}{chr(10)}Contact: {SUPPORT_USERNAME}"

MISSING_QUERY_MESSAGE = f"❌ Missing Query!{chr(10)}{chr(10)}Please provide the required information.{chr(10)}{chr(10)}📝 Example: /{{command}} {{example}}"

# DM Messages for business commands
DM_CONTACT_MESSAGE = f"📩 For this service, please contact:{chr(10)}👉 {SUPPORT_USERNAME}{chr(10)}{chr(10)}We'll assist you shortly! ✨"

# Admin Panel Messages
ADMIN_PANEL_MESSAGE = f"🔐 Admin Control Panel{chr(10)}{chr(10)}Welcome, Boss! Choose an option below:"

ADMIN_PANEL_BUTTONS = [
    ["📊 Statistics", "👥 User List"],
    ["📢 Broadcast", "🔔 Notification"],
    ["🚫 Blacklist User", "✅ Unblacklist User"],
    ["📺 Force Channels", "📋 Search Logs"],
    ["🔧 Maintenance Mode", "🔄 Refresh Panel"]
]

# Command Examples for error messages
COMMAND_EXAMPLES = {
    "num": "9876543210",
    "aadhar": "393933081942",
    "calltrace": "9876543210",
    "pak": "923001234567",
    "pan": "AXDPR2606K",
    "bin": "457173",
    "pincode": "110001",
    "weather": "London",
    "ip": "8.8.8.8",
    "pinfo": "9876543210",
    "instagram": "harsha.official369",
    "ffinfo": "12022250",
    "tginfo": "username",
    "gst": "19BOKPS7056D1ZI",
    "rc": "UP92P2111"
}
