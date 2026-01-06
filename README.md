# SDLC AI

AI-powered SDLC automation platform using:
- FastAPI
- LangGraph
- Celery
- Redis
- Ollama

## Prerequisites

- Python 3.10+
- Redis
- Ollama

## Setup

```bash
git clone <your-repo-url>
cd sdlc-ai

python3 -m venv .venv
source .venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

redis-server
ollama serve
ollama pull llama3:8b
celery -A app.workers.celery_worker.celery_app worker --loglevel=info
uvicorn app.main:app --reload
POST /v1/start

GET /v1/status/{job_id}

GET /v1/result/{job_id}

POST /v1/resume/{job_id}