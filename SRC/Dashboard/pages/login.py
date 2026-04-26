import dash
from dash import html, dcc, callback, Input, Output, State
from auth import validate_login

dash.register_page(__name__, path="/login", title="Login — Lideranças Empáticas")

layout = html.Div([
    dcc.Location(id="login-redirect"),
    html.Div([
        html.Div([
            html.Div(className="login-accent"),
            html.Div([
                html.Img(src="/assets/logo.png", className="login-logo"),
                html.H2("Lideranças Empáticas"),
                html.P("Painel do Professor", className="sub"),
            ], className="login-brand"),
            html.Div([
                html.Div([
                    html.Label("E-mail"),
                    dcc.Input(
                        id="login-email", type="email",
                        placeholder="seu@email.com",
                        className="form-control",
                        debounce=False,
                    ),
                ], className="form-group"),
                html.Div([
                    html.Label("Senha"),
                    dcc.Input(
                        id="login-password", type="password",
                        placeholder="sua senha",
                        className="form-control",
                        debounce=False,
                    ),
                ], className="form-group"),
                html.Button(
                    [html.Span("Entrar"), html.Span("→", className="btn-arrow")],
                    id="login-btn", n_clicks=0,
                    className="btn-primary btn-login",
                ),
                html.Div(id="login-msg", className="login-error"),
            ], className="login-form"),
            dcc.Link(
                "← Voltar para a página inicial",
                href="/",
                className="login-back",
            ),
        ], className="login-card"),
    ], className="login-wrapper"),
])


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
