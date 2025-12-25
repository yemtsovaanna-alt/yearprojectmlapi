# Тестирование ML Service API

## Автоматическое тестирование

### Запуск тестового скрипта

```bash
python test_api.py
```

Скрипт выполнит следующие тесты:
1. Регистрация администратора
2. Регистрация обычного пользователя
3. Авторизация
4. Отправка изображения на классификацию
5. Отправка JSON данных
6. Просмотр истории запросов
7. Просмотр статистики
8. Удаление истории (опционально)

## Ручное тестирование

### 1. Проверка работы сервера

```bash
curl http://localhost:8000/
```

Ожидаемый ответ:
```json
{
  "message": "ML Service API",
  "version": "1.0.0",
  "endpoints": {
    "POST /register": "Register a new user",
    "POST /token": "Get JWT access token",
    ...
  }
}
```

### 2. Регистрация пользователей

#### Администратор

```bash
curl -X POST "http://localhost:8000/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123",
    "is_admin": true
  }'
```

#### Обычный пользователь

```bash
curl -X POST "http://localhost:8000/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "user1",
    "password": "user123",
    "is_admin": false
  }'
```

### 3. Получение JWT токена

```bash
curl -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

Сохраните полученный `access_token`.

### 4. Тестирование POST /forward

#### С изображением

Создайте тестовое изображение или используйте существующее:

```bash
curl -X POST "http://localhost:8000/forward" \
  -F "image=@test_image.jpg"
```

Ожидаемый ответ (200 OK):
```json
{
  "result": {
    "predictions": [
      {
        "class": "golden_retriever",
        "probability": 0.8234
      }
    ],
    "top_class": "golden_retriever",
    "top_probability": 0.8234
  }
}
```

#### С JSON данными

```bash
curl -X POST "http://localhost:8000/forward" \
  -F 'data={"text": "test data", "value": 123}'
```

Ожидаемый ответ (200 OK):
```json
{
  "result": {
    "message": "JSON data processed",
    "received_data": {
      "text": "test data",
      "value": 123
    }
  }
}
```

#### Тест ошибки 400 (bad request)

```bash
curl -X POST "http://localhost:8000/forward"
```

Ожидаемый ответ (400 Bad Request):
```json
{
  "detail": "bad request"
}
```

#### Тест ошибки 403 (модель не смогла обработать)

Отправьте некорректный файл (не изображение):

```bash
curl -X POST "http://localhost:8000/forward" \
  -F "image=@text_file.txt"
```

Ожидаемый ответ (403 Forbidden):
```json
{
  "detail": "модель не смогла обработать данные"
}
```

### 5. Тестирование GET /history

Требует JWT токен администратора:

```bash
TOKEN="ваш_jwt_токен"

curl -X GET "http://localhost:8000/history" \
  -H "Authorization: Bearer $TOKEN"
