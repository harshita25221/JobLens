# Use Python 3.11 as the base image
FROM python:3.11-slim

# Install Node.js and npm (needed to build the frontend)
RUN apt-get update && apt-get install -y \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Set up a new user named "user" with user ID 1000
# HuggingFace requires apps to run as a non-root user for security
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

WORKDIR $HOME/app

# Copy the entire project into the container and change ownership to our new user
COPY --chown=user . $HOME/app

# 1. Build the Frontend
RUN cd frontend && npm install && npm run build

# 2. Install Backend Dependencies
RUN cd backend && pip install --no-cache-dir -r requirements.txt gunicorn


# HuggingFace Spaces require the app to run on port 7860
ENV PORT=7860
EXPOSE 7860

# Set optimizations for CPU
ENV OMP_NUM_THREADS=1
ENV MKL_NUM_THREADS=1

# Start the Flask app using Gunicorn
CMD cd backend && gunicorn --bind 0.0.0.0:7860 --workers 1 --threads 2 --timeout 120 app:app
