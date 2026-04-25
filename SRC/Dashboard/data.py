import pandas as pd
from sqlalchemy import text
from db import get_engine


def _conn():
    return get_engine().connect()


# ── Câmera ────────────────────────────────────────────────────────────────────

def get_camera_readings(team_id=None, category=None, from_date=None, to_date=None) -> pd.DataFrame:
    q = """
        SELECT cr.id, cr.team_id, t.name AS team_name, cr.category,
               cr.confidence, cr.kg_amount, COALESCE(cr.price, 0.0) AS price,
               cr.created_at
        FROM camera_readings cr
        JOIN teams t ON cr.team_id = t.id
        WHERE 1=1
    """
    params = {}
    if team_id:
        q += " AND cr.team_id = :team_id"
        params["team_id"] = team_id
    if category:
        q += " AND cr.category = :category"
        params["category"] = category
    if from_date:
        q += " AND cr.created_at >= :from_date"
        params["from_date"] = from_date
    if to_date:
        q += " AND cr.created_at <= :to_date"
        params["to_date"] = to_date
    q += " ORDER BY cr.created_at DESC"
    with _conn() as conn:
        return pd.read_sql(text(q), conn, params=params)


def get_camera_kpis(team_id=None, category=None, from_date=None, to_date=None) -> dict:
    df = get_camera_readings(team_id=team_id, category=category,
                             from_date=from_date, to_date=to_date)
    if df.empty:
        return {"total_kg": 0.0, "total_price": 0.0, "total_count": 0, "avg_confidence": 0.0}
    return {
        "total_kg": round(float(df["kg_amount"].sum()), 2),
        "total_price": round(float(df["price"].sum()), 2),
        "total_count": len(df),
        "avg_confidence": round(float(df["confidence"].mean()) * 100, 1),
    }


# ── App ───────────────────────────────────────────────────────────────────────

def get_readings(team_id=None, category=None, from_date=None, to_date=None) -> pd.DataFrame:
    q = """
        SELECT r.id, r.team_id, t.name AS team_name,
               r.user_id, u.name AS user_name,
               r.category, r.kg_amount, r.created_at
        FROM readings r
        JOIN teams t ON r.team_id = t.id
        LEFT JOIN users u ON r.user_id = u.id
        WHERE 1=1
    """
    params = {}
    if team_id:
        q += " AND r.team_id = :team_id"
        params["team_id"] = team_id
    if category:
        q += " AND r.category = :category"
        params["category"] = category
    if from_date:
        q += " AND r.created_at >= :from_date"
        params["from_date"] = from_date
    if to_date:
        q += " AND r.created_at <= :to_date"
        params["to_date"] = to_date
    q += " ORDER BY r.created_at DESC"
    with _conn() as conn:
        return pd.read_sql(text(q), conn, params=params)


def get_readings_kpis(team_id=None, category=None, from_date=None, to_date=None) -> dict:
    df = get_readings(team_id=team_id, category=category,
                      from_date=from_date, to_date=to_date)
    if df.empty:
        return {"total_kg": 0.0, "total_count": 0}
    return {
        "total_kg": round(float(df["kg_amount"].sum()), 2),
        "total_count": len(df),
    }


# ── Metas ─────────────────────────────────────────────────────────────────────

def get_goals(team_id=None) -> pd.DataFrame:
    q = """
        SELECT g.id, g.team_id, t.name AS team_name,
               g.category, g.target_kg
        FROM goals g
        JOIN teams t ON g.team_id = t.id
        WHERE 1=1
    """
    params = {}
    if team_id:
        q += " AND g.team_id = :team_id"
        params["team_id"] = team_id
    q += " ORDER BY g.team_id, g.category"
    with _conn() as conn:
        return pd.read_sql(text(q), conn, params=params)


# ── Equipes / Usuários ────────────────────────────────────────────────────────

def get_teams() -> pd.DataFrame:
    with _conn() as conn:
        return pd.read_sql(
            text("SELECT id, name FROM teams WHERE active = true ORDER BY name"),
            conn,
        )


def get_users() -> pd.DataFrame:
    with _conn() as conn:
        return pd.read_sql(
            text("SELECT id, name, email, role, team_id FROM users WHERE active = true"),
            conn,
        )


# ── Comparação App vs Câmera ──────────────────────────────────────────────────

def get_comparison(team_id=None, from_date=None, to_date=None) -> pd.DataFrame:
    df_app = get_readings(team_id=team_id, from_date=from_date, to_date=to_date)
    df_cam = get_camera_readings(team_id=team_id, from_date=from_date, to_date=to_date)

    categories = ["arroz", "feijao", "macarrao", "acucar", "outros"]
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
