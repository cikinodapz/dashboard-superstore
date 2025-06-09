# import dash
# from dash import dcc, html, Input, Output, callback, dash_table
# import plotly.express as px
# import plotly.graph_objects as go
# from plotly.subplots import make_subplots
# import pandas as pd
# from sqlalchemy import create_engine
# import psycopg2
# from datetime import datetime, date
# import numpy as np

# # 🔌 Database Connection
# def get_db_connection():
#     DB_USER = 'postgres'
#     DB_PASS = '18agustuz203'
#     DB_HOST = 'localhost'
#     DB_PORT = '5432'
#     DB_NAME = 'dwh_superstore2'
    
#     engine = create_engine(f'postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}')
#     return engine

# # 📊 Load Data
# def load_data():
#     engine = get_db_connection()
    
#     # Load all dimension and fact tables
#     dim_customer = pd.read_sql("SELECT * FROM dim_customer", engine)
#     dim_product = pd.read_sql("SELECT * FROM dim_product", engine)
#     dim_order = pd.read_sql("SELECT * FROM dim_order", engine)
#     dim_time = pd.read_sql("SELECT * FROM dim_time", engine)
#     dim_region = pd.read_sql("SELECT * FROM dim_region", engine)
#     fact_sales = pd.read_sql("SELECT * FROM fact_sales", engine)
    
#     # Create comprehensive dataset for analysis
#     df = (fact_sales
#           .merge(dim_customer, on='customer_key', how='left')
#           .merge(dim_product, on='product_key', how='left')
#           .merge(dim_order, on='order_key', how='left')
#           .merge(dim_time, on='time_key', how='left')
#           .merge(dim_region, on='region_key', how='left'))
    
#     # Convert date column if needed
#     if 'order_date' in df.columns:
#         df['order_date'] = pd.to_datetime(df['order_date'])
    
#     return df, dim_customer, dim_product, dim_order, dim_time, dim_region, fact_sales

# # Load data
# df, dim_customer, dim_product, dim_order, dim_time, dim_region, fact_sales = load_data()

# # 🎨 Initialize Dash App
# app = dash.Dash(__name__, suppress_callback_exceptions=True)
# app.title = "Superstore BI Dashboard"

# # 🎨 Custom CSS Styles
# custom_style = {
#     'sidebar': {
#         'position': 'fixed',
#         'top': 0,
#         'left': 0,
#         'bottom': 0,
#         'width': '250px',
#         'padding': '20px',
#         'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
#         'color': 'white',
#         'box-shadow': '2px 0 10px rgba(0,0,0,0.1)',
#         'z-index': 1000
#     },
#     'content': {
#         'margin-left': '270px',
#         'padding': '20px',
#         'background-color': '#f8f9fa',
#         'min-height': '100vh'
#     },
#     'nav-link': {
#         'display': 'block',
#         'padding': '12px 20px',
#         'color': 'white',
#         'text-decoration': 'none',
#         'border-radius': '8px',
#         'margin': '5px 0',
#         'transition': 'all 0.3s ease',
#         'cursor': 'pointer',
#         'border': 'none',
#         'background': 'transparent',
#         'width': '100%',
#         'text-align': 'left'
#     },
#     'nav-link-active': {
#         'background': 'rgba(255,255,255,0.2)',
#         'box-shadow': '0 2px 10px rgba(0,0,0,0.1)'
#     },
#     'card': {
#         'background': 'white',
#         'border-radius': '12px',
#         'padding': '20px',
#         'margin': '10px 0',
#         'box-shadow': '0 2px 20px rgba(0,0,0,0.1)',
#         'border': '1px solid #e9ecef'
#     },
#     'metric-card': {
#         'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
#         'color': 'white',
#         'border-radius': '12px',
#         'padding': '20px',
#         'text-align': 'center',
#         'box-shadow': '0 4px 20px rgba(102, 126, 234, 0.3)'
#     }
# }

# # 🧭 Sidebar Navigation
# def create_sidebar():
#     return html.Div([
#         html.Div([
#             html.H2("📊 Superstore BI", style={'margin-bottom': '30px', 'text-align': 'center'}),
#             html.Button("🏠 Overview", id="nav-overview", n_clicks=0, 
#                        style=custom_style['nav-link']),
#             html.Button("🌍 Analisis Wilayah", id="nav-region", n_clicks=0, 
#                        style=custom_style['nav-link']),
#             html.Button("👥 Analisis Pelanggan", id="nav-customer", n_clicks=0, 
#                        style=custom_style['nav-link']),
#             html.Button("💰 Diskon & Profit", id="nav-profit", n_clicks=0, 
#                        style=custom_style['nav-link']),
#         ])
#     ], style=custom_style['sidebar'])

