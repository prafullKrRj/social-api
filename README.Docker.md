# Docker Setup for Social API

This project is dockerized with two containers:
1. **PostgreSQL Database** - For data storage
2. **Django API** - The Social API application

## 📋 Prerequisites

- Docker installed on your system
- Docker Compose installed

## 🚀 Quick Start

### 1. Build and Start Containers

```bash
docker-compose up --build
```

This command will:
- Build the Django application image
- Pull the PostgreSQL image
- Start both containers
- Run database migrations automatically
- Start the Django development server

### 2. Access the Application

- **API**: http://localhost:8000
- **PostgreSQL**: localhost:5432

### 3. Stop Containers

```bash
docker-compose down
```

To stop and remove volumes (database data):
```bash
docker-compose down -v
```

## 🔧 Environment Variables

All environment variables are in the `.env` file:

```env
# Django Settings
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Settings
DB_ENGINE=django.db.backends.postgresql
DB_NAME=socialapi
DB_USER=postgres
DB_PASSWORD=postgres123
DB_HOST=postgres
DB_PORT=5432

# JWT Settings
ACCESS_TOKEN_LIFETIME_DAYS=365
REFRESH_TOKEN_LIFETIME_DAYS=30
```

**⚠️ Important**: Change the `SECRET_KEY` and `DB_PASSWORD` for production!

## 📝 Common Commands

### Create a superuser

```bash
docker-compose exec web python manage.py createsuperuser
```

### Run migrations

```bash
docker-compose exec web python manage.py migrate
```

### View logs

```bash
docker-compose logs -f
```

### Access Django shell

```bash
docker-compose exec web python manage.py shell
```

### Access PostgreSQL

```bash
docker-compose exec postgres psql -U postgres -d socialapi
```

## 🏗️ Project Structure

```
Social-api/
├── docker-compose.yml    # Orchestrates both containers
├── Dockerfile           # Django app container definition
├── .env                # Environment variables
├── .dockerignore       # Files to exclude from Docker build
├── requirements.txt    # Python dependencies
├── manage.py          # Django management script
├── socialapi/         # Django project settings
├── accounts/          # Accounts app
├── posts/            # Posts app
└── social/           # Social app
```

## 🔄 Development Workflow

1. Make code changes (they auto-reload in the container via volume mount)
2. If you add new dependencies, rebuild:
   ```bash
   docker-compose up --build
   ```
3. If you change models, run migrations:
   ```bash
   docker-compose exec web python manage.py makemigrations
   docker-compose exec web python manage.py migrate
   ```

## 🛠️ Troubleshooting

### Port already in use
If port 8000 or 5432 is already in use, change the ports in `docker-compose.yml`:
```yaml
ports:
  - "8001:8000"  # Change 8001 to any available port
```

### Database connection errors
Ensure the PostgreSQL container is healthy:
```bash
docker-compose ps
```

### Reset everything
```bash
docker-compose down -v
docker-compose up --build
```

## 📦 Production Deployment

For production:
1. Set `DEBUG=False` in `.env`
2. Change `SECRET_KEY` to a secure random string
3. Update `ALLOWED_HOSTS` with your domain
4. Use a stronger database password
5. Consider using Gunicorn instead of Django's dev server
6. Set up proper static file serving

## 📄 License

This project is part of the Social API application.

