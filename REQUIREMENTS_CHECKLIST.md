# Чек-лист требований проекта

## Основные требования (10 баллов)

### POST /forward endpoint

**Требование:** Route типа POST на /forward, который принимает два формата данных

**Реализация:**
- **JSON формат** (для данных без изображений):
  - Принимает данные через multipart/form-data параметр `data`
  - Файл: `app/main.py:92-146`
  - Пример использования: `curl -X POST /forward -F 'data={"key": "value"}'`

- **Multipart/form-data формат** (для изображений):
  - Параметр `image` для изображения
  - Файл: `app/main.py:92-146`
  - Пример использования: `curl -X POST /forward -F "image=@test.jpg"`

### Обработка ошибок

**Требование:** Правильные коды ответов для разных ситуаций

**Реализация:**
- **400 Bad Request** - неверный формат запроса:
  - Файл: `app/main.py:132-134`
  - Возвращает `{"detail": "bad request"}`

- **403 Forbidden** - модель не смогла обработать данные:
  - Файл: `app/main.py:107-110`
  - Возвращает `{"detail": "модель не смогла обработать данные"}`

- **200 OK** - успешная обработка:
  - Файл: `app/main.py:111-120` (изображения)
  - Файл: `app/main.py:121-145` (JSON)

### Формат ответа

**Требование:** Результаты в подходящем формате

**Реализация:**
- **JSON для данных без изображений**:
  - Схема: `app/schemas.py:ForwardResponse`
  - Возвращает результат в поле `result`

- **JSON для изображений**:
  - Результат классификации в JSON формате
  - Включает предсказания, класс, вероятность
  - Файл: `app/main.py:115-120`

---

## GET /history (5 баллов)

**Требование:** Показывать историю всех запросов из базы данных

**Реализация:**
- Endpoint реализован: `app/main.py:182-195`
- Модель БД: `app/models.py:RequestHistory`
- Хранит:
  - Тип запроса (image/json)
  - Время обработки
  - Размер входных данных
  - Размеры изображения (ширина/высота)
  - Код статуса
  - Результат
  - Сообщение об ошибке
  - Время создания
- Возвращает список всех запросов с деталями
- Требует JWT авторизацию администратора
- Схема ответа: `app/schemas.py:HistoryResponse`

**Пример использования:**
```bash
curl -X GET http://localhost:8000/history \
  -H "Authorization: Bearer JWT_TOKEN"
```

---

## DELETE /history (2 балла, PRO)

**Требование:** Удаление истории с подтверждающим токеном

**Реализация:**
- Endpoint реализован: `app/main.py:198-206`
- Требует admin token в заголовке `Authorization`
- Верификация токена: `app/auth.py:verify_admin_token`
- Токен настраивается через `.env` файл (`ADMIN_TOKEN`)
- Возвращает 204 No Content при успехе
- Возвращает 401/403 при неверном токене

**Пример использования:**
```bash
curl -X DELETE http://localhost:8000/history \
  -H "Authorization: Bearer admin_secret_token_12345"
```

---

## GET /stats (5 баллов)

**Требование:** Статистика запросов с метриками

**Реализация:**
- Endpoint реализован: `app/main.py:209-251`
- **Время обработки**:
  - Среднее (mean)
  - Медиана (50-й перцентиль)
  - 95-й перцентиль
  - 99-й перцентиль
  - Реализация: `app/main.py:234-237`

- **Характеристики входных запросов**:
  - Средний размер данных
  - Средняя ширина изображений
  - Средняя высота изображений
  - Реализация: `app/main.py:239-241`

- Использует NumPy для расчета квантилей
- Требует JWT авторизацию администратора
- Схема ответа: `app/schemas.py:StatsResponse`

**Пример использования:**
```bash
curl -X GET http://localhost:8000/stats \
  -H "Authorization: Bearer JWT_TOKEN"
```

**Пример ответа:**
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

---

## JWT авторизация (3 балла, PRO)

**Требование:** Механизм авторизации при помощи JWT с ролями

**Реализация:**
- **JWT токены**:
  - Создание: `app/auth.py:create_access_token`
  - Валидация: `app/auth.py:get_current_user`
  - Использует `python-jose` для работы с JWT
  - Настраиваемое время жизни (default: 30 минут)

- **Роли пользователей**:
  - User (обычный пользователь)
  - Admin (администратор)
  - Модель: `app/models.py:User`
  - Поле `is_admin` в таблице users

- **Endpoints с авторизацией**:
  - `POST /register` - регистрация пользователей
  - `POST /token` - получение JWT токена
  - `GET /history` - только для администраторов
  - `GET /stats` - только для администраторов

- **Хеширование паролей**:
  - Использует bcrypt через passlib
  - Файл: `app/auth.py:get_password_hash`

