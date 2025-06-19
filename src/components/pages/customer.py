import dash
import pandas as pd
from dash import html, dcc, dash_table
from dash.dependencies import Input, Output, State
import plotly.express as px
from src.config.styles import custom_style
from src.data.data_loader import get_data

def create_customer_page():
    df, _, _, _, _, _, _ = get_data()
    if df.empty:
        print("Customer page: DataFrame is empty")
        return html.Div([
            html.H1("👥 Customer Analysis Dashboard", style={'color': '#2c3e50', 'margin-bottom': '30px'}),
            html.P("⚠️ Tidak ada data tersedia. Periksa koneksi database atau file data_loader.py.", 
                   style={'color': '#e74c3c', 'text-align': 'center'})
        ])
    
    return html.Div([
        html.H1("👥 Customer Analysis Dashboard", style={'color': '#2c3e50', 'margin-bottom': '20px'}),
        
        # Filter Indicator
        html.Div(id="customer-filter-indicator", style={
            'color': '#2c3e50', 'fontSize': 16, 'margin-bottom': '20px', 'text-align': 'center',
            'backgroundColor': '#e3f2fd', 'padding': '10px', 'borderRadius': '5px'
        }),
        
        html.Button("🔄 Reset", id="customer-reset-button", n_clicks=0, style={
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
        dcc.Store(id='customer-filter-state', data={
            'selected_segment': None,
            'selected_customer_type': None,
            'selected_customer_name': None
        }),
        
        # Customer Metrics
        html.Div([
            html.Div([
                dcc.Graph(id="customer-segment-chart")
            ], style={**custom_style['card'], 'width': '33%'}),
            
            html.Div([
                dcc.Graph(id="customer-value-dist")
            ], style={**custom_style['card'], 'width': '33%'}),
            
            html.Div([
                dcc.Graph(id="repeat-customer-chart")
            ], style={**custom_style['card'], 'width': '33%'}),
        ], style={'display': 'flex', 'gap': '20px', 'margin-bottom': '20px'}),
        
        # Customer Details
        html.Div([
            html.Div([
                html.H3("🌟 Top 10 Customers", style={'color': '#2c3e50', 'margin-bottom': '20px'}),
                html.Div(id="top-customers-table")
            ], style={**custom_style['card'], 'width': '50%'}),
            
            html.Div([
                dcc.Graph(id="monthly-customer-trend")
            ], style={**custom_style['card'], 'width': '50%'}),
        ], style={'display': 'flex', 'gap': '20px'}),
    ])

def register_callbacks(app):
    @app.callback(
        Output('customer-filter-state', 'data'),
        [
            Input('customer-reset-button', 'n_clicks'),
            Input('customer-segment-chart', 'clickData'),
            Input('repeat-customer-chart', 'clickData'),
            Input('top-customers-table', 'active_cell')
        ],
        [State('customer-filter-state', 'data')]
    )
    def update_customer_filter_state(reset_clicks, segment_click, repeat_click, table_click, current_state):
        ctx = dash.callback_context
        
        if not ctx.triggered:
            return current_state
            
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        # Reset filter state if reset button was clicked
        if trigger_id == 'customer-reset-button':
            return {
                'selected_segment': None,
                'selected_customer_type': None,
                'selected_customer_name': None
            }
        
        # Update based on which component was clicked
        new_state = current_state.copy()
        
        if trigger_id == 'customer-segment-chart' and segment_click and 'points' in segment_click:
            new_state['selected_segment'] = segment_click['points'][0]['label']
            new_state['selected_customer_type'] = None
            new_state['selected_customer_name'] = None
            
        elif trigger_id == 'repeat-customer-chart' and repeat_click and 'points' in repeat_click:
            new_state['selected_customer_type'] = repeat_click['points'][0]['x']
            new_state['selected_segment'] = None
            new_state['selected_customer_name'] = None
            
        elif trigger_id == 'top-customers-table' and table_click:
            # This will be handled in the main callback using the filtered data
            pass
            
        return new_state

    @app.callback(
        [
            Output('customer-segment-chart', 'figure'),
            Output('customer-value-dist', 'figure'),
            Output('repeat-customer-chart', 'figure'),
            Output('top-customers-table', 'children'),
            Output('monthly-customer-trend', 'figure'),
            Output('customer-filter-indicator', 'children')
        ],
        [
            Input('current-page', 'data'),
            Input('customer-filter-state', 'data')
        ]
    )
    def update_customer_charts(current_page, filter_state):
        df, _, _, _, _, _, _ = get_data()
        
        if current_page != 'customer':
            return {}, {}, {}, [], {}, ""
        
        selected_segment = filter_state.get('selected_segment')
        selected_customer_type = filter_state.get('selected_customer_type')
        
        # Update filter text
        if selected_segment:
            filter_text = f"Filtered by Segment: {selected_segment}"
        elif selected_customer_type:
            filter_text = f"Filtered by Customer Type: {selected_customer_type}"
        else:
            filter_text = "No filter applied. Click on charts to filter data."
        
        # Filter DataFrame based on selections
        filtered_df = df
        if selected_segment:
            filtered_df = df[df['segment'] == selected_segment]
        elif selected_customer_type:
            customer_orders = df.groupby('customer_name')['order_key'].nunique().reset_index()
            repeat_customers = customer_orders[customer_orders['order_key'] > 1]['customer_name']
            if selected_customer_type == 'Repeat':
                filtered_df = df[df['customer_name'].isin(repeat_customers)]
            else:
                filtered_df = df[~df['customer_name'].isin(repeat_customers)]
        
        # Customer Segment Chart
        segment_counts = filtered_df.groupby('segment')['customer_id'].nunique().reset_index()
        segment_chart = px.pie(segment_counts, values='customer_id', names='segment',
                              title=f'👥 Customer Distribution by Segment {"- " + selected_segment if selected_segment else ""}',
                              color_discrete_sequence=['#667eea', '#f5576c', '#43e97b'])
        segment_chart.update_layout(plot_bgcolor='white', paper_bgcolor='white')
        
        # Customer Value Distribution
        customer_values = filtered_df.groupby('customer_name')['sales'].sum().reset_index()
        value_dist = px.histogram(customer_values, x='sales', nbins=30,
                                 title=f'💵 Customer Value Distribution {"- " + selected_segment if selected_segment else "- " + selected_customer_type if selected_customer_type else ""}',
                                 color_discrete_sequence=['#667eea'])
        value_dist.update_layout(plot_bgcolor='white', paper_bgcolor='white')
        
        # Repeat Customer Analysis
        customer_orders = filtered_df.groupby('customer_name')['order_key'].nunique().reset_index()
        customer_orders['customer_type'] = customer_orders['order_key'].apply(lambda x: 'Repeat' if x > 1 else 'One-time')
        repeat_analysis = customer_orders['customer_type'].value_counts().reset_index()
        repeat_analysis.columns = ['customer_type', 'count']
        
        repeat_chart = px.bar(repeat_analysis, x='customer_type', y='count',
                             title=f'🔄 Repeat vs One-time Customers {"- " + selected_segment if selected_segment else ""}',
                             color='customer_type',
                             color_discrete_sequence=['#f5576c', '#43e97b'])
        repeat_chart.update_layout(plot_bgcolor='white', paper_bgcolor='white')
        
        # Top Customers Table
        top_customers = filtered_df.groupby('customer_name').agg({
            'sales': 'sum',
            'profit': 'sum',
            'order_key': 'nunique'
        }).round(2).reset_index()
        top_customers.columns = ['Customer', 'Sales ($)', 'Profit ($)', 'Orders']
        top_customers = top_customers.nlargest(10, 'Sales ($)')
        
        customer_table = dash_table.DataTable(
            data=top_customers.to_dict('records'),
            columns=[{"name": i, "id": i, "type": "numeric", "format": {"specifier": ",.0f"}} if i != "Customer" else {"name": i, "id": i} for i in top_customers.columns],
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
                } for i in range(len(top_customers))
            ],
            tooltip_data=[
                {
                    col: {'value': f"{row[col]:,.0f}" if col != 'Customer' else row[col], 'type': 'markdown'}
                    for col in top_customers.columns
                } for _, row in top_customers.iterrows()
            ],
            style_table={'overflowX': 'auto'},
        )
        
        # Monthly Customer Trend
        monthly_customers = filtered_df.groupby(['year', 'month'])['customer_id'].nunique().reset_index()
        monthly_customers['date'] = pd.to_datetime(monthly_customers[['year', 'month']].assign(day=1))
        
        customer_trend = px.line(monthly_customers, x='date', y='customer_id',
                               title=f'📅 Monthly Active Customers {"- " + selected_segment if selected_segment else "- " + selected_customer_type if selected_customer_type else ""}',
                               color_discrete_sequence=['#43e97b'])
        customer_trend.update_layout(plot_bgcolor='white', paper_bgcolor='white')
        customer_trend.update_traces(line=dict(width=3))
        
        return segment_chart, value_dist, repeat_chart, customer_table, customer_trend, filter_text