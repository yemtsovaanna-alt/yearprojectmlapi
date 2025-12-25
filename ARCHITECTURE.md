# Архитектура проекта

## Обзор

ML Service API - это асинхронный веб-сервис для классификации изображений с использованием предобученной модели ResNet50. Сервис построен на FastAPI и поддерживает JWT авторизацию, хранение истории запросов и сбор статистики.

## Компоненты системы

### 1. Web Layer (FastAPI)

**app/main.py** - основной файл приложения

Endpoints:
- `POST /register` - регистрация пользователей
- `POST /token` - получение JWT токена
- `POST /forward` - прогон данных через ML модель
- `GET /history` - просмотр истории запросов (admin)
- `DELETE /history` - удаление истории (admin token)
- `GET /stats` - статистика запросов (admin)

### 2. Database Layer

**app/database.py** - конфигурация базы данных

- Асинхронный движок SQLAlchemy
- SQLite с драйвером aiosqlite
- Session management через dependency injection
- Автоматическая инициализация таблиц

**app/models.py** - ORM модели

```
RequestHistory:
  - id
  - request_type
  - processing_time
  - input_data_size
  - image_width, image_height
  - status_code
  - result
  - error_message
  - created_at

User:
  - id
  - username (unique)
  - hashed_password
  - is_admin
  - created_at
```

### 3. Validation Layer

**app/schemas.py** - Pydantic схемы

- Валидация входных данных
- Сериализация/десериализация
- Type safety
- Автоматическая генерация документации

### 4. Authentication & Authorization

**app/auth.py** - система авторизации

Функции:
- Хеширование паролей (bcrypt)
- Создание JWT токенов
- Валидация токенов
- Role-based access control (RBAC)
- Проверка admin токена

Роли:
- **User** - обычный пользователь
- **Admin** - администратор (доступ к /history и /stats)

### 5. ML Layer

**app/ml_model.py** - ML модель

- Предобученная ResNet50 (ImageNet weights)
- Preprocessing pipeline:
  - Resize 256x256
  - Center crop 224x224
  - Нормализация
- Top-K предсказания
- Обработка ошибок

**app/imagenet_classes.json** - маппинг классов ImageNet

### 6. Configuration

**app/config.py** - управление конфигурацией

Использует `pydantic-settings` для загрузки переменных окружения:
- DATABASE_URL
- SECRET_KEY
- ADMIN_TOKEN
- JWT_ALGORITHM
- JWT_EXPIRATION_MINUTES

### 7. Database Migrations