# # 📈 Overview Page
# def create_overview_page():
#     # Calculate key metrics
#     total_sales = df['sales'].sum()
#     total_profit = df['profit'].sum()
#     total_orders = df['order_key'].nunique()
#     avg_discount = df['discount'].mean() * 100
    
#     return html.Div([
#         html.H1("📊 Sales Overview Dashboard", style={'color': '#2c3e50', 'margin-bottom': '30px'}),
        
#         # Key Metrics Row
#         html.Div([
#             html.Div([
#                 html.H3(f"${total_sales:,.0f}", style={'margin': '0', 'font-size': '28px'}),
#                 html.P("Total Sales", style={'margin': '5px 0 0 0'})
#             ], style={**custom_style['metric-card'], 'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'}),
            
#             html.Div([
#                 html.H3(f"${total_profit:,.0f}", style={'margin': '0', 'font-size': '28px'}),
#                 html.P("Total Profit", style={'margin': '5px 0 0 0'})
#             ], style={**custom_style['metric-card'], 'background': 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)'}),
            
#             html.Div([
#                 html.H3(f"{total_orders:,}", style={'margin': '0', 'font-size': '28px'}),
#                 html.P("Total Orders", style={'margin': '5px 0 0 0'})
#             ], style={**custom_style['metric-card'], 'background': 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)'}),
            
#             html.Div([
#                 html.H3(f"{avg_discount:.1f}%", style={'margin': '0', 'font-size': '28px'}),
#                 html.P("Avg Discount", style={'margin': '5px 0 0 0'})
#             ], style={**custom_style['metric-card'], 'background': 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)'}),
#         ], style={'display': 'grid', 'grid-template-columns': 'repeat(4, 1fr)', 'gap': '20px', 'margin-bottom': '30px'}),
        
#         # Charts Row 1
#         html.Div([
#             html.Div([
#                 dcc.Graph(id="sales-trend-chart")
#             ], style={**custom_style['card'], 'width': '60%'}),
            
#             html.Div([
#                 dcc.Graph(id="category-pie-chart")
#             ], style={**custom_style['card'], 'width': '38%'}),
#         ], style={'display': 'flex', 'gap': '20px', 'margin-bottom': '20px'}),
        
#         # Charts Row 2
#         html.Div([
#             html.Div([
#                 dcc.Graph(id="top-products-chart")
#             ], style={**custom_style['card'], 'width': '50%'}),
            
#             html.Div([
#                 dcc.Graph(id="segment-performance-chart")
#             ], style={**custom_style['card'], 'width': '50%'}),
#         ], style={'display': 'flex', 'gap': '20px'}),
#     ])

# # 🌍 Regional Analysis Page
# def create_region_page():
#     return html.Div([
#         html.H1("🌍 Regional Analysis Dashboard", style={'color': '#2c3e50', 'margin-bottom': '30px'}),
        
#         # Regional Map
#         html.Div([
#             dcc.Graph(id="regional-map")
#         ], style=custom_style['card']),
        
#         # Regional Charts
#         html.Div([
#             html.Div([
#                 dcc.Graph(id="sales-by-region-chart")
#             ], style={**custom_style['card'], 'width': '50%'}),
            
#             html.Div([
#                 dcc.Graph(id="profit-by-state-chart")
#             ], style={**custom_style['card'], 'width': '50%'}),
#         ], style={'display': 'flex', 'gap': '20px', 'margin-top': '20px'}),
        
#         # Top Cities Table
#         html.Div([
#             html.H3("🏙️ Top 10 Cities by Sales", style={'color': '#2c3e50', 'margin-bottom': '20px'}),
#             html.Div(id="top-cities-table")
#         ], style=custom_style['card']),
#     ])

# # 👥 Customer Analysis Page
# def create_customer_page():
#     return html.Div([
#         html.H1("👥 Customer Analysis Dashboard", style={'color': '#2c3e50', 'margin-bottom': '30px'}),
        
#         # Customer Metrics
#         html.Div([
#             html.Div([
#                 dcc.Graph(id="customer-segment-chart")
#             ], style={**custom_style['card'], 'width': '33%'}),
            
#             html.Div([
#                 dcc.Graph(id="customer-value-dist")
#             ], style={**custom_style['card'], 'width': '33%'}),
            
#             html.Div([
#                 dcc.Graph(id="repeat-customer-chart")
#             ], style={**custom_style['card'], 'width': '33%'}),
#         ], style={'display': 'flex', 'gap': '20px', 'margin-bottom': '20px'}),
        
#         # Customer Details
#         html.Div([
#             html.Div([
#                 html.H3("🌟 Top 10 Customers", style={'color': '#2c3e50', 'margin-bottom': '20px'}),
#                 html.Div(id="top-customers-table")
#             ], style={**custom_style['card'], 'width': '50%'}),
            
