import os
import requests
from dotenv import load_dotenv

load_dotenv()

SERVER_URL = os.getenv("SERVER_URL", "http://localhost:8000")


def validate_login(email: str, password: str) -> dict | None:
    """Retorna {'token': str, 'email': str} se válido, None se inválido."""
    try:
        r = requests.post(
            f"{SERVER_URL}/api/auth/login",
            json={"email": email, "password": password},
            timeout=6,
        )
        if r.status_code == 200:
            data = r.json()
            token = data.get("access_token") or data.get("token")
            if token:
                return {"token": token, "email": email}
        return None
    except Exception:
        return None


def is_authenticated(auth_data: dict | None) -> bool:
    return bool(auth_data and auth_data.get("token"))
