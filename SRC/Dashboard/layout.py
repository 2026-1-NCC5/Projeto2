from dash import html, dcc
import plotly.io as pio
import plotly.graph_objects as go

# Fonte Arial como padrão para todos os gráficos Plotly (labels, eixos e tooltips)
pio.templates["arial"] = go.layout.Template(
    layout=dict(
        font=dict(family="Arial, Helvetica, sans-serif"),
        hoverlabel=dict(font=dict(family="Arial, Helvetica, sans-serif")),
    )
)
pio.templates.default = "plotly+arial"

COLORS = {
    "primary": "#FF6B00",
    "primary_light": "#fff3e8",
    "bg": "#f0f0f0",
    "white": "#ffffff",
    "green": "#2E7D32",
    "red": "#c62828",
}

PLOTLY_COLORS = ["#FF6B00", "#FFB347", "#FF8C42", "#E65C00", "#FFC87A"]

PLOTLY_CONFIG = {
    "responsive": True,
    "displayModeBar": "hover",
    "modeBarButtonsToRemove": [
        "select2d", "lasso2d",
        "hoverClosestCartesian", "hoverCompareCartesian", "toggleSpikelines",
    ],
    "displaylogo": False,
    "scrollZoom": False,
    "toImageButtonOptions": {"format": "png", "scale": 2, "filename": "grafico"},
}

CAT_LABELS = {
    "arroz": "Arroz",
    "feijao": "Feijão",
    "macarrao": "Macarrão",
    "acucar": "Açúcar",
    "fuba": "Fubá",
    "oleo": "Óleo",
    "outros": "Outros",
}

NAV_ITEMS = [
    {"href": "/dashboard",        "label": "📊 Visão Geral"},
    {"href": "/dashboard/app",    "label": "📱 App Manual"},
    {"href": "/dashboard/camera", "label": "📷 Câmera YOLO"},
    {"href": "/dashboard/goals",  "label": "🎯 Metas"},
    {"href": "/dashboard/teams",  "label": "👥 Equipes"},
]


def build_sidebar(pathname: str, is_open: bool = False) -> html.Div:
    items = []
    for item in NAV_ITEMS:
        is_active = pathname == item["href"] or (
            item["href"] != "/dashboard" and pathname.startswith(item["href"])
        )
        items.append(
            dcc.Link(
                item["label"],
                href=item["href"],
                className=f"nav-item {'active' if is_active else ''}",
            )
        )

    class_name = "sidebar open" if is_open else "sidebar"
    return html.Div([
        html.Div([
            html.Img(src="/assets/logo.png",
                     style={"height": "42px", "marginBottom": "8px", "display": "block"}),
            html.H1("Lideranças Empáticas"),
            html.Div("Painel Admin", className="sub"),
        ], className="sidebar-brand"),
        html.Div(items, className="sidebar-nav"),
        html.Div([
            dcc.Link("🚪 Sair", href="/logout", className="nav-item",
                     style={"color": "rgba(255,255,255,.7)", "textDecoration": "none"}),
        ], className="sidebar-footer"),
    ], className=class_name, id="sidebar")


def kpi_box(value: str, label: str) -> html.Div:
    return html.Div([
        html.Div(value, className="val"),
        html.Div(label, className="lbl"),
    ], className="kpi-box")


def page_header(title: str, subtitle: str = "") -> html.Div:
    children = [html.H2(title)]
    if subtitle:
        children.append(html.Div(subtitle, className="sub"))
    return html.Div(children, className="page-header")


def filter_team_dropdown(teams_df, dropdown_id: str) -> html.Div:
    options = [{"label": "Todas as equipes", "value": "all"}] + [
        {"label": row["name"], "value": row["id"]}
        for _, row in teams_df.iterrows()
    ]
    return html.Div([
        html.Span("Equipe", className="filter-label"),
        dcc.Dropdown(options=options, value="all", id=dropdown_id,
                     clearable=False, style={"minWidth": "180px"}),
    ])


def filter_category_dropdown(dropdown_id: str) -> html.Div:
    options = [{"label": "Todas categorias", "value": "all"}] + [
        {"label": v, "value": k} for k, v in CAT_LABELS.items()
    ]
    return html.Div([
        html.Span("Categoria", className="filter-label"),
        dcc.Dropdown(options=options, value="all", id=dropdown_id,
                     clearable=False, style={"minWidth": "180px"}),
    ])


def filter_daterange(daterange_id: str) -> html.Div:
    return html.Div([
        html.Span("Período", className="filter-label"),
        html.Div([
            dcc.DatePickerRange(
                id=daterange_id,
                display_format="DD/MM/YYYY",
                start_date_placeholder_text="Início",
                end_date_placeholder_text="Fim",
                with_portal=True,
            ),
            html.Button("Confirmar",
                        id=f"{daterange_id}-apply",
                        n_clicks=0,
                        className="btn-primary daterange-apply"),
        ], className="daterange-row"),
    ])


def empty_figure(message: str = "Sem dados"):
    import plotly.graph_objects as go
    fig = go.Figure()
    fig.update_layout(
        paper_bgcolor="white",
        plot_bgcolor="white",
        annotations=[{"text": message, "showarrow": False,
                       "font": {"color": "#aaa", "size": 14},
                       "xref": "paper", "yref": "paper", "x": 0.5, "y": 0.5}],
        xaxis={"visible": False},
        yaxis={"visible": False},
    )
    return fig
