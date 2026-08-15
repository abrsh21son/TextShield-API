![CI](https://github.com/abrsh21son/TextShield-API/actions/workflows/ci.yml/badge.svg)

# TextShield API

A Flask-based REST API for text toxicity analysis.

## Features
- Toxicity analysis via ML model
- API key authentication
- User and admin dashboard
- Credit-based usage system
- PostgreSQL + SQLModel ORM

## Quick Start
```bash
pip install -r requirements.txt
cp .env.example .env
python app.py
```


## Deployment
Deploy to Render using render.yaml. Docker support is included via Dockerfile and docker-compose.yml.



## API Usage

```bash
curl -X POST https://your-app.onrender.com/api/analyze \
  -H 'Content-Type: application/json' \
  -H 'x-api-key: safe_yourkey' \
  -d '{"text": "Hello world"}'
```
