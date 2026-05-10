import os
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

SERVER_URL = os.getenv("SERVER_URL", "http://localhost:8000")

_CAMERA_COLS = ["id", "team_id", "team_name", "category", "confidence", "kg_amount", "price", "created_at"]
_READING_COLS = ["id", "team_id", "team_name", "user_id", "user_name", "category", "kg_amount", "created_at"]
_GOAL_COLS = ["id", "team_id", "team_name", "category", "target_kg"]
_TEAM_COLS = ["id", "name"]
_USER_COLS = ["id", "name", "email", "role", "team_id"]


_API_ERROR = object()


def _get(path, token=None, params=None):
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        r = requests.get(f"{SERVER_URL}{path}", headers=headers, params=params, timeout=10)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.RequestException:
        return _API_ERROR
    except Exception:
        return []


def _to_df(data, cols):
    if not data:
        return pd.DataFrame(columns=cols)
    return pd.DataFrame(data)


# ── Pública (sem auth) ────────────────────────────────────────────────────────

def get_public_camera_readings(category=None, from_date=None, to_date=None):
    params = {k: v for k, v in {"category": category, "from_date": from_date, "to_date": to_date}.items() if v}
    data = _get("/api/public/camera-readings", params=params)
    if data is _API_ERROR:
        return _API_ERROR
    df = _to_df(data, _CAMERA_COLS)
    if not df.empty and "price" in df.columns:
        df["price"] = df["price"].fillna(0.0)
    return df


def get_public_camera_kpis(category=None, from_date=None, to_date=None) -> dict:
    df = get_public_camera_readings(category=category, from_date=from_date, to_date=to_date)
    if df is _API_ERROR or df.empty:
        return {"total_kg": 0.0, "total_price": 0.0, "total_count": 0, "avg_confidence": 0.0}
    return {
        "total_kg": round(float(df["kg_amount"].sum()), 2),
        "total_price": round(float(df["price"].sum()), 2),
        "total_count": len(df),
        "avg_confidence": round(float(df["confidence"].mean()) * 100, 1),
    }


# ── Câmera (admin) ────────────────────────────────────────────────────────────

def get_camera_readings(token, team_id=None, category=None, from_date=None, to_date=None) -> pd.DataFrame:
    params = {k: v for k, v in {"team_id": team_id, "category": category, "from_date": from_date, "to_date": to_date}.items() if v is not None}
    data = _get("/api/camera-readings", token=token, params=params)
    df = _to_df(data, _CAMERA_COLS)
    if not df.empty and "price" in df.columns:
        df["price"] = df["price"].fillna(0.0)
    return df


def get_camera_kpis(token, team_id=None, category=None, from_date=None, to_date=None) -> dict:
    df = get_camera_readings(token, team_id=team_id, category=category, from_date=from_date, to_date=to_date)
    if df.empty:
        return {"total_kg": 0.0, "total_price": 0.0, "total_count": 0, "avg_confidence": 0.0}
    return {
        "total_kg": round(float(df["kg_amount"].sum()), 2),
        "total_price": round(float(df["price"].sum()), 2),
        "total_count": len(df),
        "avg_confidence": round(float(df["confidence"].mean()) * 100, 1),
    }


# ── App ───────────────────────────────────────────────────────────────────────

def get_readings(token, team_id=None, category=None, from_date=None, to_date=None) -> pd.DataFrame:
    params = {k: v for k, v in {"team_id": team_id, "category": category, "from_date": from_date, "to_date": to_date}.items() if v is not None}
    data = _get("/api/readings", token=token, params=params)
    return _to_df(data, _READING_COLS)


def get_readings_kpis(token, team_id=None, category=None, from_date=None, to_date=None) -> dict:
    df = get_readings(token, team_id=team_id, category=category, from_date=from_date, to_date=to_date)
    if df.empty:
        return {"total_kg": 0.0, "total_count": 0}
    return {
        "total_kg": round(float(df["kg_amount"].sum()), 2),
        "total_count": len(df),
    }


# ── Metas ─────────────────────────────────────────────────────────────────────

def get_goals(token, team_id=None) -> pd.DataFrame:
    params = {}
    if team_id:
        params["team_id"] = team_id
    data = _get("/api/goals", token=token, params=params)
    return _to_df(data, _GOAL_COLS)


# ── Equipes / Usuários ────────────────────────────────────────────────────────

def get_teams() -> pd.DataFrame:
    data = _get("/api/teams")
    df = _to_df(data, _TEAM_COLS)
    if not df.empty and "active" in df.columns:
        df = df[df["active"] == True]
    return df


def get_users(token) -> pd.DataFrame:
    data = _get("/api/users", token=token)
    df = _to_df(data, _USER_COLS)
    if not df.empty and "active" in df.columns:
        df = df[df["active"] == True]
    return df


# ── Comparação App vs Câmera ──────────────────────────────────────────────────

def get_comparison(token, team_id=None, from_date=None, to_date=None) -> pd.DataFrame:
    df_app = get_readings(token, team_id=team_id, from_date=from_date, to_date=to_date)
    df_cam = get_camera_readings(token, team_id=team_id, from_date=from_date, to_date=to_date)

    categories = ["arroz", "feijao", "macarrao", "acucar", "fuba", "oleo", "outros"]
    rows = []
    for cat in categories:
        kg_app = float(df_app[df_app["category"] == cat]["kg_amount"].sum()) if not df_app.empty else 0.0
        kg_cam = float(df_cam[df_cam["category"] == cat]["kg_amount"].sum()) if not df_cam.empty else 0.0
        diff_kg = kg_cam - kg_app
        diff_pct = ((kg_cam - kg_app) / kg_app * 100) if kg_app > 0 else 0.0
        rows.append({
            "category": cat,
            "kg_app": round(kg_app, 2),
            "kg_camera": round(kg_cam, 2),
            "diff_kg": round(diff_kg, 2),
            "diff_pct": round(diff_pct, 1),
        })
    return pd.DataFrame(rows)
