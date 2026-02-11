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
#if new clone python3 -m venv venv
 source .venv/bin/activate
 pip install -r requirements.txt

  export REDIS_URL=redis://localhost:6379/0
  export JWT_SECRET=change-me
  export ALGORITHM=HS256
  export DATABASE_URL=postgresql://neondb_owner:npg_X5fpqRK6Cawb@ep-bitter-field-ahc8s4ys-pooler.c-3.us-east-1.aws.neon.tech/sdlc_ai_prod?sslmode=require
  sudo apt update
  sudo apt install redis-server -y

  pkill -f celery
  redis run or sudo systemctl start redis-server

  ollama serve
  ollama run llama3.2:3b "warmup"
  celery -A app.workers.celery_worker.celery_app worker -l info
  uvicorn app.main:app --host 0.0.0.0 --port 8000

  start api test payload
 {"product_idea":"Create structured, client-facing documentation for a financial investment solutions application.\n      ","domain":"Financial Services – Investment Products and Portfolio Management","target_audience":{"primary":["Retail investors","Relationship managers","Financial planners","      "],"secondary":["Compliance teams","Operations teams","Financial advisors","      "]},"documentation_objective":" Provide clear, accurate, regulator-safe documentation without offering financial advice.\n      ","regulatory_context":["No financial advice","No performance guarantees","Regulated financial environment","Data privacy compliance","      "]}