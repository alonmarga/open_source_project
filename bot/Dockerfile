# Use Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /opt/bot

# Copy bot source code into the container
COPY . /opt/bot

# Install dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Ensure the app folder is included in PYTHONPATH
ENV PYTHONPATH="/opt/app"

# Run the bot
CMD ["python", "main.py"]
