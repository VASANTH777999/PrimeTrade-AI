# PrimeTrade AI

A secure, scalable REST API with authentication, role-based access, CRUD for tasks, validation, versioning, and a modern frontend UI served from the backend.

## Quick Start

- Ensure Python 3.10+ is installed.
- Run `python PrimeTradeAI.py`.
- The server starts at `http://127.0.0.1:8000/`.
- API docs are available at `http://127.0.0.1:8000/docs`.

The launcher installs dependencies automatically on first run.

## Features

- JWT authentication with password hashing
- Role-based access (user, admin)
- Versioned API under `/api/v1`
- CRUD for tasks with ownership rules
- Validation and consistent error responses
- CORS enabled for future clients
- Swagger UI for API documentation

## Endpoints

- `POST /api/v1/auth/register` — Register
- `POST /api/v1/auth/login` — Login, returns `access_token`
- `GET /api/v1/users` — List all users (admin only)
- `GET /api/v1/tasks` — List tasks; `?all=true` for admin to view all
- `POST /api/v1/tasks` — Create task
- `GET /api/v1/tasks/{id}` — Get task
- `PUT /api/v1/tasks/{id}` — Update task
- `DELETE /api/v1/tasks/{id}` — Delete task

## Frontend

A modern UI is served at `/` using Tailwind via CDN. It supports registration, login, dashboard access, and task CRUD. JWT is stored client-side and sent via `Authorization: Bearer <token>`.

## Database

Uses SQLite by default via SQLAlchemy and creates `prime_trade_ai.db` in the project directory. You can set `DATABASE_URL` to use Postgres/MySQL.

## Configuration

Environment variables:

- `SECRET_KEY` — JWT secret key
- `ACCESS_TOKEN_EXPIRE_MINUTES` — Token lifetime
- `DATABASE_URL` — Database URL (e.g., `postgresql+psycopg2://user:pass@host/db`)

## Scalability Notes

- Layered architecture with clear separation of schemas, models, auth, and CRUD.
- Stateless JWT-based auth enables horizontal scaling behind a load balancer.
- Replace SQLite with Postgres/MySQL for production.
- Add Redis for caching sessions and common queries.
- Containerize with Docker and orchestrate via Kubernetes for high availability.

## Security Practices

- Strong password hashing using Passlib
- JWT signed with configurable secret and expiration
- Input validation via Pydantic
- Ownership checks to restrict resource access

## API Docs

Swagger UI available at `/docs`. Import endpoints into Postman via the OpenAPI JSON at `/openapi.json`.

Postman collection provided at `static/postman_collection.json`.

## License

MIT
