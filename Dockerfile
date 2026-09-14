FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Run the telegram bot
CMD ["python", "-m", "src.main"]
