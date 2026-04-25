import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
from data import get_camera_kpis, get_readings_kpis, get_comparison, get_goals, get_teams
from layout import CAT_LABELS, PLOTLY_CONFIG, filter_team_dropdown, filter_daterange, kpi_box, empty_figure

dash.register_page(__name__, path="/dashboard", title="Visão Geral — Admin")


def layout():
    teams = get_teams()
    return html.Div([
        html.H2("📊 Visão Geral", className="page-header"),

        html.Div([
            filter_team_dropdown(teams, "ov-team"),
            filter_daterange("ov-dates"),
        ], className="filters-row"),

        html.Div(id="ov-kpis", className="kpi-grid"),

        html.Div([
            html.H3("App vs Câmera — kg por categoria"),
            dcc.Graph(id="ov-comparison-chart", config=PLOTLY_CONFIG),
            html.Div([
                html.Button("▼ Ver detalhes", id="ov-toggle-table",
                            n_clicks=0, className="btn-secondary",
                            style={"marginTop": "12px"}),
            ]),
            dbc.Collapse(
                html.Div(id="ov-comparison-table", style={"marginTop": "14px"}),
                id="ov-collapse",
                is_open=False,
            ),
        ], className="card"),
    ])


@callback(
    Output("ov-kpis", "children"),
    Output("ov-comparison-chart", "figure"),
    Output("ov-comparison-table", "children"),
    Input("ov-team", "value"),
    Input("ov-dates", "start_date"),
    Input("ov-dates", "end_date"),
    State("auth-store", "data"),
)
def update_overview(team_id, from_date, to_date, auth_data):
    token = (auth_data or {}).get("token", "")
    tid = None if not team_id or team_id == "all" else int(team_id)
    cam_kpis = get_camera_kpis(token, team_id=tid, from_date=from_date, to_date=to_date)
    app_kpis = get_readings_kpis(token, team_id=tid, from_date=from_date, to_date=to_date)
    goals_df = get_goals(token, team_id=tid)

    meta_pct = 0.0
    if not goals_df.empty:
        total_meta = goals_df["target_kg"].sum()
        if total_meta > 0:
            meta_pct = min(cam_kpis["total_kg"] / total_meta * 100, 100)

    kpis = [
        kpi_box(f"{app_kpis['total_kg']:,.1f} kg", "Total kg App"),
        kpi_box(f"{cam_kpis['total_kg']:,.1f} kg", "Total kg Câmera"),
        kpi_box(f"R$ {cam_kpis['total_price']:,.2f}", "Valor total"),
        kpi_box(f"{meta_pct:.0f}%", "Meta atingida"),
    ]

    comp = get_comparison(token, team_id=tid, from_date=from_date, to_date=to_date)
    comp["label"] = comp["category"].map(CAT_LABELS)

    fig = go.Figure()
    fig.add_trace(go.Bar(name="App", x=comp["label"], y=comp["kg_app"],
                         marker_color="#FF6B00"))
    fig.add_trace(go.Bar(name="Câmera", x=comp["label"], y=comp["kg_camera"],
                         marker_color="#FFB347"))
    fig.update_layout(
        barmode="group", paper_bgcolor="white", plot_bgcolor="white",
        legend={"orientation": "h", "y": 1.12},
        margin={"t": 40, "b": 30, "l": 40, "r": 10},
        yaxis={"showgrid": True, "gridcolor": "#f0f0f0"},
        xaxis={"showgrid": False},
    )

    def status_badge(pct):
        if abs(pct) <= 10:
            return html.Span("✅ OK", className="status-ok")
        elif abs(pct) <= 25:
            return html.Span("⚠️ Atenção", className="status-warn")
        return html.Span("❌ Divergente", className="status-bad")

    rows = [html.Tr([
        html.Th("Categoria"), html.Th("App (kg)"), html.Th("Câmera (kg)"),
        html.Th("Diferença"), html.Th("Divergência"), html.Th("Status"),
    ], style={"background": "#f5f5f5"})]

    for _, r in comp.iterrows():
        rows.append(html.Tr([
            html.Td(html.Span(CAT_LABELS.get(r["category"], r["category"]), className="badge")),
            html.Td(f"{r['kg_app']:,.2f} kg"),
            html.Td(f"{r['kg_camera']:,.2f} kg"),
            html.Td(f"{r['diff_kg']:+.2f} kg"),
            html.Td(f"{r['diff_pct']:+.1f}%"),
            html.Td(status_badge(r["diff_pct"])),
        ]))

    table = html.Table(rows, style={"width": "100%", "borderCollapse": "collapse",
                                     "fontSize": "13px"})
    return kpis, fig, table


@callback(
    Output("ov-collapse", "is_open"),
    Output("ov-toggle-table", "children"),
    Input("ov-toggle-table", "n_clicks"),
    State("ov-collapse", "is_open"),
    prevent_initial_call=True,
)
def toggle_table(n, is_open):
    new_open = not is_open
    label = "▲ Ocultar detalhes" if new_open else "▼ Ver detalhes"
    return new_open, label
