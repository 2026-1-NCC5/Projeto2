import dash
from dash import html, dcc, callback, Input, Output, State
import plotly.express as px
import pandas as pd
from data import get_readings, get_readings_kpis, get_teams
from layout import (CAT_LABELS, PLOTLY_COLORS, filter_team_dropdown,
                    filter_category_dropdown, filter_daterange, kpi_box, empty_figure)

dash.register_page(__name__, path="/dashboard/app", title="App Manual — Admin")


def layout():
    teams = get_teams()
    return html.Div([
        html.H2("📱 App Manual", className="page-header"),

        html.Div([
            filter_team_dropdown(teams, "app-team"),
            filter_category_dropdown("app-cat"),
            filter_daterange("app-dates"),
        ], className="filters-row"),

        html.Div(id="app-kpis", className="kpi-grid"),

        html.Div([
            html.Div([
                html.Div([
                    html.H3("kg por Equipe"),
                    dcc.Graph(id="app-by-team", config={"responsive": True}),
                ], className="card"),
            ], style={"flex": "1", "minWidth": "300px"}),
            html.Div([
                html.Div([
                    html.H3("Distribuição por Categoria"),
                    dcc.Graph(id="app-donut", config={"responsive": True}),
                ], className="card"),
            ], style={"flex": "1", "minWidth": "280px"}),
        ], style={"display": "flex", "gap": "16px", "flexWrap": "wrap"}),

        html.Div([
            html.H3("Registros ao Longo do Tempo"),
            dcc.Graph(id="app-timeline", config={"responsive": True}),
        ], className="card"),

        html.Div([
            html.H3("Ranking de Equipes"),
            html.Div(id="app-ranking-table"),
        ], className="card"),
    ])


@callback(
    Output("app-kpis", "children"),
    Output("app-by-team", "figure"),
    Output("app-donut", "figure"),
    Output("app-timeline", "figure"),
    Output("app-ranking-table", "children"),
    Input("app-team", "value"),
    Input("app-cat", "value"),
    Input("app-dates", "start_date"),
    Input("app-dates", "end_date"),
    State("auth-store", "data"),
)
def update_app_data(team_id, category, from_date, to_date, auth_data):
    token = (auth_data or {}).get("token", "")
    tid = None if team_id == "all" else int(team_id)
    cat = None if category == "all" else category
    kpis_data = get_readings_kpis(token, team_id=tid, category=cat,
                                   from_date=from_date, to_date=to_date)
    df = get_readings(token, team_id=tid, category=cat, from_date=from_date, to_date=to_date)

    kpis = [
        kpi_box(f"{kpis_data['total_kg']:,.1f} kg", "Total kg registrado"),
        kpi_box(str(kpis_data["total_count"]), "Total de registros"),
    ]

    if df.empty:
        e = empty_figure()
        return kpis, e, e, e, html.P("Sem dados.", style={"color": "#aaa"})

    # kg por equipe
    by_team = (df.groupby("team_name")["kg_amount"].sum()
               .reset_index().sort_values("kg_amount", ascending=True))
    fig_team = px.bar(by_team, x="kg_amount", y="team_name", orientation="h",
                      color_discrete_sequence=["#FF6B00"],
                      labels={"kg_amount": "kg", "team_name": "Equipe"})
    fig_team.update_layout(paper_bgcolor="white", plot_bgcolor="white",
                           margin={"t": 10, "b": 30, "l": 10, "r": 10},
                           yaxis={"showgrid": False},
                           xaxis={"showgrid": True, "gridcolor": "#f0f0f0"})

    # Donut
    by_cat = df.groupby("category")["kg_amount"].sum().reset_index()
    by_cat["label"] = by_cat["category"].map(CAT_LABELS)
    fig_donut = px.pie(by_cat, values="kg_amount", names="label", hole=0.45,
                       color_discrete_sequence=PLOTLY_COLORS)
    fig_donut.update_layout(paper_bgcolor="white", margin={"t": 10, "b": 10})

    # Timeline
    df["date"] = pd.to_datetime(df["created_at"]).dt.date
    timeline = df.groupby("date").size().reset_index(name="registros")
    fig_line = px.line(timeline, x="date", y="registros", markers=True,
                       color_discrete_sequence=["#FF6B00"],
                       labels={"date": "Data", "registros": "Registros"})
    fig_line.update_layout(paper_bgcolor="white", plot_bgcolor="white",
                           margin={"t": 10, "b": 30, "l": 40, "r": 10})
    fig_line.update_xaxes(showgrid=False)
    fig_line.update_yaxes(showgrid=True, gridcolor="#f0f0f0")

    # Ranking
    ranking = (df.groupby("team_name")
               .agg(total_kg=("kg_amount", "sum"), registros=("id", "count"))
               .reset_index().sort_values("total_kg", ascending=False))
    ranking["pos"] = range(1, len(ranking) + 1)

    rows = [html.Tr([
        html.Th("Pos"), html.Th("Equipe"),
        html.Th("kg Total"), html.Th("Registros"),
    ], style={"background": "#f5f5f5"})]
    for _, r in ranking.iterrows():
        rows.append(html.Tr([
            html.Td(f"#{int(r['pos'])}"),
            html.Td(r["team_name"]),
            html.Td(f"{r['total_kg']:,.2f} kg"),
            html.Td(str(int(r["registros"]))),
        ]))
    table = html.Table(rows, style={"width": "100%", "borderCollapse": "collapse",
                                     "fontSize": "13px"})
    return kpis, fig_team, fig_donut, fig_line, table
