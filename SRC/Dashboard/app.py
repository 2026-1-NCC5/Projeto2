import dash
from dash import Dash, html, dcc, Input, Output, State, callback, ctx
import dash_bootstrap_components as dbc
from layout import build_sidebar

app = Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
    title="Lideranças Empáticas",
    update_title=None,
)

app.index_string = """<!DOCTYPE html>
<html>
<head>
    {%metas%}
    <title>{%title%}</title>
    <link rel="icon" type="image/png" href="/assets/logo.png">
    {%css%}
</head>
<body>
    {%app_entry%}
    <footer>{%config%}{%scripts%}{%renderer%}</footer>
</body>
</html>
"""

app.layout = html.Div([
    dcc.Store(id="auth-store", storage_type="session"),
    dcc.Store(id="sidebar-open", data=False),
    dcc.Location(id="url"),

    # Barra mobile com hambúrguer
    html.Div([
        html.Button("☰", id="mobile-menu-btn", n_clicks=0,
                    className="mobile-menu-btn"),
        html.Div(
            html.Img(src="/assets/logo.png", style={"height": "26px", "display": "block"}),
            style={"background": "white", "borderRadius": "6px",
                   "padding": "3px", "display": "flex", "alignItems": "center"},
        ),
        html.Span("Lideranças Empáticas", className="mobile-topbar-title"),
    ], id="mobile-topbar", className="mobile-topbar"),

    # Overlay escuro ao abrir sidebar no mobile
    html.Div(id="sidebar-overlay", n_clicks=0, className="sidebar-overlay"),

    html.Div([
        html.Div(id="sidebar-container"),
        html.Div(dash.page_container, id="content-wrapper", className="main-content"),
    ], className="app-wrapper"),
])


@callback(
    Output("mobile-topbar", "className"),
    Input("url", "pathname"),
)
def toggle_mobile_topbar(pathname):
    if pathname and pathname.startswith("/dashboard"):
        return "mobile-topbar visible"
    return "mobile-topbar"


@callback(
    Output("sidebar-open", "data"),
    Input("mobile-menu-btn", "n_clicks"),
    Input("sidebar-overlay", "n_clicks"),
    Input("url", "pathname"),
    State("sidebar-open", "data"),
    prevent_initial_call=True,
)
def toggle_sidebar(btn, overlay, pathname, is_open):
    if ctx.triggered_id == "url":
        return False
    return not bool(is_open)


@callback(
    Output("sidebar-container", "children"),
    Output("sidebar-overlay", "className"),
    Input("url", "pathname"),
    Input("sidebar-open", "data"),
)
def render_sidebar(pathname, is_open):
    overlay_class = "sidebar-overlay active" if is_open else "sidebar-overlay"
    if pathname and pathname.startswith("/dashboard"):
        return build_sidebar(pathname, is_open=bool(is_open)), overlay_class
    return [], "sidebar-overlay"


@callback(
    Output("url", "pathname"),
    Input("url", "pathname"),
    State("auth-store", "data"),
    prevent_initial_call=True,
)
def guard_admin_routes(pathname, auth_data):
    if pathname and pathname.startswith("/dashboard"):
        if not auth_data or not auth_data.get("token"):
            return "/login"
    return dash.no_update


@callback(
    Output("auth-store", "data", allow_duplicate=True),
    Output("url", "pathname", allow_duplicate=True),
    Input("url", "pathname"),
    prevent_initial_call=True,
)
def handle_logout(pathname):
    if pathname == "/logout":
        return None, "/login"
    return dash.no_update, dash.no_update


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8050, debug=False)
