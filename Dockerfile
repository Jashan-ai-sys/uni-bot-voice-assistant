# Base Image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install System Dependencies (Required for Unstructured/PDF processing)
RUN apt-get update && apt-get install -y \
    libmagic-dev \
    poppler-utils \
    tesseract-ocr \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Requirements
COPY requirements.txt .

# Install Python Dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy Application Code
COPY src/ /app/src/
COPY db/ /app/db/
COPY data/ /app/data/

# Verify Directory Structure (Debugging)
RUN ls -R /app/src

# Expose Port
EXPOSE 8000

# Start Command
CMD ["uvicorn", "src.web_app:app", "--host", "0.0.0.0", "--port", "8000"]
