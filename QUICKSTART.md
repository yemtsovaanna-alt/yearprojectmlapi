# Быстрый старт

## 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

## 2. Применение миграций

```bash
alembic upgrade head
```

## 3. Создание администратора

```bash
python create_admin.py
```

Введите имя пользователя: `admin`
Введите пароль: `admin123`

## 4. Запуск сервера

```bash
uvicorn app.main:app --reload
```

## 5. Тестирование API

### Вариант 1: Swagger UI

Откройте в браузере: http://localhost:8000/docs

### Вариант 2: Скрипт тестирования

```bash
python test_api.py
```

### Вариант 3: cURL команды

#### Получение токена

```bash
curl -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

#### Отправка изображения

```bash
curl -X POST "http://localhost:8000/forward" \
  -F "image=@path/to/your/image.jpg"
```

#### Просмотр истории

```bash
curl -X GET "http://localhost:8000/history" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

#### Просмотр статистики

```bash
curl -X GET "http://localhost:8000/stats" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## Порты

- API: http://localhost:8000
- Документация: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Переменные окружения

Настройте в файле `.env`:

```
DATABASE_URL=sqlite+aiosqlite:///./ml_service.db
SECRET_KEY=your-secret-key-here
ADMIN_TOKEN=your-admin-token-here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=30
```

## Готово!

Сервис запущен и готов к использованию.
