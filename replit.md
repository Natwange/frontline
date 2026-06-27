# Frontline — AI Security Gateway

## Overview

Frontline is a production-inspired security gateway that protects public-facing AI agents from bot attacks, prompt injection, and cost abuse before requests reach the AI model.

The demo protects **CloudDesk**, a fictional SaaS company's AI support agent.

## Architecture

- **Frontend**: Next.js 15 (TypeScript, Tailwind CSS) — port 5000
- **Backend**: FastAPI (Python) — port 8000
- **Database**: PostgreSQL (via Replit managed DB)
- **Cache**: Redis (for rate limiting and behavior analysis)
- **AI**: Claude API (Anthropic) for the support agent and AI risk classifier

## Key Features

1. **6-layer protection pipeline**: validation → rate limiting → behavior analysis → prompt attack rules → cost protection → AI risk classifier
2. **Decision engine**: combines layer results, applies the strongest action (ALLOW / LOG_ONLY / RESTRICT / THROTTLE / BLOCK)
3. **Real-time dashboard**: metrics, attack categories, risk distribution, recent logs
4. **Attack simulator**: run preset scenarios (spam bot, slow bot, prompt attack, cost attack)
5. **False positive reporting**: users can flag wrongly blocked requests

## Project Structure

```
backend/
  app/
    api/            # FastAPI route handlers
    core/           # Config (pydantic-settings)
    models/         # SQLAlchemy ORM models
    schemas/        # Pydantic request/response schemas
    services/       # Pipeline, redaction, cost estimation, AI agent
    guardrails/     # Each protection layer (validation, rate_limit, behavior, prompt_rules, cost_protection, ai_classifier)
    decision_engine.py
    database.py
    redis_client.py
    main.py
  run.py
frontend/
  app/              # Next.js App Router pages (/, /chat, /dashboard, /simulator)
  components/       # Shared components (Navbar)
  lib/              # API client
```

## Running Locally

- **Backend**: `cd backend && python3 run.py` (port 8000)
- **Frontend**: `cd frontend && npm run dev` (port 5000)

## Environment Variables / Secrets

| Key | Required | Description |
|-----|----------|-------------|
| `ANTHROPIC_API_KEY` | Optional | Enables Claude-powered support agent and AI classifier |
| `DATABASE_URL` | Auto | Managed by Replit PostgreSQL |
| `REDIS_URL` | Optional | Redis for rate limiting; falls back to no-op if unavailable |

## Without ANTHROPIC_API_KEY

The pipeline runs fully — all deterministic layers (validation, rate limiting, behavior, prompt rules, cost protection) work without any API key. Only the AI support agent response and Layer 5 AI classifier require the key. Blocked/throttled/restricted requests are fully enforced without it.

## User Preferences

- Keep code organized by feature/layer
- Prefer deterministic rules over AI-only approaches
- Progressive enforcement: prefer logging/restriction before blocking
