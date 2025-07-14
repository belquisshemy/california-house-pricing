# Use Python 3.10.4 slim version (smaller image)
FROM python:3.10.4-slim

# Set working directory
WORKDIR /app

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install dependencies, --no-cache-dir Reduces image size
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create a non-root user for security
RUN useradd --create-home --shell /bin/bash appuser && chown -R appuser:appuser /app
USER appuser

# Expose port (use 8000 as default, but Render will override with $PORT)
EXPOSE 8000

# Command to run the application
CMD gunicorn --workers=4 --bind 0.0.0.0:${PORT:-8000} app:app

