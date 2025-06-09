import pandas as pd
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px
from src.config.styles import custom_style, color_schemes
from src.data.data_loader import get_data

def create_overview_page():
    df, _, _, _, _, _, _ = get_data()
    if df.empty:
        print("Overview page: DataFrame is empty")
        return html.Div([
            html.H1("📊 Sales Overview Dashboard", style={'color': '#2c3e50', 'margin-bottom': '30px'}),
            html.P("⚠️ Tidak ada data tersedia. Periksa koneksi database atau file data_loader.py.", 
                   style={'color': '#e74c3c', 'text-align': 'center'})
        ])
    
    # Calculate key metrics
    total_sales = df['sales'].sum()
    total_profit = df['profit'].sum()
    total_orders = df['order_key'].nunique()
    avg_discount = df['discount'].mean() * 100
    
    print(f"Overview page - Total Sales: {total_sales}, Total Profit: {total_profit}, Total Orders: {total_orders}, Avg Discount: {avg_discount}")
    
    return html.Div([
        html.H1("🏠 Sales Overview Dashboard", style={'color': '#2c3e50', 'margin-bottom': '30px'}),
        
        # Key Metrics Row
        html.Div([
            html.Div([
                html.H3(f"${total_sales:,.0f}", style={'margin': '0', 'font-size': '28px'}),
                html.P("Total Sales", style={'margin': '5px 0 0 0'})
            ], style={**custom_style['metric-card'], 'background': color_schemes['gradient_backgrounds'][0]}),
            
            html.Div([
                html.H3(f"${total_profit:,.0f}", style={'margin': '0', 'font-size': '28px'}),
                html.P("Total Profit", style={'margin': '5px 0 0 0'})
            ], style={**custom_style['metric-card'], 'background': color_schemes['gradient_backgrounds'][1]}),
            
            html.Div([
                html.H3(f"{total_orders:,}", style={'margin': '0', 'font-size': '28px'}),
                html.P("Total Orders", style={'margin': '5px 0 0 0'})
            ], style={**custom_style['metric-card'], 'background': color_schemes['gradient_backgrounds'][2]}),
            
            html.Div([
                html.H3(f"{avg_discount:.1f}%", style={'margin': '0', 'font-size': '28px'}),
                html.P("Avg Discount", style={'margin': '5px 0 0 0'})
            ], style={**custom_style['metric-card'], 'background': color_schemes['gradient_backgrounds'][3]}),
        ], style={'display': 'grid', 'grid-template-columns': 'repeat(4, 1fr)', 'gap': '20px', 'margin-bottom': '30px'}),
        
        # Charts Row 1
        html.Div([
            html.Div([
                dcc.Graph(id="sales-trend-chart")
            ], style={**custom_style['card'], 'width': '60%'}),
            
            html.Div([
                dcc.Graph(id="category-pie-chart")
            ], style={**custom_style['card'], 'width': '38%'}),
        ], style={'display': 'flex', 'gap': '20px', 'margin-bottom': '20px'}),
        
        # Charts Row 2
        html.Div([
            html.Div([
                dcc.Graph(id="top-products-chart")
            ], style={**custom_style['card'], 'width': '50%'}),
            
            html.Div([
                dcc.Graph(id="segment-performance-chart")
            ], style={**custom_style['card'], 'width': '50%'}),
        ], style={'display': 'flex', 'gap': '20px'}),
    ])

def register_callbacks(app):
    @app.callback(
        [Output('sales-trend-chart', 'figure'),
         Output('category-pie-chart', 'figure'),
         Output('top-products-chart', 'figure'),
         Output('segment-performance-chart', 'figure')],
        [Input('current-page', 'data')]
    )
    def update_overview_charts(current_page):
        df, _, _, _, _, _, _ = get_data()
        print(f"Overview callback - current_page: {current_page}, df rows: {len(df)}")
        
        if current_page != 'overview':
            return {}, {}, {}, {}
        
        # Sales Trend
        monthly_sales = df.groupby(['year', 'month'])['sales'].sum().reset_index()
        monthly_sales['date'] = pd.to_datetime(monthly_sales[['year', 'month']].assign(day=1))
        
        sales_trend = px.line(monthly_sales, x='date', y='sales', 
                             title='📈 Monthly Sales Trend',
                             color_discrete_sequence=['#667eea'])
        sales_trend.update_layout(plot_bgcolor='white', paper_bgcolor='white')
        sales_trend.update_traces(line=dict(width=3))
        
        # Category Pie
        category_sales = df.groupby('category')['sales'].sum().reset_index()
        category_pie = px.pie(category_sales, values='sales', names='category',
                             title='🏷️ Sales by Category',
                             color_discrete_sequence=px.colors.qualitative.Set3)
        category_pie.update_layout(plot_bgcolor='white', paper_bgcolor='white')
        
        # Top Products
        top_products = df.groupby('product_name')['sales'].sum().nlargest(10).reset_index()
        top_products_chart = px.bar(top_products, x='sales', y='product_name',
                                   title='🏆 Top 10 Products by Sales',
                                   orientation='h',
                                   color='sales',
                                   color_continuous_scale='Viridis')
        top_products_chart.update_layout(plot_bgcolor='white', paper_bgcolor='white', height=400)
        
        # Segment Performance
        segment_metrics = df.groupby('segment').agg({
            'sales': 'sum',
            'profit': 'sum',
            'quantity': 'sum'
        }).reset_index()
        
        segment_chart = px.bar(segment_metrics, x='segment', y=['sales', 'profit'],
                              title='💼 Performance by Customer Segment',
                              barmode='group',
                              color_discrete_sequence=['#667eea', '#f5576c'])
        segment_chart.update_layout(plot_bgcolor='white', paper_bgcolor='white')
        
        return sales_trend, category_pie, top_products_chart, segment_chart