#             html.Div([
#                 dcc.Graph(id="monthly-customer-trend")
#             ], style={**custom_style['card'], 'width': '50%'}),
#         ], style={'display': 'flex', 'gap': '20px'}),
#     ])

# # 💰 Discount & Profit Page
# def create_profit_page():
#     return html.Div([
#         html.H1("💰 Discount & Profit Analysis", style={'color': '#2c3e50', 'margin-bottom': '30px'}),
        
#         # Profit Metrics
#         html.Div([
#             html.Div([
#                 dcc.Graph(id="profit-margin-chart")
#             ], style={**custom_style['card'], 'width': '50%'}),
            
#             html.Div([
#                 dcc.Graph(id="discount-impact-chart")
#             ], style={**custom_style['card'], 'width': '50%'}),
#         ], style={'display': 'flex', 'gap': '20px', 'margin-bottom': '20px'}),
        
#         # Detailed Analysis
#         html.Div([
#             html.Div([
#                 dcc.Graph(id="category-profitability")
#             ], style={**custom_style['card'], 'width': '60%'}),
            
#             html.Div([
#                 dcc.Graph(id="discount-distribution")
#             ], style={**custom_style['card'], 'width': '40%'}),
#         ], style={'display': 'flex', 'gap': '20px', 'margin-bottom': '20px'}),
        
#         # Loss Analysis
#         html.Div([
#             html.H3("⚠️ Products with Losses", style={'color': '#e74c3c', 'margin-bottom': '20px'}),
#             html.Div(id="loss-products-table")
#         ], style=custom_style['card']),
#     ])

# # 🎯 Main App Layout
# app.layout = html.Div([
#     dcc.Store(id='current-page', data='overview'),
#     create_sidebar(),
#     html.Div(id='page-content', style=custom_style['content'])
# ])

# # 🔄 Navigation Callback
# @app.callback(
#     [Output('current-page', 'data'),
#      Output('nav-overview', 'style'),
#      Output('nav-region', 'style'),
#      Output('nav-customer', 'style'),  
#      Output('nav-profit', 'style')],
#     [Input('nav-overview', 'n_clicks'),
#      Input('nav-region', 'n_clicks'),
#      Input('nav-customer', 'n_clicks'),
#      Input('nav-profit', 'n_clicks')]
# )
# def update_page(overview_clicks, region_clicks, customer_clicks, profit_clicks):
#     ctx = dash.callback_context
    
#     if not ctx.triggered:
#         return 'overview', {**custom_style['nav-link'], **custom_style['nav-link-active']}, custom_style['nav-link'], custom_style['nav-link'], custom_style['nav-link']
    
#     button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
#     styles = [custom_style['nav-link']] * 4
    
#     if button_id == 'nav-overview':
#         styles[0] = {**custom_style['nav-link'], **custom_style['nav-link-active']}
#         return 'overview', *styles
#     elif button_id == 'nav-region':
#         styles[1] = {**custom_style['nav-link'], **custom_style['nav-link-active']}
#         return 'region', *styles
#     elif button_id == 'nav-customer':
#         styles[2] = {**custom_style['nav-link'], **custom_style['nav-link-active']}
#         return 'customer', *styles
#     elif button_id == 'nav-profit':
#         styles[3] = {**custom_style['nav-link'], **custom_style['nav-link-active']}
#         return 'profit', *styles
    
#     return 'overview', {**custom_style['nav-link'], **custom_style['nav-link-active']}, custom_style['nav-link'], custom_style['nav-link'], custom_style['nav-link']

# # 📄 Page Content Callback
# @app.callback(Output('page-content', 'children'), [Input('current-page', 'data')])
# def display_page(current_page):
#     if current_page == 'overview':
#         return create_overview_page()
#     elif current_page == 'region':
#         return create_region_page()
#     elif current_page == 'customer':
#         return create_customer_page()
#     elif current_page == 'profit':
#         return create_profit_page()
#     return create_overview_page()

# # 📊 Overview Charts Callbacks
# @app.callback(
#     [Output('sales-trend-chart', 'figure'),
#      Output('category-pie-chart', 'figure'),
#      Output('top-products-chart', 'figure'),
#      Output('segment-performance-chart', 'figure')],
#     [Input('current-page', 'data')]
# )
# def update_overview_charts(current_page):
#     if current_page != 'overview':
#         return {}, {}, {}, {}
    
#     # Sales Trend
#     monthly_sales = df.groupby(['year', 'month'])['sales'].sum().reset_index()
#     monthly_sales['date'] = pd.to_datetime(monthly_sales[['year', 'month']].assign(day=1))
    
