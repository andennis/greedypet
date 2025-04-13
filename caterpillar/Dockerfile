# Use Python 3.11 as the base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Create and activate virtual environment
ENV VIRTUAL_ENV=/opt/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install system dependencies
#RUN apt-get update && apt-get install -y \
#    build-essential \
#    && rm -rf /var/lib/apt/lists/*

# Copy the current project
COPY . /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables
ENV PYTHONPATH=/app

# Command to run when container starts
CMD ["python", "-m", "caterpillar"]