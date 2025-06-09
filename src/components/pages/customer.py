import pandas as pd
from dash import html, dcc, dash_table
from dash.dependencies import Input, Output
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
        html.H1("👥 Customer Analysis Dashboard", style={'color': '#2c3e50', 'margin-bottom': '30px'}),
        
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
        [Output('customer-segment-chart', 'figure'),
         Output('customer-value-dist', 'figure'),
         Output('repeat-customer-chart', 'figure'),
         Output('top-customers-table', 'children'),
         Output('monthly-customer-trend', 'figure')],
        [Input('current-page', 'data')]
    )
    def update_customer_charts(current_page):
        df, _, _, _, _, _, _ = get_data()
        print(f"Customer callback - current_page: {current_page}, df rows: {len(df)}")
        
        if current_page != 'customer':
            return {}, {}, {}, [], {}
        
        # Customer Segment
        segment_counts = df.groupby('segment')['customer_id'].nunique().reset_index()
        segment_chart = px.pie(segment_counts, values='customer_id', names='segment',
                              title='👥 Customer Distribution by Segment',
                              color_discrete_sequence=['#667eea', '#f5576c', '#43e97b'])
        segment_chart.update_layout(plot_bgcolor='white', paper_bgcolor='white')
        
        # Customer Value Distribution
        customer_values = df.groupby('customer_name')['sales'].sum().reset_index()
        value_dist = px.histogram(customer_values, x='sales', nbins=30,
                                 title='💵 Customer Value Distribution',
                                 color_discrete_sequence=['#667eea'])
        value_dist.update_layout(plot_bgcolor='white', paper_bgcolor='white')
        
        # Repeat Customer Analysis
        customer_orders = df.groupby('customer_name')['order_key'].nunique().reset_index()
        customer_orders['customer_type'] = customer_orders['order_key'].apply(lambda x: 'Repeat' if x > 1 else 'One-time')
        repeat_analysis = customer_orders['customer_type'].value_counts().reset_index()
        repeat_analysis.columns = ['customer_type', 'count']
        
        repeat_chart = px.bar(repeat_analysis, x='customer_type', y='count',
                             title='🔄 Repeat vs One-time Customers',
                             color='customer_type',
                             color_discrete_sequence=['#f5576c', '#43e97b'])
        repeat_chart.update_layout(plot_bgcolor='white', paper_bgcolor='white')
        
        # Top Customers Table
        top_customers = df.groupby('customer_name').agg({
            'sales': 'sum',
            'profit': 'sum',
            'order_key': 'nunique'
        }).round(2).reset_index()
        top_customers.columns = ['Customer', 'Sales ($)', 'Profit ($)', 'Orders']
        top_customers = top_customers.nlargest(10, 'Sales ($)')
        
        customer_table = dash_table.DataTable(
            data=top_customers.to_dict('records'),
            columns=[{"name": i, "id": i, "type": "numeric", "format": {"specifier": ",.0f"}} if i != "Customer" else {"name": i, "id": i} for i in top_customers.columns],
            style_cell={'textAlign': 'left', 'padding': '10px'},
            style_header={'backgroundColor': '#667eea', 'color': 'white', 'fontWeight': 'bold'},
            style_data={'backgroundColor': '#f8f9fa'}
        )
        
        # Monthly Customer Trend
        monthly_customers = df.groupby(['year', 'month'])['customer_id'].nunique().reset_index()
        monthly_customers['date'] = pd.to_datetime(monthly_customers[['year', 'month']].assign(day=1))
        
        customer_trend = px.line(monthly_customers, x='date', y='customer_id',
                               title='📅 Monthly Active Customers',
                               color_discrete_sequence=['#43e97b'])
        customer_trend.update_layout(plot_bgcolor='white', paper_bgcolor='white')
        customer_trend.update_traces(line=dict(width=3))
        
        return segment_chart, value_dist, repeat_chart, customer_table, customer_trend