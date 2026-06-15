# SocialHub

SocialHub is a full-stack social media management dashboard for drafting,
scheduling, publishing, and reviewing content from a single interface.

The repository is organized as a React frontend and a Flask API. AI-assisted
content tools use the OpenAI API, while platform publishing features require
valid credentials for the relevant social network.

## Features

- Multi-account content and publishing workflows
- Scheduled posts and platform-specific content
- Analytics dashboards and engagement reporting
- AI-assisted drafting, hashtag generation, and SEO analysis
- JWT-based authentication and REST API
- Docker Compose configuration for PostgreSQL, Redis, Flask, and Nginx

## Architecture

| Area | Technology |
| --- | --- |
| Frontend | React, Vite, Tailwind CSS, Recharts |
| Backend | Flask, SQLAlchemy, Flask-JWT-Extended |
| Data | SQLite for local development; PostgreSQL configuration for deployment |
| Background services | Redis and Celery configuration |
| AI | OpenAI API |

```text
.
├── backend/          Flask application and API
├── frontend/         React application
├── database/         Schema and database diagrams
├── documentation/    Architecture, test notes, and roadmap
├── nginx/            Reverse-proxy configuration
└── docker-compose.yml
```

## Local Development

### Prerequisites

- Python 3.11+
- Node.js 18+
- npm or pnpm

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python src/main.py
```

On Windows, activate the environment with `.venv\Scripts\activate`.

### Frontend

```bash
cd frontend
pnpm install
pnpm dev
```

The frontend development server and Flask API run independently. Review the
configured API base URL before starting the frontend.

## Configuration

Copy `backend/.env.example` to `backend/.env` and configure the values needed
for your environment:

- `SECRET_KEY`
- `JWT_SECRET_KEY`
- `DATABASE_URL`
- `OPENAI_API_KEY`
- Provider-specific social media credentials

Do not commit `.env` files, API tokens, or generated databases.

## Documentation

- [Installation guide](INSTALLATION.md)
- [API reference](API_DOCUMENTATION.md)
- [Deployment guide](DEPLOYMENT_GUIDE.md)
- [Project structure](PROJECT_STRUCTURE.md)
- [Architecture notes](documentation/system_architecture.md)

## Project Status

This is an integration-focused project. Some provider adapters require external
API access or environment-specific services and should be validated before
production use. Review authentication, CORS, rate limiting, provider terms, and
secret management as part of any deployment.

## License

No license has been declared for this repository. All rights remain with the
repository owner unless a license is added.
