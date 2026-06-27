# Frontline

**Frontline** is a production-inspired security gateway that protects public-facing AI agents from bot attacks and abusive requests before they reach the AI model.

Instead of sending every request directly to an LLM, Frontline applies multiple layers of protection to detect suspicious behavior, reduce AI costs, and minimize false positives.

## Features

* Layered request protection pipeline
* Redis-backed rate limiting
* Behavior analysis for repeated and automated requests
* Prompt attack detection
* Cost protection for expensive AI requests
* AI-assisted risk classification for ambiguous cases
* Explainable security decisions
* Request logging and audit trails
* Attack simulator
* Analytics dashboard

## Architecture

```text
User / Bot
      │
      ▼
 Frontline Security Gateway
      │
      ├── Request Validation
      ├── Rate Limit Defense
      ├── Behavior Analysis
      ├── Prompt Attack Rules
      ├── Cost Protection
      ├── AI Risk Classifier (only when needed)
      └── Decision Engine
      │
      ▼
 Protected AI Agent
      │
      ▼
   AI Response
```

## Tech Stack

### Frontend

* Next.js
* TypeScript
* Tailwind CSS

### Backend

* FastAPI
* Python
* SQLAlchemy
* Pydantic

### Infrastructure

* PostgreSQL
* Redis
* Docker
* Docker Compose

### AI

* Claude API

### Cloud (Planned)

* AWS ECS Fargate
* AWS RDS
* AWS ElastiCache
* AWS CloudWatch

## Project Status

🚧 Currently under active development.

The first milestone focuses on building the core backend infrastructure, request pipeline, and security layers before implementing the dashboard and attack simulator.
