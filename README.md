# Datura AI FastAPI Task

This project is a FastAPI-based web service that utilizes various machine learning and AI components. The app is designed to serve as a starting point for building scalable APIs with FastAPI, Poetry, Docker, and other Python-related technologies.

## Features

- FastAPI backend for efficient API handling
- Poetry for dependency management and environment management
- Docker for containerization
- Handles interactions with `bittensor` for decentralized AI models (if relevant to your project)
- Exposes endpoints for interacting with machine learning models or APIs

## Requirements

- Python 3.10 or higher
- Poetry for managing dependencies
- Docker (if containerized deployment is desired)

## Installation

To set up this project, follow these steps:

### 1. Clone the Repository

```bash
glory03023git clone https://github.com/glory03023/datura_ai_fastapi_task.git
cd datura_ai_fastapi_task
docker-compose up --build
```
or
```bash
glory03023git clone https://github.com/glory03023/datura_ai_fastapi_task.git
cd datura_ai_fastapi_task
poetry install
poetry run uvicorn main:app --host 0.0.0.0 --port 9001
celery -A celery_worker worker --loglevel=info
```
Please check apis on http://45.23.20.2:9001/docs