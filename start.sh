#!/usr/bin/env bash
# Install system dependencies
apt update
apt install -y libenchant-2-2

# Install Python dependencies
pip install -r requirements.txt

# Start the bot
python bot.py