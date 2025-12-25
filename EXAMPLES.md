# Примеры использования API

## Python примеры

### 1. Регистрация и авторизация

```python
import requests

BASE_URL = "http://localhost:8000"

# Регистрация администратора
response = requests.post(
    f"{BASE_URL}/register",
    json={
        "username": "admin",
        "password": "admin123",
        "is_admin": True
    }
)
print(response.json())

# Получение токена
response = requests.post(
    f"{BASE_URL}/token",
    data={
        "username": "admin",
        "password": "admin123"
    }
)
token = response.json()["access_token"]
print(f"Access Token: {token}")
```

### 2. Классификация изображения

```python
import requests

# Загрузка изображения
with open("cat.jpg", "rb") as f:
    response = requests.post(
        f"{BASE_URL}/forward",
        files={"image": f}
    )

result = response.json()
print(f"Top prediction: {result['result']['top_class']}")
print(f"Confidence: {result['result']['top_probability']:.2%}")
```

### 3. Отправка JSON данных

```python
import requests
import json

data = {
    "text": "Hello, world!",
    "number": 42,
    "nested": {"key": "value"}
}

response = requests.post(
    f"{BASE_URL}/forward",
    files={"data": json.dumps(data)}
)

print(response.json())
```

### 4. Просмотр истории (требует авторизацию)

```python
import requests

headers = {"Authorization": f"Bearer {token}"}

response = requests.get(
    f"{BASE_URL}/history",
    headers=headers
)

history = response.json()
print(f"Total requests: {history['total']}")

for item in history['items'][:5]:
    print(f"- {item['request_type']}: {item['processing_time']:.3f}s")
```

### 5. Получение статистики (требует авторизацию)

```python
import requests

headers = {"Authorization": f"Bearer {token}"}

response = requests.get(
    f"{BASE_URL}/stats",
    headers=headers
)

stats = response.json()
print(f"Total requests: {stats['total_requests']}")
print(f"Mean processing time: {stats['mean_processing_time']:.3f}s")
print(f"95th percentile: {stats['percentile_95_processing_time']:.3f}s")
print(f"99th percentile: {stats['percentile_99_processing_time']:.3f}s")
```

### 6. Удаление истории (требует admin token)

```python
import requests

headers = {"Authorization": "Bearer admin_secret_token_12345"}

response = requests.delete(
    f"{BASE_URL}/history",
    headers=headers
)

if response.status_code == 204:
    print("History deleted successfully")
```

## cURL примеры

### Регистрация пользователя

```bash
curl -X POST "http://localhost:8000/register" \
  -H "Content-Type: application/json" \
  -d '{"username": "user1", "password": "pass123", "is_admin": false}'
```

### Получение JWT токена

```bash
curl -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

### Отправка изображения

```bash
curl -X POST "http://localhost:8000/forward" \
  -F "image=@/path/to/image.jpg"
```

### Отправка JSON данных

```bash
curl -X POST "http://localhost:8000/forward" \
  -F 'data={"key": "value", "number": 123}'
```

### Просмотр истории

```bash
TOKEN="your_jwt_token_here"

curl -X GET "http://localhost:8000/history" \
  -H "Authorization: Bearer $TOKEN"
```

### Просмотр статистики

```bash
TOKEN="your_jwt_token_here"

curl -X GET "http://localhost:8000/stats" \
  -H "Authorization: Bearer $TOKEN"
```

### Удаление истории

```bash
curl -X DELETE "http://localhost:8000/history" \
  -H "Authorization: Bearer admin_secret_token_12345"
```

## JavaScript примеры

### Отправка изображения

```javascript
const formData = new FormData();
formData.append('image', fileInput.files[0]);

fetch('http://localhost:8000/forward', {
  method: 'POST',
  body: formData
})
  .then(response => response.json())
  .then(data => {
    console.log('Prediction:', data.result.top_class);
    console.log('Confidence:', data.result.top_probability);
  });
```

### Получение статистики

```javascript
const token = 'your_jwt_token_here';

fetch('http://localhost:8000/stats', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
})
  .then(response => response.json())
  .then(stats => {
    console.log('Total requests:', stats.total_requests);
    console.log('Mean time:', stats.mean_processing_time);
  });
```

## Обработка ошибок

### Python

```python
import requests

try:
    response = requests.post(
        "http://localhost:8000/forward",
        files={"image": open("test.jpg", "rb")}
    )
    response.raise_for_status()
    result = response.json()
    print(result)
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 400:
        print("Bad request - check your input")
    elif e.response.status_code == 403:
        print("Model could not process data")
    else:
        print(f"Error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Пакетная обработка изображений

```python
import requests
from pathlib import Path

image_folder = Path("images")
results = []

for image_path in image_folder.glob("*.jpg"):
    with open(image_path, "rb") as f:
        response = requests.post(
            "http://localhost:8000/forward",
            files={"image": f}
        )
        if response.status_code == 200:
            result = response.json()
            results.append({
                "filename": image_path.name,
                "prediction": result["result"]["top_class"],
                "confidence": result["result"]["top_probability"]
            })

for r in results:
    print(f"{r['filename']}: {r['prediction']} ({r['confidence']:.2%})")
```
