import requests
import json
from io import BytesIO
from PIL import Image
import numpy as np


BASE_URL = "http://localhost:8000"


def create_test_image():
    img_array = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
    img = Image.fromarray(img_array)
    img_bytes = BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    return img_bytes


def test_register_user():
    print("\n=== Testing User Registration ===")
    response = requests.post(
        f"{BASE_URL}/register",
        json={
            "username": "testuser",
            "password": "testpass123",
            "is_admin": False
        }
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.json()


def test_register_admin():
    print("\n=== Testing Admin Registration ===")
    response = requests.post(
        f"{BASE_URL}/register",
        json={
            "username": "admin",
            "password": "admin123",
            "is_admin": True
        }
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.json()


def test_login(username: str, password: str):
    print(f"\n=== Testing Login for {username} ===")
    response = requests.post(
        f"{BASE_URL}/token",
        data={
            "username": username,
            "password": password
        }
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.json()


def test_forward_image():
    print("\n=== Testing POST /forward with Image ===")
    img_bytes = create_test_image()
    response = requests.post(
        f"{BASE_URL}/forward",
        files={"image": ("test.jpg", img_bytes, "image/jpeg")}
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.json()


def test_forward_json():
    print("\n=== Testing POST /forward with JSON ===")
    test_data = {"text": "sample text", "value": 42, "nested": {"key": "value"}}
    response = requests.post(
        f"{BASE_URL}/forward",
        files={"data": json.dumps(test_data)}
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.json()


def test_history(token: str):
    print("\n=== Testing GET /history ===")
    response = requests.get(
        f"{BASE_URL}/history",
        headers={"Authorization": f"Bearer {token}"}
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.json()


def test_stats(token: str):
    print("\n=== Testing GET /stats ===")
    response = requests.get(
        f"{BASE_URL}/stats",
        headers={"Authorization": f"Bearer {token}"}
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.json()


def test_delete_history(admin_token: str):
    print("\n=== Testing DELETE /history ===")
    response = requests.delete(
        f"{BASE_URL}/history",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    print(f"Status Code: {response.status_code}")
    if response.status_code == 204:
        print("History deleted successfully")
    else:
        print(f"Response: {response.text}")


def main():
    print("=" * 60)
    print("ML Service API Testing Script")
    print("=" * 60)

    try:
        test_register_admin()
    except Exception as e:
        print(f"Admin already exists or error: {e}")

    try:
        test_register_user()
    except Exception as e:
        print(f"User already exists or error: {e}")

    admin_token_response = test_login("admin", "admin123")
    admin_token = admin_token_response.get("access_token")

    test_forward_image()
    test_forward_image()
    test_forward_json()

    if admin_token:
        test_history(admin_token)
        test_stats(admin_token)

        confirm = input("\nDo you want to delete history? (yes/no): ")
        if confirm.lower() == "yes":
            test_delete_history("admin_secret_token_12345")

    print("\n" + "=" * 60)
    print("Testing completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
