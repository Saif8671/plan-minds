# AI Schedule Organizer Backend

Production-ready FastAPI backend that accepts natural-language routines, parses them with AI, generates optimized schedules, manages tasks, tracks habits, and provides analytics.

## Features

- **Authentication** — JWT register, login, refresh tokens
- **User Profiles** — Timezone, wake/sleep times, study preferences
- **Task Management** — Fixed, flexible, and recurring tasks with priorities
- **AI Routine Parser** — Groq-backed AI with rule-based fallback
- **Scheduling Engine** — Conflict-aware daily/weekly schedule generation
- **Reminders** — Task, meal, water, sleep, and custom reminders
- **Analytics** — Dashboard, weekly, and monthly productivity reports

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | FastAPI + Python 3.12 |
| Database | PostgreSQL + SQLAlchemy 2.0 (async) |
| Migrations | Alembic |
| Auth | JWT (python-jose + passlib) |
| AI | Groq API (with rule-based fallback) |
| Validation | Pydantic v2 |

## Quick Start

### Prerequisites

- Python 3.12+
- PostgreSQL 16+ (or Docker)

### Local Development

```bash
cd backend

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env
# Edit .env with your settings

# Run database migrations
alembic upgrade head

# Start the server
uvicorn main:app --reload
```

API docs: [http://localhost:8000/docs](http://localhost:8000/docs)

### Docker

```bash
cd backend
copy .env.example .env
docker compose up --build
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/api/v1/auth/register` | Register user |
| POST | `/api/v1/auth/login` | Login |
| POST | `/api/v1/auth/refresh` | Refresh token |
| GET | `/api/v1/users/me` | Get profile |
| PUT | `/api/v1/users/me` | Update profile |
| POST | `/api/v1/tasks` | Create task |
| GET | `/api/v1/tasks` | List tasks |
| POST | `/api/v1/ai/parse-routine` | Parse natural language routine |
| POST | `/api/v1/ai/chat` | AI productivity chat |
| POST | `/api/v1/schedule/generate` | Generate schedule |
| POST | `/api/v1/schedule/regenerate` | Regenerate after skipped tasks |
| GET | `/api/v1/schedule/today` | Today's schedule |
| GET | `/api/v1/schedule/week` | Weekly schedule |
| POST | `/api/v1/reminders` | Create reminder |
| GET | `/api/v1/analytics/dashboard` | Dashboard analytics |

All endpoints except `/health`, `/auth/register`, and `/auth/login` require a Bearer token.

## Example Workflow

```bash
# 1. Register
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123","name":"Saif"}'

# 2. Parse a routine
curl -X POST http://localhost:8000/api/v1/ai/parse-routine \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"routine_text":"I wake up at 6. College from 9 to 4. Need 2 hours of DSA. Sleep at 11."}'

# 3. Generate schedule
curl -X POST http://localhost:8000/api/v1/schedule/generate \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{}'
```

## Project Structure

```
backend/
├── app/
│   ├── api/           # Route handlers (auth, users, tasks, ai, schedule, reminders, analytics)
│   ├── core/          # Config, database, security, logging, exceptions
│   ├── models/        # SQLAlchemy ORM models
│   ├── schemas/       # Pydantic request/response models
│   ├── services/      # Business logic layer
│   ├── repositories/  # Data access layer
│   └── tests/         # Unit tests
├── alembic/           # Database migrations
├── main.py            # Application entry point
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Testing

```bash
pytest
pytest --cov=app
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+asyncpg://...` |
| `SECRET_KEY` | JWT signing key | (required in production) |
| `GROQ_API_KEY` | Groq API key | (optional, uses rule-based fallback) |
| `GROQ_MODEL` | Groq model name | `llama-3.1-8b-instant` |
| `OPENAI_API_KEY` | Backwards-compatible alias for `GROQ_API_KEY` | optional |
| `OPENAI_MODEL` | Backwards-compatible alias for `GROQ_MODEL` | optional |
| `CORS_ORIGINS` | Allowed CORS origins | `["http://localhost:3000"]` |

## Future Enhancements

- Supabase Auth integration
- Celery + Redis background workers
- Firebase Cloud Messaging notifications
- LangGraph agent workflows
- Calendar sync (Google, Outlook, Apple)
- Vector database for habit learning

## License

MIT
