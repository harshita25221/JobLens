# Use Python 3.11 as the base image
FROM python:3.11-slim

# Install Node.js and npm (needed to build the frontend)
RUN apt-get update && apt-get install -y \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy the entire project into the container
COPY . /app

# 1. Build the Frontend
RUN cd frontend && npm install && npm run build

# 2. Install Backend Dependencies
# (We install gunicorn explicitly just in case)
RUN cd backend && pip install --no-cache-dir -r requirements.txt gunicorn

# 3. Cache the ML Models
# This downloads the KeyBERT model during the Docker build so it starts instantly
ENV HF_HOME=/app/backend/.hf_cache
RUN python -c "from keybert import KeyBERT; KeyBERT()"

# HuggingFace Spaces require the app to run on port 7860
ENV PORT=7860
EXPOSE 7860

# Set optimizations for CPU
ENV OMP_NUM_THREADS=1
ENV MKL_NUM_THREADS=1

# Start the Flask app using Gunicorn
CMD cd backend && gunicorn --bind 0.0.0.0:7860 --workers 1 --threads 2 --timeout 120 app:app
