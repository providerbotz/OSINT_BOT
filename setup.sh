#!/bin/bash

# ==========================================
# PROVIDER OSINT BOT - QUICK SETUP SCRIPT
# ==========================================

echo "🚀 Provider OSINT Bot - Quick Setup"
echo "================================="
echo ""

# Check Python
echo "📦 Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Installing..."
    sudo apt update
    sudo apt install python3 python3-pip -y
else
    echo "✅ Python3 found: $(python3 --version)"
fi

echo ""

# Install requirements
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully!"
else
    echo "❌ Failed to install dependencies!"
    exit 1
fi

echo ""
echo "================================="
echo "✅ Setup Complete!"
echo ""
echo "Next steps:"
echo "1. Edit config.py and add your API URLs"
echo "   nano config.py"
echo ""
echo "2. Run the bot:"
echo "   python3 bot.py"
echo ""
echo "Or use PM2 for production:"
echo "   pm2 start bot.py --name provider --interpreter python3"
echo ""
echo "================================="
echo "📞 Support: @PROVIDERBOTZ"
echo "================================="
