# Руководство по деплою

## Локальный деплой

### Вариант 1: Прямой запуск

```bash
# Установка зависимостей
pip install -r requirements.txt

# Применение миграций
alembic upgrade head

# Запуск сервера
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Вариант 2: С несколькими workers (production)

```bash
# Применение миграций
alembic upgrade head

# Запуск с несколькими workers
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Вариант 3: С Gunicorn (production)

```bash
# Установка Gunicorn
pip install gunicorn

# Применение миграций
alembic upgrade head

# Запуск
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Docker деплой

### Вариант 1: Docker

```bash
# Сборка образа
docker build -t ml-service:latest .

# Запуск контейнера
docker run -d \
  -p 8000:8000 \
  -v ml_data:/app/data \
  -e DATABASE_URL="sqlite+aiosqlite:////app/data/ml_service.db" \
  -e SECRET_KEY="your-secret-key" \
  -e ADMIN_TOKEN="your-admin-token" \
  --name ml-service \
  ml-service:latest
```

### Вариант 2: Docker Compose

```bash
# Запуск (миграции применяются автоматически при старте контейнера)
docker-compose up -d

# Просмотр логов
docker-compose logs -f

# Остановка
docker-compose down
```

**Примечание:** Docker контейнер автоматически запускает `alembic upgrade head` перед стартом приложения (см. Dockerfile CMD)

## База данных в продакшене

### PostgreSQL (рекомендуется для production)

1. **Изменение requirements.txt**
```bash
# Добавьте
asyncpg==0.29.0
```

2. **Изменение DATABASE_URL в .env**
```
DATABASE_URL=postgresql+asyncpg://user:password@localhost/dbname
```

3. **Настройка PostgreSQL**
```bash
# Установка
sudo apt install postgresql postgresql-contrib -y

# Создание БД
sudo -u postgres psql
CREATE DATABASE ml_service;
CREATE USER ml_user WITH PASSWORD 'strong_password';
GRANT ALL PRIVILEGES ON DATABASE ml_service TO ml_user;
\q

# Применение миграций
alembic upgrade head
```

## Мониторинг и логирование

### Prometheus + Grafana

1. **Добавление метрик**
```bash
pip install prometheus-fastapi-instrumentator
```

2. **В app/main.py**
```python
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(...)

Instrumentator().instrument(app).expose(app)
```

### Sentry для error tracking

```bash
pip install sentry-sdk[fastapi]
```

```python
import sentry_sdk

sentry_sdk.init(
    dsn="your-sentry-dsn",
    traces_sample_rate=1.0,
)
```

## Безопасность в продакшене

### 1. Firewall

```bash
# UFW на Ubuntu
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

### 2. Fail2ban

```bash
sudo apt install fail2ban -y
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### 3. Изменение секретов

```bash
# Генерация нового SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Генерация нового ADMIN_TOKEN
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 4. HTTPS с Nginx

```nginx
# В Nginx конфигурации
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Резервное копирование

### SQLite

```bash
# Backup
sqlite3 ml_service.db ".backup ml_service_backup.db"

# Или через cron (ежедневно в 2:00)
0 2 * * * /usr/bin/sqlite3 /path/to/ml_service.db ".backup /backups/ml_service_$(date +\%Y\%m\%d).db"
```

### PostgreSQL

```bash
# Backup
pg_dump -U ml_user -d ml_service > backup.sql

# Restore
psql -U ml_user -d ml_service < backup.sql

# Автоматический backup
0 2 * * * /usr/bin/pg_dump -U ml_user -d ml_service > /backups/ml_service_$(date +\%Y\%m\%d).sql
```

## Scaling

### Horizontal Scaling

1. Используйте PostgreSQL вместо SQLite
2. Добавьте Redis для кеширования
3. Load balancer (nginx/HAProxy)
4. Несколько инстансов приложения

### Vertical Scaling

- CPU: Минимум 2 cores для PyTorch
- RAM: Минимум 4GB, рекомендуется 8GB+
- Disk: SSD для базы данных

## Health Checks

Добавьте в `app/main.py`:

```python
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}
```

## Работа с миграциями Alembic

### Проверка текущей версии

```bash
# Локально
alembic current

# В Docker контейнере
docker exec fastapitask-ml-service-1 alembic current
```

### Создание новой миграции

```bash
# После изменения моделей в app/models.py
alembic revision --autogenerate -m "описание изменений"

# Пример: добавили поле phone в User
alembic revision --autogenerate -m "add phone field to users"
```

### Применение миграций

```bash
# Применить все непримененные миграции
alembic upgrade head

# Применить конкретную миграцию
alembic upgrade <revision_id>

# В Docker автоматически при запуске
```

### Откат миграций

```bash
# Откатить одну миграцию назад
alembic downgrade -1

# Откатить до конкретной версии
alembic downgrade <revision_id>

# Откатить все миграции
alembic downgrade base
```

### История миграций

```bash
# Просмотр всех миграций
alembic history

# Подробная информация
alembic history --verbose
```

## Rollback приложения

```bash
# Docker
docker-compose down
docker-compose pull
docker-compose up -d

# Database rollback (если нужно)
docker exec fastapitask-ml-service-1 alembic downgrade -1
```

## Checklist перед деплоем

- [ ] SECRET_KEY изменен на уникальный
- [ ] ADMIN_TOKEN изменен на уникальный
- [ ] .env файл не в git репозитории
- [ ] Миграции применены
- [ ] Firewall настроен (если нужно)
- [ ] Backup настроен (если нужно)
- [ ] Health checks работают

## Полезные команды

### Docker

```bash
# Просмотр логов
docker-compose logs -f ml-service

# Перезапуск
docker-compose restart ml-service

# Остановка
docker-compose stop

# Удаление контейнеров и volumes
docker-compose down -v

# Проверка использования ресурсов
docker stats
```

### Локальный запуск

```bash
# Просмотр процессов
ps aux | grep uvicorn

# Проверка использования ресурсов
htop
df -h
free -h
```
