# SDLC AI

AI-powered SDLC automation platform using:
- FastAPI
- LangGraph
- Celery
- Redis
- Ollama

---

## Prerequisites

- Ubuntu / WSL2
- Python **3.10+** (mandatory)
- Redis
- Ollama
- Enterprise laptops: browser access to `localhost` may be restricted

---

## Important Notes (Read This First)

- Python **3.8 / 3.9 will NOT work** (LangGraph + modern typing requires 3.10+)
- Browser access to `http://localhost` may be **blocked by enterprise security**
- **curl is the source of truth** for API validation
- Swagger UI (`/docs`) is optional, not required

---

## Python Version Setup (Required)

### Install Python 3.10 using pyenv (Ubuntu / WSL)

System Python on Ubuntu 20.04 is too old. Use `pyenv`.

```bash
sudo apt update
sudo apt install -y \
  build-essential libssl-dev zlib1g-dev libbz2-dev \
  libreadline-dev libsqlite3-dev libffi-dev \
  libncurses5-dev libncursesw5-dev liblzma-dev \
  xz-utils tk-dev ca-certificates curl

 ## after restarting vm 
 source venv/bin/activate
  pkill -f celery
  redis run
  ollama serve
  ollama run llama3.2:3b "warmup"
  celery -A app.workers.celery_worker.celery_app worker -l info
  uvicorn app.main:app --host 0.0.0.0 --port 8000