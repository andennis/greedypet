FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Create and activate virtual environment
ENV VIRTUAL_ENV=/opt/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Copy the current project
COPY . /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables
ENV PYTHONPATH=/app

# Command to run when container starts
CMD ["./caterpillar.sh"]