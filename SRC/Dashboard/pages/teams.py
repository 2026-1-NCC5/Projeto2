import dash
from dash import html, dcc, callback, Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from data import get_teams, get_readings, get_camera_readings, get_users
from layout import PLOTLY_CONFIG, kpi_box, empty_figure

dash.register_page(__name__, path="/dashboard/teams", title="Equipes — Admin")

_GRAPH_H = {"height": "340px"}

layout = html.Div([
    html.H2("👥 Equipes", className="page-header"),
    html.Div(id="teams-kpis", className="kpi-grid"),
    html.Div([
        html.Div([
            html.Div([
                html.H3("Ranking por kg Total"),
                dcc.Graph(id="teams-ranking", config=PLOTLY_CONFIG, style=_GRAPH_H),
            ], className="card"),
        ], style={"flex": "1", "minWidth": "300px"}),
        html.Div([
            html.Div([
                html.H3("App vs Câmera por Equipe"),
                dcc.Graph(id="teams-comparison", config=PLOTLY_CONFIG, style=_GRAPH_H),
            ], className="card"),
        ], style={"flex": "1", "minWidth": "300px"}),
    ], style={"display": "flex", "gap": "16px", "flexWrap": "wrap"}),
    html.Div([
        html.H3("Cards de Equipe"),
        html.Div(id="teams-cards"),
    ], className="card"),
])


@callback(
    Output("teams-kpis", "children"),
    Output("teams-ranking", "figure"),
    Output("teams-comparison", "figure"),
    Output("teams-cards", "children"),
    Input("url", "pathname"),
    State("auth-store", "data"),
)
def update_teams(pathname, auth_data):
    if not pathname or "teams" not in pathname:
        raise dash.exceptions.PreventUpdate

    token = (auth_data or {}).get("token", "")
    teams = get_teams()
    df_app = get_readings(token)
    df_cam = get_camera_readings(token)
    users = get_users(token)

    kpis = [
        kpi_box(str(len(teams)), "Equipes ativas"),
        kpi_box(
            str(len(users[users["role"].isin(["operador", "coordenador"])])) if not users.empty else "0",
            "Membros ativos"
        ),
    ]

    if teams.empty:
        e = empty_figure()
        return kpis, e, e, []

    app_sum = (df_app.groupby("team_id")["kg_amount"].sum()
               .reset_index(name="kg_app") if not df_app.empty
               else pd.DataFrame(columns=["team_id", "kg_app"]))
    cam_sum = (df_cam.groupby("team_id")["kg_amount"].sum()
               .reset_index(name="kg_cam") if not df_cam.empty
               else pd.DataFrame(columns=["team_id", "kg_cam"]))

    merged = (teams
              .merge(app_sum, left_on="id", right_on="team_id", how="left")
              .merge(cam_sum, left_on="id", right_on="team_id", how="left")
              .fillna(0))
    merged["total"] = merged["kg_app"] + merged["kg_cam"]
    merged_asc = merged.sort_values("total", ascending=True)

    fig_rank = px.bar(merged_asc, x="total", y="name", orientation="h",
                      color_discrete_sequence=["#FF6B00"],
                      labels={"total": "kg Total", "name": "Equipe"})
    fig_rank.update_layout(paper_bgcolor="white", plot_bgcolor="white",
                           margin={"t": 10, "b": 30, "l": 10, "r": 10},
                           yaxis={"showgrid": False},
                           xaxis={"showgrid": True, "gridcolor": "#f0f0f0"})

    fig_comp = go.Figure()
    fig_comp.add_trace(go.Bar(name="App", x=merged["name"], y=merged["kg_app"],
                              marker_color="#FF6B00"))
    fig_comp.add_trace(go.Bar(name="Câmera", x=merged["name"], y=merged["kg_cam"],
                              marker_color="#FFB347"))
    fig_comp.update_layout(
        barmode="group", paper_bgcolor="white", plot_bgcolor="white",
        margin={"t": 50, "b": 40, "l": 40, "r": 10},
        legend={"orientation": "h", "y": 1.1},
        yaxis={"showgrid": True, "gridcolor": "#f0f0f0"},
        xaxis={"showgrid": False},
    )

    def div_color(app_kg, cam_kg):
        if app_kg == 0:
            return "#888"
        pct = abs((cam_kg - app_kg) / app_kg * 100)
        return "#2E7D32" if pct <= 10 else ("#F57F17" if pct <= 25 else "#c62828")

    cards = []
    for _, t in merged.sort_values("total", ascending=False).iterrows():
        team_users = users[users["team_id"] == t["id"]] if not users.empty else pd.DataFrame()
        color = div_color(t["kg_app"], t["kg_cam"])
        div_label = (
            f"Divergência: {abs((t['kg_cam'] - t['kg_app']) / t['kg_app'] * 100):.1f}%"
            if t["kg_app"] > 0 else "Sem dados App"
        )
        cards.append(html.Div([
            html.Div(t["name"], style={"fontWeight": "700", "fontSize": "15px",
                                        "color": "#FF6B00", "marginBottom": "10px"}),
            html.Div([
                html.Div([
                    html.Div(f"{t['kg_app']:,.1f} kg", style={"fontWeight": "700"}),
                    html.Div("App", style={"fontSize": "11px", "color": "#888"}),
                ]),
                html.Div([
                    html.Div(f"{t['kg_cam']:,.1f} kg", style={"fontWeight": "700"}),
                    html.Div("Câmera", style={"fontSize": "11px", "color": "#888"}),
                ]),
                html.Div([
                    html.Div(str(len(team_users)), style={"fontWeight": "700"}),
                    html.Div("Membros", style={"fontSize": "11px", "color": "#888"}),
                ]),
            ], style={"display": "flex", "gap": "16px"}),
            html.Div(div_label, style={"fontSize": "12px", "color": color,
                                        "marginTop": "8px", "fontWeight": "600"}),
        ], style={
            "background": "#fff", "borderRadius": "10px", "padding": "16px",
            "border": f"2px solid {color}", "minWidth": "200px", "flex": "1",
        }))

    return kpis, fig_rank, fig_comp, html.Div(cards, style={"display": "flex", "gap": "12px", "flexWrap": "wrap"})