#     sales_trend = px.line(monthly_sales, x='date', y='sales', 
#                          title='📈 Monthly Sales Trend',
#                          color_discrete_sequence=['#667eea'])
#     sales_trend.update_layout(plot_bgcolor='white', paper_bgcolor='white')
#     sales_trend.update_traces(line=dict(width=3))
    
#     # Category Pie
#     category_sales = df.groupby('category')['sales'].sum().reset_index()
#     category_pie = px.pie(category_sales, values='sales', names='category',
#                          title='🏷️ Sales by Category',
#                          color_discrete_sequence=px.colors.qualitative.Set3)
#     category_pie.update_layout(plot_bgcolor='white', paper_bgcolor='white')
    
#     # Top Products
#     top_products = df.groupby('product_name')['sales'].sum().nlargest(10).reset_index()
#     top_products_chart = px.bar(top_products, x='sales', y='product_name',
#                                title='🏆 Top 10 Products by Sales',
#                                orientation='h',
#                                color='sales',
#                                color_continuous_scale='Viridis')
#     top_products_chart.update_layout(plot_bgcolor='white', paper_bgcolor='white', height=400)
    
#     # Segment Performance
#     segment_metrics = df.groupby('segment').agg({
#         'sales': 'sum',
#         'profit': 'sum',
#         'quantity': 'sum'
#     }).reset_index()
    
#     segment_chart = px.bar(segment_metrics, x='segment', y=['sales', 'profit'],
#                           title='💼 Performance by Customer Segment',
#                           barmode='group',
#                           color_discrete_sequence=['#667eea', '#f5576c'])
#     segment_chart.update_layout(plot_bgcolor='white', paper_bgcolor='white')
    
#     return sales_trend, category_pie, top_products_chart, segment_chart

# # 🌍 Regional Charts Callbacks
# @app.callback(
#     [Output('regional-map', 'figure'),
#      Output('sales-by-region-chart', 'figure'),
#      Output('profit-by-state-chart', 'figure'),
#      Output('top-cities-table', 'children')],
#     [Input('current-page', 'data')]
# )
# def update_regional_charts(current_page):
#     if current_page != 'region':
#         return {}, {}, {}, []
    
#     # Regional Map
#     region_sales = df.groupby(['state', 'lat', 'lng'])['sales'].sum().reset_index()
    
#     regional_map = px.scatter_mapbox(region_sales, 
#                                    lat='lat', lon='lng',
#                                    size='sales',
#                                    hover_name='state',
#                                    hover_data={'sales': ':,.0f'},
#                                    title='🗺️ Sales Distribution by Location',
#                                    mapbox_style='open-street-map',
#                                    height=500,
#                                    zoom=3)
#     regional_map.update_layout(plot_bgcolor='white', paper_bgcolor='white')
    
#     # Sales by Region
#     region_totals = df.groupby('region')['sales'].sum().reset_index()
#     region_chart = px.bar(region_totals, x='region', y='sales',
#                          title='🌎 Sales by Region',
#                          color='sales',
#                          color_continuous_scale='Blues')
#     region_chart.update_layout(plot_bgcolor='white', paper_bgcolor='white')
    
#     # Profit by State
#     state_profit = df.groupby('state')['profit'].sum().nlargest(15).reset_index()
#     state_chart = px.bar(state_profit, x='profit', y='state',
#                         title='💰 Top 15 States by Profit',
#                         orientation='h',
#                         color='profit',
#                         color_continuous_scale='Greens')
#     state_chart.update_layout(plot_bgcolor='white', paper_bgcolor='white', height=500)
    
#     # Top Cities Table
#     top_cities = df.groupby('city').agg({
#         'sales': 'sum',
#         'profit': 'sum',
#         'order_key': 'nunique'
#     }).round(2).reset_index()
#     top_cities.columns = ['City', 'Sales ($)', 'Profit ($)', 'Orders']
#     top_cities = top_cities.nlargest(10, 'Sales ($)')
    
#     table = dash_table.DataTable(
#         data=top_cities.to_dict('records'),
#         columns=[{"name": i, "id": i, "type": "numeric", "format": {"specifier": ",.0f"}} if i != "City" else {"name": i, "id": i} for i in top_cities.columns],
#         style_cell={'textAlign': 'left', 'padding': '10px'},
#         style_header={'backgroundColor': '#667eea', 'color': 'white', 'fontWeight': 'bold'},
#         style_data={'backgroundColor': '#f8f9fa'},
#         style_data_conditional=[
#             {
#                 'if': {'row_index': 0},
#                 'backgroundColor': '#e3f2fd',
#                 'color': 'black',
#             }
#         ]
#     )
    
#     return regional_map, region_chart, state_chart, table

