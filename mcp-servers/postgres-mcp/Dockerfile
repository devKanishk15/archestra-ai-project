FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy server code
COPY server.py .

# Make server executable
RUN chmod +x server.py

# Set environment variables (can be overridden)
ENV POSTGRES_HOST=postgres
ENV POSTGRES_PORT=5432
ENV POSTGRES_DB=transformation_db
ENV POSTGRES_USER=admin
ENV POSTGRES_PASSWORD=admin123

# Run the server
CMD ["python", "server.py"]
