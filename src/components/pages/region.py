import dash
import pandas as pd
from dash import html, dcc, dash_table
from dash.dependencies import Input, Output, State
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
        html.H1("🌍 Regional Analysis Dashboard", style={'color': '#2c3e50', 'margin-bottom': '20px'}),
        
        # Filter Indicator
        html.Div(id="filter-indicator", style={
            'color': '#2c3e50', 'fontSize': 16, 'margin-bottom': '20px', 'text-align': 'center',
            'backgroundColor': '#e3f2fd', 'padding': '10px', 'borderRadius': '5px'
        }),
        
        html.Button("🔄 Reset", id="reset-filter-button", n_clicks=0, style={
            'background': 'linear-gradient(to right, #667eea, #764ba2)',
            'color': 'white',
            'padding': '12px 24px',
            'border': 'none',
            'borderRadius': '8px',
            'cursor': 'pointer',
            'fontSize': '16px',
            'marginBottom': '20px',
            'display': 'block',
            'marginLeft': 'auto',
            'marginRight': 'auto',
            'boxShadow': '0 3px 6px rgba(0, 0, 0, 0.1)'
        }),
        
        # Hidden div to store filter state
        dcc.Store(id='region-filter-state', data={'selected_state': None, 'selected_region': None}),
        
        # Regional Map
        html.Div([
            dcc.Graph(
                id="regional-map",
                config={
                    'scrollZoom': True,
                    'displayModeBar': True,
                    'modeBarButtonsToRemove': ['lasso2d', 'select2d'],
                    'doubleClick': 'reset',
                }
            )
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
        Output('region-filter-state', 'data'),
        [
            Input('reset-filter-button', 'n_clicks'),
            Input('regional-map', 'clickData'),
            Input('sales-by-region-chart', 'clickData'),
            Input('profit-by-state-chart', 'clickData')
        ],
        [State('region-filter-state', 'data')]
    )
    def update_filter_state(reset_clicks, map_click, region_click, state_click, current_state):
        ctx = dash.callback_context
        
        if not ctx.triggered:
            return current_state
            
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        # Reset filter state if reset button was clicked
        if trigger_id == 'reset-filter-button':
            return {'selected_state': None, 'selected_region': None}
        
        # Update based on which component was clicked
        new_state = current_state.copy()
        
        if trigger_id == 'regional-map' and map_click and 'points' in map_click:
            new_state['selected_state'] = map_click['points'][0].get('hovertext')
            new_state['selected_region'] = None
        elif trigger_id == 'profit-by-state-chart' and state_click and 'points' in state_click:
            new_state['selected_state'] = state_click['points'][0].get('y')
            new_state['selected_region'] = None
        elif trigger_id == 'sales-by-region-chart' and region_click and 'points' in region_click:
            new_state['selected_region'] = region_click['points'][0].get('x')
            new_state['selected_state'] = None
            
        return new_state

    @app.callback(
        [
            Output('regional-map', 'figure'),
            Output('sales-by-region-chart', 'figure'),
            Output('profit-by-state-chart', 'figure'),
            Output('top-cities-table', 'children'),
            Output('filter-indicator', 'children')
        ],
        [
            Input('current-page', 'data'),
            Input('region-filter-state', 'data')
        ]
    )
    def update_regional_charts(current_page, filter_state):
        df, _, _, _, _, _, _ = get_data()
        
        if current_page != 'region':
            return {}, {}, {}, [], ""
        
        selected_state = filter_state.get('selected_state')
        selected_region = filter_state.get('selected_region')
        
        # Update filter text
        if selected_state:
            filter_text = f"Filtered by State: {selected_state}"
        elif selected_region:
            filter_text = f"Filtered by Region: {selected_region}"
        else:
            filter_text = "No filter applied. Click on the map or charts to filter data."
        
        # Filter DataFrame
        filtered_df = df
        if selected_state:
            filtered_df = df[df['state'] == selected_state]
        elif selected_region:
            filtered_df = df[df['region'] == selected_region]
        
        # Regional Map
        region_sales = df.groupby(['state', 'lat', 'lng'])['sales'].sum().reset_index()
        region_sales['sales_scaled'] = region_sales['sales'] / region_sales['sales'].max() * 30

        regional_map = px.scatter_mapbox(
            region_sales,
            lat='lat',
            lon='lng',
            size='sales_scaled',
            color='sales',
            color_continuous_scale='Viridis',
            hover_name='state',
            hover_data={
                'sales': ':,.0f',
                'sales_scaled': False,
                'lat': False,
                'lng': False
            },
            title=f'🗺️ Sales Distribution by Location '
                  f'{"- " + selected_state if selected_state else "- " + selected_region if selected_region else ""}',
            mapbox_style='open-street-map',
            height=500,
            zoom=3.5,
            center={'lat': 37.0902, 'lon': -95.7129},
            opacity=0.7
        )
        regional_map.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            margin={'r': 20, 't': 50, 'l': 20, 'b': 20},
            title={'x': 0.5, 'xanchor': 'center', 'font': {'size': 20, 'color': '#2c3e50'}},
            mapbox_accesstoken=None,
            showlegend=True,
            mapbox=dict(
                zoom=5 if selected_state else 3.5,
                pitch=0,
                bearing=0,
                style='open-street-map',
                center=(
                    {'lat': region_sales[region_sales['state'] == selected_state]['lat'].iloc[0],
                     'lon': region_sales[region_sales['state'] == selected_state]['lng'].iloc[0]}
                    if selected_state else {'lat': 37.0902, 'lon': -95.7129}
                ),
                bounds={'west': -180, 'east': 180, 'south': -90, 'north': 90}
            )
        )
        
        # Sales by Region
        region_totals = filtered_df.groupby('region')['sales'].sum().reset_index()
        region_chart = px.bar(
            region_totals,
            x='region',
            y='sales',
            title=f'🌎 Sales by Region '
                  f'{"- " + selected_state if selected_state else "- " + selected_region if selected_region else ""}',
            color='sales',
            color_continuous_scale='Blues',
            text_auto='.2s'
        )
        region_chart.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis_title="Region",
            yaxis_title="Sales ($)",
            font=dict(size=12),
            showlegend=False
        )
        region_chart.update_traces(
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>Sales: $%{y:,.0f}<extra></extra>'
        )
        
        # Profit by State
        state_profit = filtered_df.groupby('state')['profit'].sum().nlargest(15).reset_index()
        state_chart = px.bar(
            state_profit,
            x='profit',
            y='state',
            title=f'💰 {"Profit by City in " + selected_state if selected_state else "Profit by State"}',
            orientation='h',
            color='profit',
            color_continuous_scale='Greens',
            text_auto='.2s'
        )
        state_chart.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            height=500,
            xaxis_title="Profit ($)",
            yaxis_title="State",
            font=dict(size=12),
            showlegend=False
        )
        state_chart.update_traces(
            textposition='auto',
            hovertemplate='<b>%{y}</b><br>Profit: $%{x:,.0f}<extra></extra>'
        )
        
        # Top Cities Table
        top_cities = filtered_df.groupby('city').agg({
            'sales': 'sum',
            'profit': 'sum',
            'order_key': 'nunique'
        }).round(2).reset_index()
        top_cities.columns = ['City', 'Sales ($)', 'Profit ($)', 'Orders']
        top_cities = top_cities.nlargest(10, 'Sales ($)')
        
        table = dash_table.DataTable(
            data=top_cities.to_dict('records'),
            columns=[
                {"name": i, "id": i, "type": "numeric", "format": {"specifier": ",.0f"}} if i != "City"
                else {"name": i, "id": i} for i in top_cities.columns
            ],
            style_cell={'textAlign': 'left', 'padding': '10px', 'fontSize': 14},
            style_header={
                'backgroundColor': '#667eea',
                'color': 'white',
                'fontWeight': 'bold',
                'textAlign': 'center'
            },
            style_data={'backgroundColor': '#f8f9fa'},
            style_data_conditional=[
                {
                    'if': {'row_index': i},
                    'backgroundColor': '#e3f2fd' if i % 2 == 0 else '#ffffff',
                    'color': 'black'
                } for i in range(len(top_cities))
            ],
            tooltip_data=[
                {
                    col: {'value': f"{row[col]:,.0f}" if col != 'City' else row[col], 'type': 'markdown'}
                    for col in top_cities.columns
                } for _, row in top_cities.iterrows()
            ],
            style_table={'overflowX': 'auto'},
        )
        
        return regional_map, region_chart, state_chart, table, filter_text