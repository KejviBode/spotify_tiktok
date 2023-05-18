from os import path

from dash import Dash, html, dcc, callback, Input, Output, page_registry, page_container
import plotly.express as px
import pandas as pd


app = Dash(__name__, use_pages=True)


app.layout = html.Div(
    [
        html.Div(
            className="navigation-bar",
            style={
                "background-color": "#DEFBD6",
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
                        html.Span("Spotify", style={"color": "#1ed760", 'text-shadow': '-1px -1px 0 #000, 1px -1px 0 #000, -1px 1px 0 #000, 1px 1px 0 #000'}),
                        html.Span("/", style={"color": "black"}),
                        html.Span("T", style={"color": "#00f2ea", 'text-shadow': '-1px -1px 0 #000, 1px -1px 0 #000, -1px 1px 0 #000, 1px 1px 0 #000'}),
                        html.Span("i", style={"color": "Black"}),
                        html.Span("k", style={"color": "#ff0050", 'text-shadow': '-1px -1px 0 #000, 1px -1px 0 #000, -1px 1px 0 #000, 1px 1px 0 #000'}),
                        html.Span("T", style={"color": "#00f2ea", 'text-shadow': '-1px -1px 0 #000, 1px -1px 0 #000, -1px 1px 0 #000, 1px 1px 0 #000'}),
                        html.Span("o", style={"color": "Black"}),
                        html.Span("k", style={"color": "#ff0050", 'text-shadow': '-1px -1px 0 #000, 1px -1px 0 #000, -1px 1px 0 #000, 1px 1px 0 #000'}),
                        html.Span(" Chart Comparison", style={"color": "black"}),
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
                            style={"background-color": "#FBD6F9", "height": "20px", 'margin-right': '5px'},
                        )
                        for page in page_registry.values()
                    ],
                ),
            ],
        ),
        page_container,
    ]
)
