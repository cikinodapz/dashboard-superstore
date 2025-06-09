import pandas as pd
from dash import html, dcc, dash_table
from dash.dependencies import Input, Output
import plotly.express as px
from src.config.styles import custom_style
from src.data.data_loader import get_data

def create_region_page():
    df, _, _, _, _, _, _ = get_data()
    if df.empty:
        print("Region page: DataFrame is empty")
        return html.Div([
            html.H1("🌍 Regional Analysis Dashboard", style={'color': '#2c3e50', 'margin-bottom': '30px'}),
            html.P("⚠️ Tidak ada data tersedia. Periksa koneksi database atau file data_loader.py.", 
                   style={'color': '#e74c3c', 'text-align': 'center'})
        ])
    
    return html.Div([
        html.H1("🌍 Regional Analysis Dashboard", style={'color': '#2c3e50', 'margin-bottom': '30px'}),
        
        # Regional Map
        html.Div([
            dcc.Graph(id="regional-map")
        ], style=custom_style['card']),
        
        # Regional Charts
        html.Div([
            html.Div([
                dcc.Graph(id="sales-by-region-chart")
            ], style={**custom_style['card'], 'width': '50%'}),
            
            html.Div([
                dcc.Graph(id="profit-by-state-chart")
            ], style={**custom_style['card'], 'width': '50%'}),
        ], style={'display': 'flex', 'gap': '20px', 'margin-top': '20px'}),
        
        # Top Cities Table
        html.Div([
            html.H3("🏙️ Top 10 Cities by Sales", style={'color': '#2c3e50', 'margin-bottom': '20px'}),
            html.Div(id="top-cities-table")
        ], style=custom_style['card']),
    ])

def register_callbacks(app):
    @app.callback(
        [Output('regional-map', 'figure'),
         Output('sales-by-region-chart', 'figure'),
         Output('profit-by-state-chart', 'figure'),
         Output('top-cities-table', 'children')],
        [Input('current-page', 'data')]
    )
    def update_regional_charts(current_page):
        df, _, _, _, _, _, _ = get_data()
        print(f"Region callback - current_page: {current_page}, df rows: {len(df)}")
        
        if current_page != 'region':
            return {}, {}, {}, []
        
        # Regional Map
        region_sales = df.groupby(['state', 'lat', 'lng'])['sales'].sum().reset_index()
        
        regional_map = px.scatter_mapbox(region_sales, 
                                       lat='lat', lon='lng',
                                       size='sales',
                                       hover_name='state',
                                       hover_data={'sales': ':,.0f'},
                                       title='🗺️ Sales Distribution by Location',
                                       mapbox_style='open-street-map',
                                       height=500,
                                       zoom=3)
        regional_map.update_layout(plot_bgcolor='white', paper_bgcolor='white')
        
        # Sales by Region
        region_totals = df.groupby('region')['sales'].sum().reset_index()
        region_chart = px.bar(region_totals, x='region', y='sales',
                             title='🌎 Sales by Region',
                             color='sales',
                             color_continuous_scale='Blues')
        region_chart.update_layout(plot_bgcolor='white', paper_bgcolor='white')
        
        # Profit by State
        state_profit = df.groupby('state')['profit'].sum().nlargest(15).reset_index()
        state_chart = px.bar(state_profit, x='profit', y='state',
                            title='💰 Top 15 States by Profit',
                            orientation='h',
                            color='profit',
                            color_continuous_scale='Greens')
        state_chart.update_layout(plot_bgcolor='white', paper_bgcolor='white', height=500)
        
        # Top Cities Table
        top_cities = df.groupby('city').agg({
            'sales': 'sum',
            'profit': 'sum',
            'order_key': 'nunique'
        }).round(2).reset_index()
        top_cities.columns = ['City', 'Sales ($)', 'Profit ($)', 'Orders']
        top_cities = top_cities.nlargest(10, 'Sales ($)')
        
        table = dash_table.DataTable(
            data=top_cities.to_dict('records'),
            columns=[{"name": i, "id": i, "type": "numeric", "format": {"specifier": ",.0f"}} if i != "City" else {"name": i, "id": i} for i in top_cities.columns],
            style_cell={'textAlign': 'left', 'padding': '10px'},
            style_header={'backgroundColor': '#667eea', 'color': 'white', 'fontWeight': 'bold'},
            style_data={'backgroundColor': '#f8f9fa'},
            style_data_conditional=[
                {
                    'if': {'row_index': 0},
                    'backgroundColor': '#e3f2fd',
                    'color': 'black',
                }
            ]
        )
        
        return regional_map, region_chart, state_chart, table