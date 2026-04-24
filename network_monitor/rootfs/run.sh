#!/bin/bash

set -e

# Leggi la configurazione da Home Assistant
CONFIG_FILE=/data/options.json

NETWORK_RANGE=$(jq -r '.network_range // "192.168.1.0/24"' $CONFIG_FILE)
SCAN_INTERVAL=$(jq -r '.scan_interval_hours // 1' $CONFIG_FILE)
OFFLINE_THRESHOLD=$(jq -r '.offline_threshold_hours // 2' $CONFIG_FILE)
TELEGRAM_ENABLED=$(jq -r '.telegram_enabled // false' $CONFIG_FILE)
TELEGRAM_BOT_TOKEN=$(jq -r '.telegram_bot_token // ""' $CONFIG_FILE)
TELEGRAM_CHAT_ID=$(jq -r '.telegram_chat_id // ""' $CONFIG_FILE)
API_KEY=$(jq -r '.api_key // ""' $CONFIG_FILE)

# Esporta le variabili
export NETWORK_RANGE
export SCAN_INTERVAL_HOURS=$SCAN_INTERVAL
export OFFLINE_THRESHOLD_HOURS=$OFFLINE_THRESHOLD
export TELEGRAM_BOT_TOKEN
export TELEGRAM_CHAT_ID
export API_KEY
export FLASK_PORT=5000
export DEBUG=false

echo "🚀 Network Monitor Addon starting..."
echo "📍 Network: $NETWORK_RANGE"
echo "🔄 Scan interval: ${SCAN_INTERVAL}h"
echo "⏰ Offline threshold: ${OFFLINE_THRESHOLD}h"

if [ "$TELEGRAM_ENABLED" = "true" ]; then
    echo "📱 Telegram notifications: Enabled"
else
    echo "📱 Telegram notifications: Disabled"
fi

cd /app && python main.py
