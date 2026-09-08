# Use a lightweight Python 3.11 Linux base image
FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Install dependencies first (leverages Docker layer caching)
COPY requirements.txt .
RUN pip install --default-timeout=1000 --retries=10 --no-cache-dir -r requirements.txt

# Copy application source code, trained model files, and configs
COPY . .

# Expose port 8000 for documentation purposes
EXPOSE 8000

# Bind Uvicorn to 0.0.0.0 so external host traffic can reach the container
# NOTE: 0.0.0.0 binds to all container network interfaces. Binding to 127.0.0.1 
# would restrict access to loopback inside the container, making it inaccessible from host port 8000.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]