#!/bin/bash

# Check if NGROK_AUTHTOKEN is set
if [ -z "$NGROK_AUTHTOKEN" ]; then
  echo "Error: NGROK_AUTHTOKEN is not set"
  exit 1
fi

# Add ngrok authtoken
ngrok config add-authtoken $NGROK_AUTHTOKEN

# Start ngrok in the background
ngrok http 8001 > /dev/null &
sleep 5  # Wait for ngrok to initialize

# Get the public URL from ngrok
NGROK_URL=$(curl -s http://localhost:4040/api/tunnels | jq -r .tunnels[0].public_url)

# Check if NGROK_URL is empty
if [ -z "$NGROK_URL" ]; then
  echo "Error: Unable to fetch ngrok URL"
  exit 1
fi

# Log the ngrok URL
echo "ngrok URL: $NGROK_URL"

# Set the Telegram Webhook
WEBHOOK_URL="$NGROK_URL/$TELEGRAM_BOT_TOKEN"
curl -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/setWebhook" -d "url=$WEBHOOK_URL"

# Log the Webhook setup
echo "Webhook set to: $WEBHOOK_URL"
