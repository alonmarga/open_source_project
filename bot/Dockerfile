# Use Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /opt/bot

# Copy bot source code into the container
COPY . /opt/bot

# Install dependencies from requirements.txt
RUN apt-get update && apt-get install -y curl jq \
    && pip install --no-cache-dir -r requirements.txt

# Download ngrok
RUN curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | tee /etc/apt/trusted.gpg.d/ngrok.asc > /dev/null && \
    echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | tee /etc/apt/sources.list.d/ngrok.list && \
    apt-get update && apt-get install ngrok

# Add script to set Webhook
COPY setup_webhook.sh /opt/bot/setup_webhook.sh
RUN chmod +x /opt/bot/setup_webhook.sh

# Set PYTHONPATH to include the app folder
ENV PYTHONPATH="/opt:/opt/app:/opt/bot"

# Expose port for FastAPI
EXPOSE 8001

# Start ngrok and bot
CMD ["/bin/bash", "-c", "/opt/bot/setup_webhook.sh && uvicorn main:app --host 0.0.0.0 --port 8001"]
