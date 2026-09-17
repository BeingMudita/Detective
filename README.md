# 🕵️ Internet Detective

A controlled **OSINT investigation simulation** — players crack fictional
cybersecurity mysteries by discovering entities, correlating evidence,
reconstructing timelines, and defending a case. Built as a B.Tech CSE
final-year project.

> **Zero-cost by design.** The whole application builds, runs, tests and demos on
> a single laptop with `docker compose up`. No paid API, no cloud account, no
> managed database, no API key. Recurring cost: **₹0.**

> **Safety.** Every identity, username, email, domain, IP, organisation and
> profile in this project is **fictional or a reserved example**
> (`*.example` domains, RFC-5737 documentation IP ranges). The app performs no
> real reconnaissance, scraping, scanning, or investigation of real people.

The full architecture, engine design, database model, threat model and roadmap
live in [`docs/design-spec.html`](docs/design-spec.html) (open it in a browser).

---

## Status — Phase 1: Foundation ✅

This repository currently implements the **foundation** slice:

- Async **FastAPI** backend, **SQLAlchemy 2.0** models, **Alembic** migration.
- **Argon2id** password hashing, **JWT** access tokens, and **Postgres-backed,
  rotating, revocable refresh tokens** delivered as an httpOnly cookie.
- **Role-based access control** (`PLAYER` / `ADMIN`).
- Append-only **audit log** (the substrate for later analytics & research).
- **React + TypeScript + Vite + Tailwind** shell: register, login, protected
  dashboard, sign-out, 404 — with the product's "SOC / case-dossier" look.
- Tests that run on **SQLite** (backend) and **jsdom** (frontend) — no services
  required.

Cases, the investigation graph, scoring, timelines and Watson arrive in later
phases (see the roadmap in the design spec).

---

## Quick start (Docker — recommended)

```bash
cp .env.example .env
docker compose up --build
```

Then open:

| Surface        | URL                              |
| -------------- | -------------------------------- |
| App (frontend) | http://localhost:5173            |
| API docs       | http://localhost:8000/docs       |
| Health check   | http://localhost:8000/api/v1/health |

The backend automatically runs migrations and seeds two demo accounts:

| Role   | Email                     | Password          |
| ------ | ------------------------- | ----------------- |
| Admin  | `admin@aurelia.example`   | `Detective#001`   |
| Player | `player@aurelia.example`  | `Investigate#001` |

> These are development seeds — change them before any real deployment.

---

## Local development (without Docker)

You need Python 3.12+, Node 20+, and a local PostgreSQL (or point
`DATABASE_URL` at any Postgres you have).

**Backend**

```bash
cd backend
python -m venv .venv && source .venv/Scripts/activate   # Windows Git Bash
# (Linux/macOS: source .venv/bin/activate)
pip install -r requirements.txt

# Edit ../.env: set DATABASE_URL host to localhost, or export it:
export DATABASE_URL="postgresql+asyncpg://detective:detective@localhost:5432/detective"

alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload
```

**Frontend**

```bash
cd frontend
npm install
npm run dev          # http://localhost:5173, proxies /api -> localhost:8000
```

---

## Testing

```bash
# Backend — runs on in-memory SQLite, needs no database server
cd backend && pip install -r requirements.txt && pytest -q

# Frontend
cd frontend && npm run test
```

Phase 1 ships **16 backend tests** (auth flow, RBAC, security primitives,
health) and **4 frontend tests** (auth store, UI component).

---

## Project structure

```
Detective/
├─ backend/            FastAPI · SQLAlchemy · Alembic
│  ├─ app/
│  │  ├─ api/v1/       routers: auth, users, admin, health
│  │  ├─ core/         config, security, rate limiting, logging
│  │  ├─ db/           engine, session, declarative base
│  │  ├─ models/       users, refresh_tokens, audit_log
│  │  ├─ schemas/      Pydantic request/response models
│  │  ├─ repositories/ data access
│  │  ├─ services/     auth use-cases (framework-agnostic)
│  │  └─ seed.py
│  ├─ alembic/         migrations (0001_initial)
│  └─ tests/           pytest (SQLite)
├─ frontend/           React · TS · Vite · Tailwind
│  └─ src/
│     ├─ app/          providers, router
│     ├─ components/   ui primitives, layout
│     ├─ features/     auth, dashboard
│     ├─ lib/api/      typed client with silent token refresh
│     └─ store/        zustand auth slice
├─ docs/design-spec.html   full architecture & roadmap
├─ docker-compose.yml
└─ .env.example
```

---

## Security notes (Phase 1)

- Passwords hashed with **Argon2id**; never stored or logged in plaintext.
- Access tokens are short-lived JWTs; refresh tokens are opaque, stored **only
  as SHA-256 hashes**, rotated on use and revocable on logout.
- RBAC enforced server-side on every protected route (never inferred from the
  client).
- Security headers, strict CORS to the frontend origin, and in-process rate
  limiting on auth endpoints.
- `SECRET_KEY` is generated and persisted locally on first run if unset — no
  external secret manager, no manual key handling.

---

## License / academic use

Educational project. All scenarios and data are fictional and exist solely to
teach OSINT investigation *methodology* and analytical reasoning in a sandbox.
