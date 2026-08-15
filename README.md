![CI](https://github.com/abrsh21son/TextShield-API/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-3.1-lightgrey?logo=flask)
![License](https://img.shields.io/badge/License-MIT-gold)

# TextShield API

> AI-powered text toxicity detection as a service. Protect your platform from harmful content with a simple REST API.

---

## Overview

TextShield API analyses text content in real-time and returns a toxicity score, profanity flag, and detailed breakdown — helping developers build safer, more respectful digital experiences.

**Key capabilities:**

- Toxicity scoring with detailed category breakdown
- Profanity detection with configurable thresholds
- Credit-based usage system with per-user API keys
- User dashboard with weekly usage analytics
- Admin panel for user and key management
- Mock analyzer mode for local development (no external calls)

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11, Flask 3.1 |
| ORM | SQLModel + SQLAlchemy 2 |
| Database | PostgreSQL (production) / SQLite (dev/test) |
| Auth | Session-based + API key middleware |
| ML Model | External Hugging Face Space (REST) |
| Frontend | Jinja2 templates + Tailwind CSS |
| Server | Gunicorn |
| CI | GitHub Actions |
| Deploy | Render / Docker |

---

## Getting Started

### Prerequisites

- Python 3.11+
- pip

### Local Setup

```bash
# 1. Clone the repository
git clone https://github.com/abrsh21son/TextShield-API.git
cd TextShield-API

# 2. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
```

Edit `.env`:

```env
DATABASE_URL=sqlite:///./app.db
FLASK_SECRET_KEY=any-random-secret-string
ANALYZER_URL=mock
DEMO_API_KEY=
```

> `ANALYZER_URL=mock` uses a local keyword-based scorer — no external service needed for development.

```bash
# 5. Run the app
python app.py
```

Visit `http://localhost:5000`

---

## Docker (with PostgreSQL)

```bash
docker-compose up --build
```

The app will be available at `http://localhost:8000` with a full PostgreSQL database running alongside it.

```bash
# Stop everything
docker-compose down
```

---

## Creating an Admin Account

There is no admin signup page. Insert one directly into the database:

```bash
python -c "
from utility.database.main import get_session, init_db
from utility.database.model import Admin
from werkzeug.security import generate_password_hash
init_db()
db = get_session()
db.add(Admin(email='admin@example.com', password_hash=generate_password_hash('yourpassword')))
db.commit()
print('Admin created successfully')
"
```

Then log in at `/admin/login`.

---

## API Reference

### Analyze Text (authenticated)

```http
POST /api/analyze
x-api-key: safe_yourapikey
Content-Type: application/json

{
  "text": "Your text here"
}
```

**Response:**

```json
{
  "success": true,
  "toxicity_score": 12.5,
  "is_profane": false,
  "result": {
    "toxicity": 12.5,
    "severe_toxicity": 10.0,
    "obscene": 7.5,
    "identity_attack": 6.25,
    "insult": 8.75,
    "threat": 5.0,
    "sexual_explicit": 0.0,
    "average": 12.5
  }
}
```

### Demo Analyze (no auth required)

```http
POST /api/demo-analyze
Content-Type: application/json

{
  "text": "Hello world"
}
```

### Generate API Key

```http
POST /api/generate-key
(requires login session)
```

### Delete API Key

```http
DELETE /api/delete-key
Content-Type: application/json

{
  "key": "safe_yourapikey"
}
```

---

## Page Routes

| Route | Description |
|---|---|
| `/` | Landing page |
| `/user/signup` | User registration |
| `/user/login` | User login |
| `/user/dashboard` | User dashboard (API keys, usage chart) |
| `/admin/login` | Admin login |
| `/admindashboard` | Admin dashboard (user management, stats) |
| `/api/analyze` | Authenticated text analysis |
| `/api/demo-analyze` | Demo analysis (no key needed) |
| `/api/usage-stats` | User usage statistics (JSON) |
| `/logout` | Session logout |

---

## Deployment (Render)

1. Sign up at [render.com](https://render.com)
2. Create a **PostgreSQL** database — copy the connection string
3. Create a **Web Service** → connect `abrsh21son/TextShield-API`
4. Render auto-detects `render.yaml`
5. Set environment variables:

| Variable | Value |
|---|---|
| `DATABASE_URL` | Your PostgreSQL connection string |
| `FLASK_SECRET_KEY` | Click "Generate" in Render |
| `ANALYZER_URL` | `https://your-hf-space.hf.space/analyze` |
| `DEMO_API_KEY` | Optional demo key string |

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `DATABASE_URL` | Yes | PostgreSQL or SQLite connection string |
| `FLASK_SECRET_KEY` | Yes | Secret key for session signing |
| `ANALYZER_URL` | Yes | ML model endpoint or `mock` |
| `DEMO_API_KEY` | No | Optional key to bypass auth for demo |

---

## Running Tests

```bash
pytest
```

Tests use SQLite in-memory and the mock analyzer — no external services needed.

```bash
# With coverage
pytest --cov=. --cov-report=term-missing
```

---

## Project Structure

```
TextShield-API/
├── app.py                    # Flask app, routes, auth decorators
├── config.py                 # Environment config
├── wsgi.py                   # Production WSGI entry point
├── middleware/
│   └── api_auth.py           # API key authentication
├── routes/
│   └── analyze.py            # /api/analyze blueprint
├── services/
│   ├── analyzer.py           # Toxicity analysis logic
│   └── usage.py              # Usage recording service
├── utility/
│   ├── database/
│   │   ├── model.py          # SQLModel ORM models
│   │   └── main.py           # DB engine and session
│   └── mapper.py             # Chart data mapper
├── templates/
│   ├── User/                 # Landing, login, signup, dashboard
│   └── Admin/                # Admin login, admin dashboard
├── static/
│   ├── css/                  # Black/gold theme stylesheets
│   └── Js/                   # Frontend JavaScript
└── tests/                    # pytest test suite
```

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## License

MIT License. See [LICENSE](LICENSE) for details.

---

*TextShield API v1.0.0 — August 2026*