# # 👥 Customer Charts Callbacks  
# @app.callback(
#     [Output('customer-segment-chart', 'figure'),
#      Output('customer-value-dist', 'figure'),
#      Output('repeat-customer-chart', 'figure'),
#      Output('top-customers-table', 'children'),
#      Output('monthly-customer-trend', 'figure')],
#     [Input('current-page', 'data')]
# )
# def update_customer_charts(current_page):
#     if current_page != 'customer':
#         return {}, {}, {}, [], {}
    
#     # Customer Segment
#     segment_counts = df.groupby('segment')['customer_id'].nunique().reset_index()
#     segment_chart = px.pie(segment_counts, values='customer_id', names='segment',
#                           title='👥 Customer Distribution by Segment',
#                           color_discrete_sequence=['#667eea', '#f5576c', '#43e97b'])
#     segment_chart.update_layout(plot_bgcolor='white', paper_bgcolor='white')
    
#     # Customer Value Distribution
#     customer_values = df.groupby('customer_name')['sales'].sum().reset_index()
#     value_dist = px.histogram(customer_values, x='sales', nbins=30,
#                              title='💵 Customer Value Distribution',
#                              color_discrete_sequence=['#667eea'])
#     value_dist.update_layout(plot_bgcolor='white', paper_bgcolor='white')
    
#     # Repeat Customer Analysis
#     customer_orders = df.groupby('customer_name')['order_key'].nunique().reset_index()
#     customer_orders['customer_type'] = customer_orders['order_key'].apply(lambda x: 'Repeat' if x > 1 else 'One-time')
#     repeat_analysis = customer_orders['customer_type'].value_counts().reset_index()
#     repeat_analysis.columns = ['customer_type', 'count']
    
#     repeat_chart = px.bar(repeat_analysis, x='customer_type', y='count',
#                          title='🔄 Repeat vs One-time Customers',
#                          color='customer_type',
#                          color_discrete_sequence=['#f5576c', '#43e97b'])
#     repeat_chart.update_layout(plot_bgcolor='white', paper_bgcolor='white')
    
#     # Top Customers Table
#     top_customers = df.groupby('customer_name').agg({
#         'sales': 'sum',
#         'profit': 'sum',
#         'order_key': 'nunique'
#     }).round(2).reset_index()
#     top_customers.columns = ['Customer', 'Sales ($)', 'Profit ($)', 'Orders']
#     top_customers = top_customers.nlargest(10, 'Sales ($)')
    
#     customer_table = dash_table.DataTable(
#         data=top_customers.to_dict('records'),
#         columns=[{"name": i, "id": i, "type": "numeric", "format": {"specifier": ",.0f"}} if i != "Customer" else {"name": i, "id": i} for i in top_customers.columns],
#         style_cell={'textAlign': 'left', 'padding': '10px'},
#         style_header={'backgroundColor': '#667eea', 'color': 'white', 'fontWeight': 'bold'},
#         style_data={'backgroundColor': '#f8f9fa'}
#     )
    
#     # Monthly Customer Trend
#     monthly_customers = df.groupby(['year', 'month'])['customer_id'].nunique().reset_index()
#     monthly_customers['date'] = pd.to_datetime(monthly_customers[['year', 'month']].assign(day=1))
    
#     customer_trend = px.line(monthly_customers, x='date', y='customer_id',
#                            title='📅 Monthly Active Customers',
#                            color_discrete_sequence=['#43e97b'])
#     customer_trend.update_layout(plot_bgcolor='white', paper_bgcolor='white')
#     customer_trend.update_traces(line=dict(width=3))
    
#     return segment_chart, value_dist, repeat_chart, customer_table, customer_trend

# @app.callback(
#     [Output('profit-margin-chart', 'figure'),
#      Output('discount-impact-chart', 'figure'),
#      Output('category-profitability', 'figure'),
#      Output('discount-distribution', 'figure'),
#      Output('loss-products-table', 'children')],
#     [Input('current-page', 'data')]
# )
# def update_profit_charts(current_page):
#     if current_page != 'profit':
#         return {}, {}, {}, {}, []
    
#     # Profit Margin by Category
#     category_profit = df.groupby('category').agg({
#         'sales': 'sum',
#         'profit': 'sum'
#     }).reset_index()
#     category_profit['profit_margin'] = (category_profit['profit'] / category_profit['sales'] * 100).round(2)
    
#     margin_chart = px.bar(category_profit, x='category', y='profit_margin',
#                          title='📊 Profit Margin by Category (%)',
#                          color='profit_margin',
#                          color_continuous_scale='RdYlGn')
#     margin_chart.update_layout(plot_bgcolor='white', paper_bgcolor='white')
    
