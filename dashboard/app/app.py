from os import path

from dash import Dash, html, dcc, callback, Input, Output, page_registry, page_container
import plotly.express as px

external_stylesheets = ['app/assets/styles.css']
app = Dash(__name__, use_pages=True, external_stylesheets=external_stylesheets)

app.layout = html.Div(
    [
        html.Div(
            className="navigation-bar",
            style={
                "background-color": "Black",
                "padding": "10px",
                "top": "0",
                "left": "0",
                "right": "0",
                "width": "100%",
                "position": "fixed",
                "z-index": "9999",
                "display": "flex",
                "justify-content": "space-between",
                "height": "50px",
            },
            children=[
                html.H1(
                    children=[
                        html.Span("Spotify", style={"color": "#1ed760"}),
                        html.Span("/", style={"color": "white"}),
                        html.Span("T", style={"color": "#00f2ea"}),
                        html.Span("i", style={"color": "white"}),
                        html.Span("k", style={"color": "#ff0050"}),
                        html.Span("T", style={"color": "#00f2ea"}),
                        html.Span("o", style={"color": "white"}),
                        html.Span("k", style={"color": "#ff0050"}),
                        html.Span(" Chart Comparison", style={"color": "white"}),
                    ],
                    style={
                        "margin-top": "10px",
                        "font-size": "40px",
                        "font-weight": "bold",
                        "margin-right": "20px"
                    },
                ),
                html.Div(
                    className="button-container",
                    style={"display": "flex", "align-items": "center", "margin-right": "20px"},
                    children=[
                        html.Button(
                            dcc.Link(
                                page["name"],
                                href=page["path"],
                                style={
                                    "margin-right": "10px",
                                    "margin-left": "10px",
                                    "color": "black",
                                    "textDecoration": "none",
                                    "font-weight": "bold"
                                },
                            ),
                            style={"background-color": "#CDCBCD", "height": "20px", 'margin-right': '5px'},
                        )
                        for page in page_registry.values()
                    ],
                ),
            ],
        ),
        html.Div([html.Img(src="assets/spotify_logo.png", style={'width': '100px', 'height': '100px', 'padding-right': '20px'}),
        html.Img(src="assets/tiktok_logo.png", style={'width': '100px', 'height': '100px', 'padding-right': '20px'})], \
            style={"float": "right", "width": "30%", "margin-top": "-20px", "display": "flex", "justify-content": "flex-end", \
                   "align-items": "center", 'margin-bottom': '10px'}),
        page_container,
    ]
)

# {'margin-top': '10px', "float": "right", "width": "30%"}