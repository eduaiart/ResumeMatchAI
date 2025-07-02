# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements-gcp.txt requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Download spaCy model and clean up pip cache to reduce image size
RUN python -m spacy download en_core_web_sm && \
    pip cache purge

# Copy application files
COPY . .

# Create uploads directory
RUN mkdir -p uploads && chmod 755 uploads

# Create instance directory for Flask
RUN mkdir -p instance

# Set environment variables
ENV FLASK_APP=main.py
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

# Expose port - use PORT env var for Cloud Run compatibility
EXPOSE 8080

# Create non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Health check - use PORT env var
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8080}/ || exit 1

# Run the application - bind to PORT env var for Cloud Run compatibility
CMD ["sh", "-c", "exec gunicorn --bind 0.0.0.0:${PORT:-8080} --workers 2 --timeout 120 main:app"]