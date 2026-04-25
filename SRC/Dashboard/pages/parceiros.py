import dash
from dash import html, dcc, callback, Input, Output
import plotly.express as px
import pandas as pd
from data import get_public_camera_readings, get_public_camera_kpis, _API_ERROR
from layout import CAT_LABELS, PLOTLY_COLORS, PLOTLY_CONFIG, empty_figure

dash.register_page(__name__, path="/", title="Resultados — Lideranças Empáticas")

_GRAPH_H = {"height": "340px"}


def _public_header():
    return html.Div([
        html.Div([
            html.Div(
                html.Img(src="/assets/logo.png", style={"height": "36px", "display": "block"}),
                style={"background": "white", "borderRadius": "8px",
                       "padding": "4px", "display": "flex", "alignItems": "center"},
            ),
            html.Div([
                html.H1("Lideranças Empáticas"),
                html.Div("Resultados da Arrecadação", className="sub"),
            ]),
        ], style={"display": "flex", "alignItems": "center", "gap": "12px"}),
        dcc.Link("🔐 Admin", href="/login", className="admin-link"),
    ], className="public-header")


layout = html.Div([
    _public_header(),
    html.Div([
        html.Div([
            html.Div([
                html.Span("Categoria", className="filter-label"),
                dcc.Dropdown(
                    id="pub-filter-cat",
                    options=[{"label": "Todas", "value": "all"}] + [
                        {"label": v, "value": k} for k, v in CAT_LABELS.items()
                    ],
                    value="all", clearable=False, style={"minWidth": "200px"},
                ),
            ]),
        ], className="filters-row"),

        html.Div(id="pub-kpis", className="kpi-grid"),

        html.Div([
            html.Div([
                html.Div([
                    html.H3("Distribuição por Categoria"),
                    dcc.Graph(id="pub-donut", config=PLOTLY_CONFIG, style=_GRAPH_H),
                ], className="card"),
            ], style={"flex": "1", "minWidth": "280px"}),
            html.Div([
                html.Div([
                    html.H3("Detecções ao Longo do Tempo"),
                    dcc.Graph(id="pub-timeline", config=PLOTLY_CONFIG, style=_GRAPH_H),
                ], className="card"),
            ], style={"flex": "2", "minWidth": "320px"}),
        ], style={"display": "flex", "gap": "16px", "flexWrap": "wrap"}),

        html.Div([
            html.H3("kg Validado por Categoria"),
            dcc.Graph(id="pub-bars", config=PLOTLY_CONFIG, style=_GRAPH_H),
        ], className="card"),

    ], style={"maxWidth": "1100px", "margin": "24px auto", "padding": "0 16px"}),
], style={"margin": "-24px"})


@callback(
    Output("pub-kpis", "children"),
    Output("pub-donut", "figure"),
    Output("pub-timeline", "figure"),
    Output("pub-bars", "figure"),
    Input("pub-filter-cat", "value"),
)
def update_public(category):
    cat = None if not category or category == "all" else category
    kpis = get_public_camera_kpis(category=cat)
    df = get_public_camera_readings(category=cat)

    kpi_boxes = [
        html.Div([html.Div(f"{kpis['total_kg']:,.1f} kg", className="val"),
                  html.Div("Total kg validado", className="lbl")], className="kpi-box"),
        html.Div([html.Div(f"R$ {kpis['total_price']:,.2f}", className="val"),
                  html.Div("Valor estimado", className="lbl")], className="kpi-box"),
        html.Div([html.Div(str(kpis["total_count"]), className="val"),
                  html.Div("Detecções", className="lbl")], className="kpi-box"),
        html.Div([html.Div(f"{kpis['avg_confidence']:.1f}%", className="val"),
                  html.Div("Confiança média", className="lbl")], className="kpi-box"),
    ]

    if df is _API_ERROR:
        msg = empty_figure("⚠️ Servidor indisponível — reconstrua o container")
        return kpi_boxes, msg, msg, msg

    if df.empty:
        e = empty_figure("Sem dados")
        return kpi_boxes, e, e, e

    # Donut
    agg = df.groupby("category")["kg_amount"].sum().reset_index()
    agg["label"] = agg["category"].map(CAT_LABELS)
    fig_donut = px.pie(agg, values="kg_amount", names="label", hole=0.45,
                       color_discrete_sequence=PLOTLY_COLORS)
    fig_donut.update_traces(
        textposition="inside",
        textinfo="percent",
        hovertemplate="<b>%{label}</b><br>%{value:.1f} kg<br>%{percent}<extra></extra>",
    )
    fig_donut.update_layout(paper_bgcolor="white", showlegend=True,
                            margin={"t": 10, "b": 10, "l": 10, "r": 10})

    # Timeline
    df["date"] = pd.to_datetime(df["created_at"]).dt.date
    timeline = df.groupby("date").size().reset_index(name="count")
    fig_line = px.line(timeline, x="date", y="count", markers=True,
                       color_discrete_sequence=["#FF6B00"],
                       labels={"date": "Data", "count": "Detecções"})
    fig_line.update_traces(
        hovertemplate="<b>%{x|%d/%m/%Y}</b><br>%{y} detecções<extra></extra>"
    )
    fig_line.update_layout(paper_bgcolor="white", plot_bgcolor="white",
                           margin={"t": 10, "b": 30, "l": 40, "r": 10})
    fig_line.update_xaxes(showgrid=False)
    fig_line.update_yaxes(showgrid=True, gridcolor="#f0f0f0")

    # Barras
    bar_agg = df.groupby("category").agg(
        kg=("kg_amount", "sum"), price=("price", "sum")
    ).reset_index()
    bar_agg["label"] = bar_agg["category"].map(CAT_LABELS)
    bar_agg["text"] = bar_agg["price"].apply(lambda x: f"R$ {x:,.2f}")
    fig_bars = px.bar(bar_agg, x="label", y="kg", text="text",
                      color_discrete_sequence=["#FF6B00"],
                      labels={"label": "Categoria", "kg": "kg"})
    fig_bars.update_traces(
        textposition="outside",
        customdata=bar_agg["price"],
        hovertemplate="<b>%{x}</b><br>%{y:.1f} kg<br>R$ %{customdata:,.2f}<extra></extra>",
    )
    fig_bars.update_layout(paper_bgcolor="white", plot_bgcolor="white",
                           margin={"t": 40, "b": 30, "l": 40, "r": 10})
    fig_bars.update_yaxes(showgrid=True, gridcolor="#f0f0f0")
    fig_bars.update_xaxes(showgrid=False)

    return kpi_boxes, fig_donut, fig_line, fig_bars
