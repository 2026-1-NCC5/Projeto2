import dash
from dash import html

dash.register_page(__name__, path="/logout")

layout = html.Div([
    html.Div([
        html.Div([
            html.Img(src="/assets/logo.png",
                     style={"height": "64px", "marginBottom": "20px"}),
            html.Div([
                html.Div(className="logout-spinner"),
            ]),
            html.Div("Saindo...",
                     style={"marginTop": "16px", "fontSize": "15px",
                            "color": "#888", "fontWeight": "500"}),
        ], style={"display": "flex", "flexDirection": "column",
                  "alignItems": "center", "justifyContent": "center"}),
    ], style={"display": "flex", "alignItems": "center", "justifyContent": "center",
              "height": "100vh", "background": "#f0f0f0"}),
])
