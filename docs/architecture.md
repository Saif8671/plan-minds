# Architecture

PlanMinds is built on a split architecture:

## Backend
- **Framework:** FastAPI
- **Database:** PostgreSQL (with Asyncpg)
- **ORM:** SQLAlchemy + Alembic (Migrations)
- **AI Processing:** Groq integration for fast natural language parsing
- **Scheduler:** Background worker processing (planned APScheduler/Redis integration)
- **Containerization:** Docker & Docker Compose

## Mobile
- **Framework:** React Native with Expo
- **Language:** TypeScript
- **State Management:** Zustand (global UI state), React Query (server state & caching)
- **Styling:** NativeWind (Tailwind CSS)
- **Navigation:** React Navigation (Stack + Tabs)