**alembic/** - система миграций

- Версионирование схемы БД
- Автоматическая генерация миграций
- Rollback поддержка
- История изменений

## Поток данных

### Классификация изображения

```
Client
  ↓ POST /forward (multipart/form-data)
FastAPI Endpoint
  ↓ File validation
ML Model (ResNet50)
  ↓ Image preprocessing
  ↓ Inference
  ↓ Top-K predictions
Database
  ↓ Save request history
Response
  ↓ JSON with predictions
Client
```

### Авторизованный запрос

```
Client
  ↓ Request with JWT token
JWT Middleware
  ↓ Token validation
  ↓ Extract user info
Database
  ↓ Verify user exists
  ↓ Check permissions
Endpoint Handler
  ↓ Business logic
Response
  ↓ JSON data
Client
```

## Безопасность

### 1. Аутентификация

- Пароли хешируются с bcrypt (work factor: 12)
- JWT токены с временем жизни (default: 30 минут)
- Secure token generation (python-jose)

### 2. Авторизация

- Role-based access control
- Admin endpoints защищены JWT
- DELETE /history требует отдельный admin token
- Dependency injection для проверки прав

### 3. Валидация данных

- Pydantic схемы для всех входных данных
- Type checking на уровне Python
- Автоматическая валидация JSON
- Проверка форматов файлов

### 4. Обработка ошибок

- Централизованная обработка исключений
- Правильные HTTP коды ошибок
- Логирование всех запросов в БД
- Graceful degradation

## Масштабируемость

### Текущая архитектура

- SQLite (подходит для разработки и малых нагрузок)
- Синхронная обработка запросов
- In-memory model loading

### Возможности масштабирования

1. **База данных**
   - Замена SQLite на PostgreSQL/MySQL
   - Connection pooling
   - Read replicas
   - Sharding по времени (history)

2. **ML модель**
   - Model serving (TorchServe, TensorFlow Serving)
   - GPU acceleration
   - Batch processing
   - Model caching

3. **API**
   - Horizontal scaling (multiple workers)
   - Load balancing (nginx, HAProxy)
   - Caching (Redis)
   - Rate limiting

4. **Мониторинг**
   - Prometheus metrics
   - Grafana dashboards
   - ELK stack для логов
   - Health checks

## Зависимости

### Production

```
FastAPI - веб-фреймворк
uvicorn - ASGI сервер
SQLAlchemy - ORM
alembic - миграции БД
pydantic - валидация данных
python-jose - JWT
passlib - хеширование паролей
torch/torchvision - ML модель
Pillow - обработка изображений
```

### Development

```
pytest - тестирование
black - форматирование кода
flake8 - линтинг
mypy - type checking
```

## Производительность

### Оптимизации

1. **Асинхронность**
   - Async/await для I/O операций
   - Асинхронная работа с БД
   - Non-blocking endpoints

2. **Database**
   - Индексы на часто запрашиваемые поля
   - Lazy loading для связей
   - Batch inserts

3. **ML Model**
   - Модель загружается один раз при старте
   - Batch prediction для нескольких изображений
   - GPU acceleration (если доступно)

### Метрики производительности

Endpoint `/stats` предоставляет:
- Среднее время обработки
- Медиана (50-й перцентиль)
- 95-й перцентиль
- 99-й перцентиль
- Характеристики входных данных

## Расширяемость

### Добавление новых моделей

1. Создайте новый класс модели в `app/ml_model.py`
2. Реализуйте метод `predict()`
3. Зарегистрируйте модель в роутере
4. Обновите схемы в `app/schemas.py`

### Добавление новых endpoints

1. Добавьте handler в `app/main.py`
2. Создайте Pydantic схемы в `app/schemas.py`
3. При необходимости обновите модели БД
4. Создайте миграцию через alembic

### Интеграция с внешними сервисами

1. Добавьте клиент в отдельный модуль
2. Используйте async HTTP клиент (httpx)
3. Добавьте retry logic и circuit breaker
4. Логируйте все внешние вызовы

## Тестирование

### Unit тесты

- Тесты для auth функций
- Тесты для ML модели
- Тесты для схем валидации

### Integration тесты

- Тесты endpoints
- Тесты БД операций
- Тесты авторизации

### E2E тесты

- Полный флоу регистрации → авторизации → запроса
- Тесты с реальными изображениями
- Тесты производительности

## Деплой

### Development

```bash
uvicorn app.main:app --reload
```

### Production

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Мониторинг и логирование

### Логи

- Request/Response логирование
- Error tracking
- Performance metrics
- Audit trail (история в БД)

### Метрики

- Request count
- Response times (mean, percentiles)
- Error rates
- Model predictions distribution

## Best Practices

1. **Код**
   - Понятные имена переменных и функций
   - Минимум комментариев, self-documenting code
   - Type hints везде
   - Async/await для I/O

2. **БД**
   - Используйте миграции для всех изменений схемы
   - Индексы на JOIN колонках
   - Не храните большие объекты в БД

3. **Безопасность**
   - Никогда не коммитьте .env файл
   - Используйте secrets management
   - Регулярно обновляйте зависимости
   - Валидируйте все входные данные

4. **API**
   - Версионирование API
   - Правильные HTTP коды
   - Понятные сообщения об ошибках
   - Документация (Swagger)
