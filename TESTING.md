# Тестирование ML Service API

## Ручное тестирование

### 1. Проверка работы сервера

```bash
curl http://localhost:8000/
```

Ожидаемый ответ:
```json
{
  "message": "ML Service API - Log Anomaly Detection",
  "version": "1.0.0",
  "endpoints": {
    "POST /register": "Register a new user",
    "POST /token": "Get JWT access token",
    "POST /forward": "Detect anomalies in log sequence (Isolation Forest)",
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

#### С нормальными логами

```bash
cat test_logs/normal_logs.json | curl -X POST "http://localhost:8000/forward" \
  -H "Content-Type: application/json" \
  -d @-
```

Ожидаемый ответ (200 OK):
```json
{
  "score": -0.5814839173818528,
  "is_anomaly": false,
  "threshold": -0.5827027071289144,
  "num_events": 8
}
```

#### С аномальными логами

```bash
cat test_logs/anomaly_logs.json | curl -X POST "http://localhost:8000/forward" \
  -H "Content-Type: application/json" \
  -d @-
```

Ожидаемый ответ (200 OK):
```json
{
  "score": -0.6472622282626409,
  "is_anomaly": true,
  "threshold": -0.5827027071289144,
  "num_events": 8
}
```

#### Тест ошибки 422 (validation error)

```bash
curl -X POST "http://localhost:8000/forward" \
  -H "Content-Type: application/json" \
  -d '{"logs": []}'
```

Ожидаемый ответ (422 Unprocessable Entity):
```json
{
  "detail": [
    {
      "type": "too_short",
      "loc": ["body", "logs"],
      "msg": "List should have at least 1 item after validation, not 0"
    }
  ]
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
      "request_type": "log_anomaly_detection",
      "processing_time": 0.023,
      "input_data_size": 8,
      "image_width": null,
      "image_height": null,
      "status_code": 200,
      "result": "...",
      "error_message": null,
      "created_at": "2025-12-25T10:30:00"
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
  "mean_processing_time": 0.025,
  "median_processing_time": 0.023,
  "percentile_95_processing_time": 0.045,
  "percentile_99_processing_time": 0.089,
  "average_input_size": 8.5,
  "average_image_width": null,
  "average_image_height": null
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

## Тестирование через Swagger UI

1. Откройте http://localhost:8000/docs
2. Используйте интерактивный интерфейс для тестирования endpoints
3. Для защищенных endpoints:
   - Нажмите кнопку "Authorize" в правом верхнем углу
   - Введите username и password
   - Нажмите "Authorize"
   - Теперь можете тестировать защищенные endpoints

## Тестовые файлы

В папке `test_logs/` находятся готовые тестовые файлы:

| Файл | Описание | Ожидаемый результат |
|------|----------|---------------------|
| normal_logs.json | Нормальные HDFS логи | is_anomaly: false |
| normal_logs_2.json | Нормальные логи (вариант 2) | is_anomaly: false |
| anomaly_logs.json | Логи с ошибками | is_anomaly: true |
| anomaly_logs_2.json | Логи с ошибками (вариант 2) | is_anomaly: true |

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
- [ ] POST /forward с нормальными логами возвращает is_anomaly: false
- [ ] POST /forward с аномальными логами возвращает is_anomaly: true
- [ ] POST /forward с пустым списком возвращает 422
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

1. **Модель не загружена (503)**
   - Убедитесь, что файл `models/isolation_forest.joblib` существует
   - Проверьте права доступа к файлу

2. **JWT токен истекает**
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