#     # Discount Impact
#     df['discount_range'] = pd.cut(df['discount'], bins=[0, 0.1, 0.2, 0.3, 1.0], 
#                                  labels=['0-10%', '10-20%', '20-30%', '30%+'])
#     discount_impact = df.groupby('discount_range').agg({
#         'sales': 'sum',
#         'profit': 'sum'
#     }).reset_index()
    
#     impact_chart = px.bar(discount_impact, x='discount_range', y=['sales', 'profit'],
#                          title='💸 Discount Impact on Sales & Profit',
#                          barmode='group',
#                          color_discrete_sequence=['#667eea', '#f5576c'])
#     impact_chart.update_layout(plot_bgcolor='white', paper_bgcolor='white')
    
#     # Category Profitability - Modified to use available columns
#     # First check if 'sub_category' exists, if not use another column
#     groupby_columns = ['category']
#     if 'sub_category' in df.columns:
#         groupby_columns.append('sub_category')
    
#     cat_profit_detail = df.groupby(groupby_columns).agg({
#         'profit': 'sum',
#         'sales': 'sum'
#     }).reset_index()
    
#     # Create hover data based on available columns
#     hover_data = {}
#     if 'sub_category' in df.columns:
#         hover_data['sub_category'] = True
    
#     profitability_chart = px.scatter(cat_profit_detail, x='sales', y='profit',
#                                    color='category', size='profit',
#                                    hover_data=hover_data,
#                                    title='💎 Category Profitability Matrix')
#     profitability_chart.update_layout(plot_bgcolor='white', paper_bgcolor='white')
    
#     # Discount Distribution
#     discount_dist = px.histogram(df, x='discount', nbins=20,
#                                title='📈 Discount Distribution',
#                                color_discrete_sequence=['#f5576c'])
#     discount_dist.update_layout(plot_bgcolor='white', paper_bgcolor='white')
    
#     # Loss Products Table
#     loss_products = df.groupby('product_name')['profit'].sum().reset_index()
#     loss_products = loss_products[loss_products['profit'] < 0].nsmallest(10, 'profit')
#     loss_products.columns = ['Product', 'Loss ($)']
#     loss_products['Loss ($)'] = loss_products['Loss ($)'].round(2)
    
#     if not loss_products.empty:
#         loss_table = dash_table.DataTable(
#             data=loss_products.to_dict('records'),
#             columns=[{"name": i, "id": i, "type": "numeric", "format": {"specifier": ",.2f"}} if 'Loss' in i else {"name": i, "id": i} for i in loss_products.columns],
#             style_cell={'textAlign': 'left', 'padding': '10px'},
#             style_header={'backgroundColor': '#e74c3c', 'color': 'white', 'fontWeight': 'bold'},
#             style_data={'backgroundColor': '#fdf2f2'},
#         )
#     else:
#         loss_table = html.P("🎉 No products with losses found!", style={'text-align': 'center', 'color': '#27ae60'})
    
#     return margin_chart, impact_chart, profitability_chart, discount_dist, loss_table

# # 🚀 Run the App
# if __name__ == '__main__':
#     app.run(debug=True, port=8050)

# # 🎯 Additional Features & Enhancements

# # 📱 Responsive Design Enhancement
# def add_responsive_styles():
#     """Add responsive CSS for mobile compatibility"""
#     return {
#         '@media (max-width: 768px)': {
#             'sidebar': {'width': '100%', 'position': 'static'},
#             'content': {'margin-left': '0px'},
#             'grid-template-columns': 'repeat(2, 1fr)'
#         }
#     }

# # 📊 Advanced Analytics Functions
# def calculate_customer_lifetime_value():
#     """Calculate Customer Lifetime Value"""
#     customer_metrics = df.groupby('customer_name').agg({
#         'sales': 'sum',
#         'profit': 'sum',
#         'order_key': 'nunique',
#         'order_date': ['min', 'max']
#     }).reset_index()
    
#     customer_metrics.columns = ['customer_name', 'total_sales', 'total_profit', 
#                                'total_orders', 'first_order', 'last_order']
    
#     # Calculate customer lifespan in days
#     customer_metrics['lifespan_days'] = (
#         pd.to_datetime(customer_metrics['last_order']) - 
#         pd.to_datetime(customer_metrics['first_order'])
#     ).dt.days + 1
    
#     # Calculate CLV metrics
#     customer_metrics['avg_order_value'] = customer_metrics['total_sales'] / customer_metrics['total_orders']
#     customer_metrics['purchase_frequency'] = customer_metrics['total_orders'] / (customer_metrics['lifespan_days'] / 365)
#     customer_metrics['clv'] = customer_metrics['avg_order_value'] * customer_metrics['purchase_frequency'] * 2  # Assuming 2-year projection
    
