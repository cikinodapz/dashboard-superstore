from dash import html
from src.config.styles import custom_style

def create_sidebar():
    return html.Div([
        html.Div([
            html.H2("📊 Superstore BI", style={'margin-bottom': '30px', 'text-align': 'center'}),
            html.Button("🏠 Overview", id="nav-overview", n_clicks=0, 
                       style=custom_style['nav-link']),
            html.Button("🌍 Analisis Wilayah", id="nav-region", n_clicks=0, 
                       style=custom_style['nav-link']),
            html.Button("👥 Analisis Pelanggan", id="nav-customer", n_clicks=0, 
                       style=custom_style['nav-link']),
            html.Button("💰 Diskon & Profit", id="nav-profit", n_clicks=0, 
                       style=custom_style['nav-link']),
        ])
    ], style=custom_style['sidebar'])