- **Dependency injection**:
  - `get_current_user` - получение текущего пользователя
  - `get_current_admin_user` - проверка прав администратора
  - Файл: `app/auth.py:59-85`

**Пример использования:**
```bash
# Регистрация администратора
curl -X POST http://localhost:8000/register \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123", "is_admin": true}'

# Получение токена
curl -X POST http://localhost:8000/token \
  -d "username=admin&password=admin123"

# Использование токена
curl -X GET http://localhost:8000/history \
  -H "Authorization: Bearer TOKEN"
```

---

## Alembic миграции (5 баллов, PRO)

**Требование:** Механизм миграций базы данных при помощи alembic

**Реализация:**
- **Конфигурация Alembic**:
  - Файл: `alembic.ini`
  - Environment: `alembic/env.py`
  - Template: `alembic/script.py.mako`

- **Миграции**:
  - Папка: `alembic/versions/`
  - Начальная миграция: `alembic/versions/001_initial_migration.py`
  - Создает таблицы: `users`, `request_history`
  - Создает индексы

- **Асинхронная поддержка**:
  - Использует `async_engine_from_config`
  - Поддержка SQLAlchemy 2.0
  - Файл: `alembic/env.py:45-59`

- **Функции миграций**:
  - `upgrade()` - применение миграции
  - `downgrade()` - откат миграции
  - Offline режим поддерживается

**Команды:**
```bash
# Применение миграций
alembic upgrade head

# Создание новой миграции
alembic revision --autogenerate -m "description"

# Откат миграции
alembic downgrade -1

# История миграций
alembic history
```

---

## Дополнительные возможности

### Документация

- **README.md** - основная документация
- **QUICKSTART.md** - быстрый старт
- **EXAMPLES.md** - примеры использования
- **ARCHITECTURE.md** - архитектура проекта
- **TESTING.md** - руководство по тестированию

### ML модель

- **ResNet50** предобученная на ImageNet
- **Preprocessing pipeline**:
  - Resize 256x256
  - Center crop 224x224
  - Нормализация
- **Top-K предсказания** (default: 5)
- **Обработка ошибок** при некорректных изображениях

### Вспомогательные скрипты

- **create_admin.py** - создание администратора
- **test_api.py** - автоматическое тестирование API

### Контейнеризация

- **Dockerfile** - для деплоя
- **docker-compose.yml** - для локального запуска
- **.dockerignore** - исключение файлов

### Безопасность

- Хеширование паролей (bcrypt)
- JWT токены с истечением
- Разделение прав доступа
- Валидация входных данных
- .env для секретов (не в git)

### База данных

- Асинхронная работа (aiosqlite)
- SQLAlchemy ORM
- Индексы на часто используемых полях
- Логирование всех запросов

---

## Итоговая оценка

| Требование | Баллы | Статус |
|-----------|-------|--------|
| POST /forward | 10 | Выполнено |
| GET /history | 5 | Выполнено |
| DELETE /history (PRO) | 2 | Выполнено |
| GET /stats | 5 | Выполнено |
| JWT авторизация (PRO) | 3 | Выполнено |
| Alembic миграции (PRO) | 5 | Выполнено |
| **ИТОГО** | **30** | **Все выполнено** |

---

## Структура файлов

```
fastapitask/
├── app/
│   ├── __init__.py             # Инициализация пакета
│   ├── main.py                 # Основное приложение
│   ├── config.py               # Конфигурация
│   ├── database.py             # База данных
│   ├── models.py               # ORM модели
│   ├── schemas.py              # Pydantic схемы
│   ├── auth.py                 # JWT авторизация
│   ├── ml_model.py             # ML модель
│   └── imagenet_classes.json   # Классы ImageNet
├── alembic/
│   ├── versions/
│   │   └── 001_initial_migration.py  # Начальная миграция
│   ├── env.py                  # Alembic окружение
│   └── script.py.mako          # Шаблон миграций
├── alembic.ini                 # Конфигурация Alembic
├── requirements.txt            # Зависимости
├── .env                        # Переменные окружения
├── .env.example                # Пример переменных
├── .gitignore                  # Git ignore
├── Dockerfile                  # Docker образ
├── docker-compose.yml          # Docker Compose
├── .dockerignore               # Docker ignore
├── create_admin.py             # Создание администратора
├── test_api.py                 # Тестирование API
├── README.md                   # Основная документация
├── QUICKSTART.md               # Быстрый старт
├── EXAMPLES.md                 # Примеры использования
├── ARCHITECTURE.md             # Архитектура
├── TESTING.md                  # Тестирование
└── REQUIREMENTS_CHECKLIST.md   # Этот файл
```

## Команды для проверки

```bash
# Установка
pip install -r requirements.txt

# Миграции
alembic upgrade head

# Запуск
uvicorn app.main:app --reload

# Тестирование
python test_api.py

# Документация
open http://localhost:8000/docs
```

Все требования проекта выполнены!
