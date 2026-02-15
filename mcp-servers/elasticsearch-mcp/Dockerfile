FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy server code
COPY server.py .

# Make server executable
RUN chmod +x server.py

# Set environment variables
ENV ELASTICSEARCH_URL=http://elasticsearch:9200

# Run the server
CMD ["python", "server.py"]
