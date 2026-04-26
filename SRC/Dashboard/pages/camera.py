import dash
from dash import html, dcc, callback, Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from data import get_camera_readings, get_camera_kpis, get_teams
from layout import (CAT_LABELS, PLOTLY_COLORS, PLOTLY_CONFIG, filter_team_dropdown,
                    filter_category_dropdown, filter_daterange, kpi_box, empty_figure)

dash.register_page(__name__, path="/dashboard/camera", title="Câmera YOLO — Admin")

_GRAPH_H = {"height": "340px"}
_GRAPH_H_LG = {"height": "400px"}


def layout():
    teams = get_teams()
    return html.Div([
        html.H2("📷 Câmera YOLO", className="page-header"),

        html.Div([
            filter_team_dropdown(teams, "cam-team"),
            filter_category_dropdown("cam-cat"),
            filter_daterange("cam-dates"),
        ], className="filters-row"),

        html.Div(id="cam-kpis", className="kpi-grid"),

        html.Div([
            html.Div([
                html.Div([
                    html.H3("kg e Valor por Categoria"),
                    dcc.Graph(id="cam-bars", config=PLOTLY_CONFIG, style=_GRAPH_H),
                ], className="card"),
            ], style={"flex": "2", "minWidth": "320px"}),
            html.Div([
                html.Div([
                    html.H3("Confiança Média por Categoria"),
                    dcc.Graph(id="cam-conf-bars", config=PLOTLY_CONFIG, style=_GRAPH_H),
                ], className="card"),
            ], style={"flex": "1", "minWidth": "260px"}),
        ], style={"display": "flex", "gap": "16px", "flexWrap": "wrap"}),

        html.Div([
            html.H3("Detecções ao Longo do Tempo"),
            dcc.Graph(id="cam-timeline", config=PLOTLY_CONFIG, style=_GRAPH_H),
        ], className="card"),

        html.Div([
            html.H3("Heatmap: Equipe × Categoria (kg)"),
            dcc.Graph(id="cam-heatmap", config=PLOTLY_CONFIG, style=_GRAPH_H_LG),
        ], className="card"),
    ])


@callback(
    Output("cam-kpis", "children"),
    Output("cam-bars", "figure"),
    Output("cam-conf-bars", "figure"),
    Output("cam-timeline", "figure"),
    Output("cam-heatmap", "figure"),
    Input("cam-team", "value"),
    Input("cam-cat", "value"),
    Input("cam-dates-apply", "n_clicks"),
    State("cam-dates", "start_date"),
    State("cam-dates", "end_date"),
    State("auth-store", "data"),
)
def update_camera(team_id, category, _n_apply, from_date, to_date, auth_data):
    token = (auth_data or {}).get("token", "")
    tid = None if not team_id or team_id == "all" else int(team_id)
    cat = None if not category or category == "all" else category
    kpis_data = get_camera_kpis(token, team_id=tid, category=cat,
                                 from_date=from_date, to_date=to_date)
    df = get_camera_readings(token, team_id=tid, category=cat,
                             from_date=from_date, to_date=to_date)

    kpis = [
        kpi_box(f"{kpis_data['total_kg']:,.1f} kg", "Total kg validado"),
        kpi_box(f"R$ {kpis_data['total_price']:,.2f}", "Valor total"),
        kpi_box(str(kpis_data["total_count"]), "Detecções"),
        kpi_box(f"{kpis_data['avg_confidence']:.1f}%", "Confiança média"),
    ]

    if df.empty:
        e = empty_figure()
        return kpis, e, e, e, e

    # Barras kg + valor R$
    agg = df.groupby("category").agg(kg=("kg_amount", "sum"),
                                      price=("price", "sum")).reset_index()
    agg["label"] = agg["category"].map(CAT_LABELS)
    agg["text"] = agg["price"].apply(lambda x: f"R$ {x:,.2f}")
    fig_bars = px.bar(agg, x="label", y="kg", text="text",
                      color_discrete_sequence=["#FF6B00"],
                      labels={"label": "Categoria", "kg": "kg"})
    fig_bars.update_traces(
        textposition="outside",
        customdata=agg["price"],
        hovertemplate="<b>%{x}</b><br>%{y:.1f} kg<br>R$ %{customdata:,.2f}<extra></extra>",
    )
    fig_bars.update_layout(paper_bgcolor="white", plot_bgcolor="white",
                           margin={"t": 40, "b": 30, "l": 40, "r": 10},
                           yaxis={"showgrid": True, "gridcolor": "#f0f0f0"},
                           xaxis={"showgrid": False})

    # Confiança por categoria
    conf = df.groupby("category")["confidence"].mean().reset_index()
    conf["label"] = conf["category"].map(CAT_LABELS)
    conf["pct"] = (conf["confidence"] * 100).round(1)
    conf["text"] = conf["pct"].apply(lambda x: f"{x:.1f}%")
    fig_conf = px.bar(conf, x="label", y="pct", text="text",
                      color_discrete_sequence=["#FFB347"],
                      labels={"label": "Categoria", "pct": "Confiança (%)"},
                      range_y=[0, 115])
    fig_conf.update_traces(
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>Confiança: %{y:.1f}%<extra></extra>",
    )
    fig_conf.update_layout(paper_bgcolor="white", plot_bgcolor="white",
                           margin={"t": 40, "b": 30, "l": 40, "r": 10},
                           yaxis={"showgrid": True, "gridcolor": "#f0f0f0"},
                           xaxis={"showgrid": False})

    # Timeline
    df["date"] = pd.to_datetime(df["created_at"]).dt.date
    timeline = df.groupby("date").size().reset_index(name="detecções")
    fig_line = px.line(timeline, x="date", y="detecções", markers=True,
                       color_discrete_sequence=["#FF6B00"],
                       labels={"date": "Data"})
    fig_line.update_traces(
        hovertemplate="<b>%{x|%d/%m/%Y}</b><br>%{y} detecções<extra></extra>"
    )
    fig_line.update_layout(paper_bgcolor="white", plot_bgcolor="white",
                           margin={"t": 10, "b": 30, "l": 40, "r": 10})
    fig_line.update_xaxes(showgrid=False)
    fig_line.update_yaxes(showgrid=True, gridcolor="#f0f0f0")

    # Heatmap
    heat = df.groupby(["team_name", "category"])["kg_amount"].sum().reset_index()
    if not heat.empty:
        heat_pivot = heat.pivot(index="team_name", columns="category",
                                values="kg_amount").fillna(0)
        heat_pivot.columns = [CAT_LABELS.get(c, c) for c in heat_pivot.columns]
        fig_heat = go.Figure(go.Heatmap(
            z=heat_pivot.values,
            x=list(heat_pivot.columns),
            y=list(heat_pivot.index),
            colorscale=[[0, "#fff3e8"], [1, "#FF6B00"]],
            text=heat_pivot.values.round(1),
            texttemplate="%{text} kg",
            hovertemplate="<b>%{y}</b><br>%{x}<br>%{z:.1f} kg<extra></extra>",
        ))
        fig_heat.update_layout(paper_bgcolor="white",
                               margin={"t": 10, "b": 30, "l": 10, "r": 10})
    else:
        fig_heat = empty_figure()

    return kpis, fig_bars, fig_conf, fig_line, fig_heat
