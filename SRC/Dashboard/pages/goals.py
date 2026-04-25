import dash
from dash import html, dcc, callback, Input, Output, State
import plotly.graph_objects as go
import pandas as pd
from data import get_goals, get_readings, get_camera_readings, get_teams
from layout import CAT_LABELS, PLOTLY_CONFIG, filter_team_dropdown, kpi_box, empty_figure

dash.register_page(__name__, path="/dashboard/goals", title="Metas — Admin")


def layout():
    teams = get_teams()
    return html.Div([
        html.H2("🎯 Metas", className="page-header"),

        html.Div([filter_team_dropdown(teams, "goals-team")], className="filters-row"),

        html.Div(id="goals-kpis", className="kpi-grid"),

        html.Div([
            html.H3("Progresso por Equipe e Categoria"),
            dcc.Graph(id="goals-progress", config=PLOTLY_CONFIG, style={"height": "420px"}),
        ], className="card"),

        html.Div([
            html.H3("Tabela Detalhada"),
            html.Div(id="goals-table"),
        ], className="card"),
    ])


@callback(
    Output("goals-kpis", "children"),
    Output("goals-progress", "figure"),
    Output("goals-table", "children"),
    Input("goals-team", "value"),
    State("auth-store", "data"),
)
def update_goals(team_id, auth_data):
    token = (auth_data or {}).get("token", "")
    tid = None if not team_id or team_id == "all" else int(team_id)
    goals = get_goals(token, team_id=tid)
    df_app = get_readings(token, team_id=tid)
    df_cam = get_camera_readings(token, team_id=tid)

    if goals.empty:
        fig = empty_figure("Nenhuma meta cadastrada")
        return [], fig, html.P("Sem metas cadastradas.", style={"color": "#aaa"})

    rows = []
    for _, g in goals.iterrows():
        kg_app = float(
            df_app[(df_app["team_id"] == g["team_id"]) &
                   (df_app["category"] == g["category"])]["kg_amount"].sum()
        ) if not df_app.empty else 0.0
        kg_cam = float(
            df_cam[(df_cam["team_id"] == g["team_id"]) &
                   (df_cam["category"] == g["category"])]["kg_amount"].sum()
        ) if not df_cam.empty else 0.0
        pct = min(kg_app / g["target_kg"] * 100, 100) if g["target_kg"] > 0 else 0.0
        rows.append({
            "team_name": g["team_name"],
            "category": g["category"],
            "target_kg": g["target_kg"],
            "kg_app": round(kg_app, 2),
            "kg_cam": round(kg_cam, 2),
            "pct": round(pct, 1),
        })

    df_m = pd.DataFrame(rows)
    avg_pct = df_m["pct"].mean()

    kpis = [
        kpi_box(f"{avg_pct:.0f}%", "% Média das metas"),
        kpi_box(str(len(df_m[df_m["pct"] >= 100])), "Metas atingidas"),
        kpi_box(str(len(df_m[df_m["pct"] < 100])), "Metas pendentes"),
    ]

    x_labels = [
        f"{r['team_name']} — {CAT_LABELS.get(r['category'], r['category'])}"
        for _, r in df_m.iterrows()
    ]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Realizado (App)", x=x_labels, y=df_m["kg_app"],
        marker_color="#FF6B00",
        customdata=df_m["pct"],
        hovertemplate="<b>%{x}</b><br>Realizado: %{y:.1f} kg<br>%{customdata:.1f}% da meta<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        name="Meta", x=x_labels, y=df_m["target_kg"],
        mode="markers",
        marker={"symbol": "line-ew", "size": 14, "color": "#c62828",
                "line": {"width": 3, "color": "#c62828"}},
        hovertemplate="<b>%{x}</b><br>Meta: %{y:.1f} kg<extra></extra>",
    ))
    fig.update_layout(
        paper_bgcolor="white", plot_bgcolor="white",
        margin={"t": 30, "b": 100, "l": 40, "r": 10},
        yaxis={"showgrid": True, "gridcolor": "#f0f0f0"},
        xaxis={"showgrid": False, "tickangle": -30},
        legend={"orientation": "h", "y": 1.08},
    )

    table_rows = [html.Tr([
        html.Th(c) for c in
        ["Equipe", "Categoria", "Meta (kg)", "App (kg)", "Câmera (kg)", "% Atingido"]
    ], style={"background": "#f5f5f5"})]

    for _, r in df_m.iterrows():
        color = "#2E7D32" if r["pct"] >= 100 else ("#F57F17" if r["pct"] >= 70 else "#c62828")
        table_rows.append(html.Tr([
            html.Td(r["team_name"]),
            html.Td(html.Span(CAT_LABELS.get(r["category"], r["category"]),
                              className="badge")),
            html.Td(f"{r['target_kg']:,.2f}"),
            html.Td(f"{r['kg_app']:,.2f}"),
            html.Td(f"{r['kg_cam']:,.2f}"),
            html.Td(f"{r['pct']:.1f}%", style={"color": color, "fontWeight": "700"}),
        ]))

    table = html.Table(table_rows, style={"width": "100%", "borderCollapse": "collapse",
                                           "fontSize": "13px"})
    return kpis, fig, table
