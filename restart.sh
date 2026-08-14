#!/bin/bash
# Find and kill any existing instances of honcho and the bot
echo "Stopping any existing bot instances..."
pkill -f "honcho"
pkill -f "python -m src.main"
pkill -f "redis_gateway.py"
sleep 1

# Start honcho
echo "Starting new honcho instance..."
honcho start
