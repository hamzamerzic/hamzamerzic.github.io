FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    assimp-utils \
    libglib2.0-0 \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install flask flask-cors numpy pymeshlab

# Set working directory
WORKDIR /app

# Copy app code
COPY app.py /app/app.py
COPY clean_mesh.py /app/clean_mesh.py

# Expose port (optional for info)
EXPOSE 8080

# Start the Flask app
CMD ["python", "app.py"]
