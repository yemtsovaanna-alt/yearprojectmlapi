# ML Service API

Полноценный ML-сервис на базе FastAPI для классификации изображений с использованием предобученной модели ResNet50.

## Возможности

- POST `/forward` - прогон данных через ML модель (изображения и JSON)
- GET `/history` - просмотр истории запросов (требует JWT авторизацию администратора)
- DELETE `/history` - удаление истории запросов (требует admin token в заголовке)
- GET `/stats` - статистика запросов с квантилями и характеристиками (требует JWT авторизацию администратора)
- JWT авторизация с ролями (пользователь/администратор)
- Миграции базы данных через Alembic
- Асинхронная работа с БД (SQLAlchemy + aiosqlite)

## Структура проекта

```
fastapitask/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Основное приложение с endpoints
│   ├── config.py               # Конфигурация приложения
│   ├── database.py             # Настройка БД
│   ├── models.py               # SQLAlchemy модели
│   ├── schemas.py              # Pydantic схемы
│   ├── auth.py                 # JWT авторизация
│   ├── ml_model.py             # ML модель (ResNet50)
│   └── imagenet_classes.json   # Классы ImageNet
├── alembic/
│   ├── versions/
│   │   └── 001_initial_migration.py
│   ├── env.py
│   └── script.py.mako
├── alembic.ini
├── requirements.txt
├── .env.example
├── .env
├── .gitignore
└── README.md
```

## Установка

### 1. Клонирование репозитория

```bash
cd fastapitask
```

### 2. Создание виртуального окружения

```bash
python -m venv venv
source venv/bin/activate  # На Linux/Mac
# или
venv\Scripts\activate  # На Windows
```

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 4. Настройка переменных окружения

Скопируйте `.env.example` в `.env` и измените значения при необходимости:

```bash
cp .env.example .env
```

Содержимое `.env`:
```
DATABASE_URL=sqlite+aiosqlite:///./ml_service.db
SECRET_KEY=your-secret-key-here-change-in-production
ADMIN_TOKEN=your-admin-token-here-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=30
```

### 5. Применение миграций базы данных

```bash
alembic upgrade head
```

## Запуск сервера

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Сервер будет доступен по адресу: `http://localhost:8000`

Автоматическая документация API:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Использование API

### 1. Регистрация пользователя

```bash
curl -X POST "http://localhost:8000/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123",
    "is_admin": true
  }'
```

### 2. Получение JWT токена

```bash
curl -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

Ответ:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

Сохраните `access_token` для последующих запросов.

### 3. POST /forward - Классификация изображения

```bash
curl -X POST "http://localhost:8000/forward" \
  -F "image=@/path/to/your/image.jpg"
```

Ответ:
```json
{
  "result": {
    "predictions": [
      {
        "class": "golden_retriever",
        "probability": 0.9234
      },
      {
        "class": "labrador_retriever",
        "probability": 0.0543
      }
    ],
    "top_class": "golden_retriever",
    "top_probability": 0.9234
  }
}
```

### 4. POST /forward - Обработка JSON данных

```bash
curl -X POST "http://localhost:8000/forward" \
  -F 'data={"text": "sample data", "value": 123}'
```

Ответ:
```json
{
  "result": {
    "message": "JSON data processed",
    "received_data": {
      "text": "sample data",
      "value": 123
    }
  }
}
```

### 5. GET /history - Просмотр истории запросов

Требует JWT авторизацию с правами администратора:

```bash
curl -X GET "http://localhost:8000/history" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

Ответ:
```json
{
  "total": 10,
  "items": [
    {
      "id": 1,
      "request_type": "image",
      "processing_time": 0.523,
      "input_data_size": 102400,
      "image_width": 800,
      "image_height": 600,
      "status_code": 200,
      "result": "...",
      "error_message": null,
      "created_at": "2025-12-24T10:30:00"
    }
  ]
}
```

### 6. DELETE /history - Удаление истории запросов

Требует admin token в заголовке Authorization:

```bash
curl -X DELETE "http://localhost:8000/history" \
  -H "Authorization: Bearer admin_secret_token_12345"
```

### 7. GET /stats - Статистика запросов

Требует JWT авторизацию с правами администратора:

```bash
curl -X GET "http://localhost:8000/stats" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

Ответ:
```json
{
  "total_requests": 100,
  "mean_processing_time": 0.456,
  "median_processing_time": 0.423,
  "percentile_95_processing_time": 0.789,
  "percentile_99_processing_time": 1.234,
  "average_input_size": 153600,
  "average_image_width": 1024,
  "average_image_height": 768
}
```

## Коды ответов

- `200` - Успешная обработка запроса
- `201` - Успешное создание ресурса
- `204` - Успешное удаление (без тела ответа)
- `400` - Неверный формат запроса (bad request)
- `401` - Не авторизован
- `403` - Доступ запрещен / Модель не смогла обработать данные
- `500` - Внутренняя ошибка сервера

## Обработка ошибок

### Неверный формат запроса (400)

```json
{
  "detail": "bad request"
}
```

### Модель не смогла обработать данные (403)

```json
{
  "detail": "модель не смогла обработать данные"
}
```

## Миграции базы данных

### Создание новой миграции

```bash
alembic revision --autogenerate -m "description of changes"
```

### Применение миграций

```bash
alembic upgrade head
```

### Откат последней миграции

```bash
alembic downgrade -1
```

### Просмотр истории миграций

```bash
alembic history
```

## Разработка

### Запуск в режиме разработки

```bash
uvicorn app.main:app --reload
```

### Тестирование endpoints

Используйте Swagger UI по адресу `http://localhost:8000/docs` для интерактивного тестирования всех endpoints.

## Технологии

- **FastAPI** - современный веб-фреймворк для построения API
- **SQLAlchemy** - ORM для работы с базой данных
- **Alembic** - инструмент миграций базы данных
- **PyTorch + torchvision** - ML фреймворк и предобученная модель ResNet50
- **JWT (python-jose)** - авторизация и аутентификация
- **Pydantic** - валидация данных
- **aiosqlite** - асинхронный драйвер для SQLite

## Безопасность

- Пароли хешируются с использованием bcrypt
- JWT токены с настраиваемым временем жизни
- Разделение прав доступа (пользователь/администратор)
- Валидация входных данных через Pydantic
- Защищенные эндпоинты для административных операций

## Лицензия

MIT
