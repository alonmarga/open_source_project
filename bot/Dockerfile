# Use a lightweight Python image
FROM python:3.11-slim

# Set the working directory
WORKDIR /opt

# Copy both app and bot folders into the container
COPY ./app /app
COPY ./bot /bot

# Install dependencies
RUN pip install --no-cache-dir -r /bot/requirements.txt -r /app/requirements.txt

# Set PYTHONPATH to allow bot to access app
ENV PYTHONPATH="/:/app"

# Run the bot
CMD ["python", "main.py"]
