FROM python:3.9-slim

WORKDIR /app

# Create logs directory
RUN mkdir -p /app/logs

# Copy just the requirements.txt first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose the web interface port
EXPOSE 8080

# Run the application
CMD ["python", "app.py"]