#     return customer_metrics

# def seasonal_analysis():
#     """Analyze seasonal trends"""
#     df['season'] = df['month'].map({
#         12: 'Winter', 1: 'Winter', 2: 'Winter',
#         3: 'Spring', 4: 'Spring', 5: 'Spring',
#         6: 'Summer', 7: 'Summer', 8: 'Summer',
#         9: 'Fall', 10: 'Fall', 11: 'Fall'
#     })
    
#     seasonal_data = df.groupby(['season', 'category']).agg({
#         'sales': 'sum',
#         'profit': 'sum',
#         'quantity': 'sum'
#     }).reset_index()
    
#     return seasonal_data

# def market_basket_analysis():
#     """Simple market basket analysis"""
#     # Group products bought together
#     order_products = df.groupby('order_id')['product_name'].apply(list).reset_index()
    
#     # Find frequently bought together items
#     from itertools import combinations
#     product_pairs = []
    
#     for products in order_products['product_name']:
#         if len(products) > 1:
#             for pair in combinations(products, 2):
#                 product_pairs.append(sorted(pair))
    
#     pair_counts = pd.Series(product_pairs).value_counts().head(20)
#     return pair_counts

# # 🎨 Enhanced Color Schemes
# color_schemes = {
#     'primary': ['#667eea', '#764ba2'],
#     'success': ['#43e97b', '#38f9d7'],
#     'warning': ['#f093fb', '#f5576c'],
#     'info': ['#4facfe', '#00f2fe'],
#     'gradient_backgrounds': [
#         'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
#         'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
#         'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
#         'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)'
#     ]
# }

# # 📈 Export Functions
# def export_dashboard_data():
#     """Export processed data for external use"""
#     export_data = {
#         'sales_summary': df.groupby(['year', 'month', 'category']).agg({
#             'sales': 'sum',
#             'profit': 'sum',
#             'quantity': 'sum'
#         }).reset_index(),
        
#         'customer_summary': df.groupby(['customer_name', 'segment']).agg({
#             'sales': 'sum',
#             'profit': 'sum',
#             'order_key': 'nunique'
#         }).reset_index(),
        
#         'product_performance': df.groupby(['product_name', 'category', 'sub_category']).agg({
#             'sales': 'sum',
#             'profit': 'sum',
#             'quantity': 'sum'
#         }).reset_index(),
        
#         'regional_analysis': df.groupby(['region', 'state', 'city']).agg({
#             'sales': 'sum',
#             'profit': 'sum',
#             'order_key': 'nunique'
#         }).reset_index()
#     }
    
#     return export_data

# # 🔍 Advanced Filtering Functions
# def create_date_filter():
#     """Create date range filter component"""
#     return dcc.DatePickerRange(
#         id='date-picker-range',
#         start_date=df['order_date'].min(),
#         end_date=df['order_date'].max(),
#         display_format='YYYY-MM-DD',
#         style={'margin': '10px'}
#     )

# def create_category_filter():
#     """Create category filter dropdown"""
#     return dcc.Dropdown(
#         id='category-filter',
#         options=[{'label': cat, 'value': cat} for cat in df['category'].unique()],
#         value=df['category'].unique().tolist(),
#         multi=True,
#         placeholder="Select Categories",
#         style={'margin': '10px'}
#     )

# # 📊 Additional Chart Functions
# def create_advanced_charts():
#     """Create more sophisticated chart visualizations"""
    
#     # Correlation Heatmap
#     def correlation_heatmap():
#         corr_data = df[['sales', 'profit', 'discount', 'quantity', 'shipping_cost']].corr()
        
#         heatmap = px.imshow(corr_data, 
#                            title='🔥 Correlation Heatmap',
#                            color_continuous_scale='RdBu',
#                            aspect='auto')
#         heatmap.update_layout(plot_bgcolor='white', paper_bgcolor='white')
#         return heatmap
    
#     # Time Series Decomposition
#     def sales_decomposition():
#         monthly_sales = df.groupby(['year', 'month'])['sales'].sum().reset_index()
#         monthly_sales['date'] = pd.to_datetime(monthly_sales[['year', 'month']].assign(day=1))
#         monthly_sales = monthly_sales.set_index('date').sort_index()
        
#         # Simple trend calculation
#         monthly_sales['trend'] = monthly_sales['sales'].rolling(window=3, center=True).mean()
        
#         decomp_fig = make_subplots(rows=2, cols=1, 
#                                   subplot_titles=['Original Sales', 'Trend'],
#                                   vertical_spacing=0.1)
        