```

Ожидаемый ответ (200 OK):
```json
{
  "total": 5,
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

#### Тест без авторизации

```bash
curl -X GET "http://localhost:8000/history"
```

Ожидаемый ответ (401 Unauthorized):
```json
{
  "detail": "Not authenticated"
}
```

#### Тест с пользователем без прав администратора

```bash
curl -X POST "http://localhost:8000/token" \
  -d "username=user1&password=user123"

# Используйте полученный токен
curl -X GET "http://localhost:8000/history" \
  -H "Authorization: Bearer $USER_TOKEN"
```

Ожидаемый ответ (403 Forbidden):
```json
{
  "detail": "Not enough permissions"
}
```

### 6. Тестирование GET /stats

Требует JWT токен администратора:

```bash
TOKEN="ваш_jwt_токен"

curl -X GET "http://localhost:8000/stats" \
  -H "Authorization: Bearer $TOKEN"
```

Ожидаемый ответ (200 OK):
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

### 7. Тестирование DELETE /history

Требует admin token из переменных окружения:

```bash
curl -X DELETE "http://localhost:8000/history" \
  -H "Authorization: Bearer admin_secret_token_12345"
```

Ожидаемый ответ (204 No Content) - пустое тело ответа.

#### Тест с неверным токеном

```bash
curl -X DELETE "http://localhost:8000/history" \
  -H "Authorization: Bearer wrong_token"
```

Ожидаемый ответ (403 Forbidden):
```json
{
  "detail": "Invalid admin token"
}
```

#### Тест без заголовка Authorization

```bash
curl -X DELETE "http://localhost:8000/history"
```

Ожидаемый ответ (401 Unauthorized):
```json
{
  "detail": "Authorization header required"
}
```

## Тестирование через Swagger UI

1. Откройте http://localhost:8000/docs
2. Используйте интерактивный интерфейс для тестирования endpoints
3. Для защищенных endpoints:
   - Нажмите кнопку "Authorize" в правом верхнем углу
   - Введите username и password
   - Нажмите "Authorize"
   - Теперь можете тестировать защищенные endpoints

## Нагрузочное тестирование

### С использованием Apache Bench

```bash
ab -n 1000 -c 10 http://localhost:8000/
```

### С использованием wrk

```bash
wrk -t12 -c400 -d30s http://localhost:8000/
```

## Проверка базы данных

### Просмотр таблиц

```bash
sqlite3 ml_service.db

.tables
.schema request_history
.schema users

SELECT * FROM users;
SELECT * FROM request_history LIMIT 10;
```

## Проверка миграций

### Текущая версия БД

```bash
alembic current
```

### История миграций

```bash
alembic history
```

### Применение миграций

```bash
alembic upgrade head
```

### Откат миграции

```bash
alembic downgrade -1
```

## Чек-лист тестирования

- [ ] Сервер запускается без ошибок
- [ ] Root endpoint (/) возвращает информацию
- [ ] Регистрация пользователя работает
- [ ] Регистрация администратора работает
- [ ] Повторная регистрация с тем же username возвращает ошибку
- [ ] Авторизация с правильными credentials работает
- [ ] Авторизация с неправильными credentials возвращает 401
- [ ] POST /forward с изображением возвращает предсказания
- [ ] POST /forward с JSON данными работает
- [ ] POST /forward без данных возвращает 400
- [ ] POST /forward с некорректным изображением возвращает 403
- [ ] GET /history требует авторизацию
- [ ] GET /history с токеном администратора возвращает данные
- [ ] GET /history с токеном обычного пользователя возвращает 403
- [ ] GET /stats требует авторизацию
- [ ] GET /stats возвращает корректную статистику
- [ ] DELETE /history с правильным admin token работает
- [ ] DELETE /history с неправильным токеном возвращает 403
- [ ] DELETE /history без заголовка Authorization возвращает 401
- [ ] Все запросы логируются в базу данных
- [ ] Swagger UI доступен и работает
- [ ] ReDoc доступен и работает

## Отладка

### Включение debug режима

В `app/main.py` измените:

```python
app = FastAPI(title="ML Service API", version="1.0.0", debug=True)
```

### Просмотр логов

```bash
uvicorn app.main:app --reload --log-level debug
```

### Проверка зависимостей

```bash
pip list
pip check
```

## Известные проблемы

1. **Модель долго загружается при первом запуске**
   - Это нормально, ResNet50 загружает веса из интернета
   - При повторных запусках использует кеш

2. **Ошибка при обработке больших изображений**
   - Убедитесь, что изображение не превышает размер 10MB
   - Можно настроить лимит в FastAPI

3. **JWT токен истекает**
   - Настройте время жизни в `.env` (JWT_EXPIRATION_MINUTES)
   - Получите новый токен через /token

## Полезные команды

```bash
# Очистка базы данных
rm ml_service.db

# Пересоздание базы данных
alembic upgrade head

# Проверка синтаксиса Python
python -m py_compile app/*.py

# Форматирование кода (если установлен black)
black app/

# Проверка типов (если установлен mypy)
mypy app/
```
