# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables to ensure that Python output is sent straight to the terminal (e.g., for logs)
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app
# Copy the application code into the container
COPY . /app/
# Install system dependencies for Poetry and any other dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

# Install Python dependencies with Poetry
RUN poetry install --no-interaction

RUN poetry add pycryptodome=3.18.0

# Expose port 8000 (default FastAPI port)
EXPOSE 9001

# Command to run the FastAPI app using Uvicorn
CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9001"]