#         decomp_fig.add_trace(go.Scatter(x=monthly_sales.index, y=monthly_sales['sales'],
#                                        name='Original', line=dict(color='#667eea')), row=1, col=1)
#         decomp_fig.add_trace(go.Scatter(x=monthly_sales.index, y=monthly_sales['trend'],
#                                        name='Trend', line=dict(color='#f5576c')), row=2, col=1)
        
#         decomp_fig.update_layout(title='📈 Sales Time Series Analysis',
#                                plot_bgcolor='white', paper_bgcolor='white')
#         return decomp_fig
    
#     # Profit vs Sales Scatter with Trendline
#     def profit_sales_scatter():
#         product_metrics = df.groupby('product_name').agg({
#             'sales': 'sum',
#             'profit': 'sum',
#             'category': 'first'
#         }).reset_index()
        
#         scatter_fig = px.scatter(product_metrics, x='sales', y='profit', 
#                                color='category', 
#                                hover_name='product_name',
#                                title='💰 Profit vs Sales Analysis',
#                                trendline='ols')
#         scatter_fig.update_layout(plot_bgcolor='white', paper_bgcolor='white')
#         return scatter_fig
    
#     return {
#         'correlation_heatmap': correlation_heatmap(),
#         'sales_decomposition': sales_decomposition(), 
#         'profit_sales_scatter': profit_sales_scatter()
#     }

# # 🎯 Performance Metrics Dashboard
# def create_kpi_dashboard():
#     """Create comprehensive KPI dashboard"""
    
#     current_year = df['year'].max()
#     previous_year = current_year - 1
    
#     current_year_data = df[df['year'] == current_year]
#     previous_year_data = df[df['year'] == previous_year]
    
#     kpis = {
#         'sales_growth': {
#             'current': current_year_data['sales'].sum(),
#             'previous': previous_year_data['sales'].sum(),
#             'icon': '📈'
#         },
#         'profit_growth': {
#             'current': current_year_data['profit'].sum(),
#             'previous': previous_year_data['profit'].sum(),
#             'icon': '💰'
#         },
#         'customer_growth': {
#             'current': current_year_data['customer_id'].nunique(),
#             'previous': previous_year_data['customer_id'].nunique(),
#             'icon': '👥'
#         },
#         'order_growth': {
#             'current': current_year_data['order_key'].nunique(),
#             'previous': previous_year_data['order_key'].nunique(),
#             'icon': '📦'
#         }
#     }
    
#     # Calculate growth percentages
#     for kpi in kpis:
#         if kpis[kpi]['previous'] > 0:
#             kpis[kpi]['growth'] = ((kpis[kpi]['current'] - kpis[kpi]['previous']) / kpis[kpi]['previous']) * 100
#         else:
#             kpis[kpi]['growth'] = 0
    
#     return kpis

# # 🎨 Custom CSS Animations
# def add_animations():
#     """Add CSS animations for enhanced UX"""
#     return """
#     .metric-card {
#         transition: transform 0.3s ease, box-shadow 0.3s ease;
#     }
    
#     .metric-card:hover {
#         transform: translateY(-5px);
#         box-shadow: 0 8px 25px rgba(0,0,0,0.15);
#     }
    
#     .nav-button {
#         transition: all 0.3s ease;
#     }
    
#     .nav-button:hover {
#         background-color: rgba(255,255,255,0.1);
#         transform: translateX(5px);
#     }
    
#     .chart-container {
#         animation: fadeIn 0.6s ease-in;
#     }
    
#     @keyframes fadeIn {
#         from { opacity: 0; transform: translateY(20px); }
#         to { opacity: 1; transform: translateY(0); }
#     }
    
#     .loading-spinner {
#         border: 4px solid #f3f3f3;
#         border-top: 4px solid #667eea;
#         border-radius: 50%;
#         width: 40px;
#         height: 40px;
#         animation: spin 1s linear infinite;
#         margin: 20px auto;
#     }
    
#     @keyframes spin {
#         0% { transform: rotate(0deg); }
#         100% { transform: rotate(360deg); }
#     }
#     """

# print("🎉 Dashboard siap dijalankan!")
# print("💡 Untuk menjalankan dashboard, ketik: python dashboard.py")
# print("🌐 Dashboard akan tersedia di: http://localhost:8050")
# print("\n📋 Fitur Dashboard:")
# print("   ✅ 4 Halaman utama dengan navigasi sidebar")
# print("   ✅ Visualisasi interaktif dengan Plotly")
# print("   ✅ Peta geografis untuk analisis wilayah")  
# print("   ✅ Tabel data yang dapat disortir")
# print("   ✅ Desain responsive dan profesional")
# print("   ✅ Tema terang dengan gradient yang menarik")
# print("   ✅ Analisis mendalam untuk setiap aspek bisnis")
# print("\n🚀 Selamat menganalisis data Superstore Anda!")