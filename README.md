# Club Pass Service

Telegram bot-based ticket sales system for nightclubs.

## Project Structure

```
club-pass-service/
├── api/              # REST API service (FastAPI)
├── bot/              # Telegram bot service
├── mini-app/         # Telegram Mini App
├── docker/           # Dockerfiles
└── docs/             # Documentation
```

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)

### Running with Docker Compose

1. Copy environment variables:
   ```bash
   cp .env.example .env
   ```

2. Update `.env` with your configuration

3. Start services:
   ```bash
   docker-compose up -d
   ```

4. API will be available at: `http://localhost:8000`
   - API docs: `http://localhost:8000/docs`
   - Health check: `http://localhost:8000/api/v1/health`

### Local Development

1. Install dependencies:
   ```bash
   cd api
   pip install -r requirements.txt
   ```

2. Set up environment variables (see `.env.example`)

3. Run the API:
   ```bash
   uvicorn api.main:app --reload
   ```

## API Endpoints

- `GET /` - Root endpoint
- `GET /api/v1/health` - Health check
- `GET /api/v1/health/db` - Database health check

## Documentation

See `docs/` directory for:
- `PROJECT_DESCRIPTION.md` - Technical specification
- `PROJECT_STRUCTURE.md` - Architecture principles
