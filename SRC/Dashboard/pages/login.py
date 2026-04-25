import dash
from dash import html, dcc, callback, Input, Output, State
from auth import validate_login

dash.register_page(__name__, path="/login", title="Login — Lideranças Empáticas")

layout = html.Div([
    dcc.Location(id="login-redirect"),
    html.Div([
        html.Div([
            html.Div("📷", style={"fontSize": "36px", "textAlign": "center", "marginBottom": "8px"}),
            html.H2("Lideranças Empáticas"),
            html.Div("Painel do Professor", className="sub"),
            html.Div([
                html.Div([
                    html.Label("E-mail"),
                    dcc.Input(id="login-email", type="email",
                              placeholder="admin@admin.com",
                              className="form-control", debounce=False,
                              style={"width": "100%"}),
                ], className="form-group"),
                html.Div([
                    html.Label("Senha"),
                    dcc.Input(id="login-password", type="password",
                              placeholder="••••••••",
                              className="form-control", debounce=False,
                              style={"width": "100%"}),
                ], className="form-group"),
                html.Button("Entrar", id="login-btn", n_clicks=0,
                            className="btn-primary",
                            style={"width": "100%", "marginTop": "8px"}),
                html.Div(id="login-msg", style={"marginTop": "12px", "fontSize": "13px"}),
            ]),
        ], className="login-card"),
    ], className="login-wrapper"),
], style={"background": "#f0f0f0", "minHeight": "100vh"})


@callback(
    Output("auth-store", "data"),
    Output("login-redirect", "pathname"),
    Output("login-msg", "children"),
    Output("login-msg", "style"),
    Input("login-btn", "n_clicks"),
    State("login-email", "value"),
    State("login-password", "value"),
    prevent_initial_call=True,
)
def do_login(n_clicks, email, password):
    if not email or not password:
        return (dash.no_update, dash.no_update,
                "Preencha e-mail e senha.",
                {"color": "#c62828", "fontSize": "13px"})
    result = validate_login(email, password)
    if result:
        return result, "/dashboard", "", {}
    return (None, dash.no_update,
            "E-mail ou senha incorretos.",
            {"color": "#c62828", "fontSize": "13px"})
