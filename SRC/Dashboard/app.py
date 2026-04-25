import dash
from dash import Dash, html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc
from layout import build_sidebar

app = Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
    title="Lideranças Empáticas",
)

app.layout = html.Div([
    dcc.Store(id="auth-store", storage_type="session"),
    dcc.Location(id="url"),
    html.Div([
        html.Div(id="sidebar-container"),
        html.Div(dash.page_container, id="content-wrapper", className="main-content"),
    ], className="app-wrapper"),
])


@callback(
    Output("sidebar-container", "children"),
    Input("url", "pathname"),
)
def render_sidebar(pathname):
    if pathname and pathname.startswith("/dashboard"):
        return build_sidebar(pathname)
    return []


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
