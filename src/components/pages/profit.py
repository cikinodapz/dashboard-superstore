import pandas as pd
from dash import html, dcc, dash_table
from dash.dependencies import Input, Output
import plotly.express as px
from src.config.styles import custom_style
from src.data.data_loader import get_data

def create_profit_page():
    df, _, _, _, _, _, _ = get_data()
    if df.empty:
        print("Profit page: DataFrame is empty")
        return html.Div([
            html.H1("💰 Discount & Profit Analysis", style={'color': '#2c3e50', 'margin-bottom': '30px'}),
            html.P("⚠️ Tidak ada data tersedia. Periksa koneksi database atau file data_loader.py.", 
                   style={'color': '#e74c3c', 'text-align': 'center'})
        ])
    
    return html.Div([
        html.H1("💰 Discount & Profit Analysis", style={'color': '#2c3e50', 'margin-bottom': '30px'}),
        
        # Profit Metrics
        html.Div([
            html.Div([
                dcc.Graph(id="profit-margin-chart")
            ], style={**custom_style['card'], 'width': '50%'}),
            
            html.Div([
                dcc.Graph(id="discount-impact-chart")
            ], style={**custom_style['card'], 'width': '50%'}),
        ], style={'display': 'flex', 'gap': '20px', 'margin-bottom': '20px'}),
        
        # Detailed Analysis
        html.Div([
            html.Div([
                dcc.Graph(id="category-profitability")
            ], style={**custom_style['card'], 'width': '60%'}),
            
            html.Div([
                dcc.Graph(id="discount-distribution")
            ], style={**custom_style['card'], 'width': '40%'}),
        ], style={'display': 'flex', 'gap': '20px', 'margin-bottom': '20px'}),
        
        # Loss Analysis
        html.Div([
            html.H3("⚠️ Products with Losses", style={'color': '#e74c3c', 'margin-bottom': '20px'}),
            html.Div(id="loss-products-table")
        ], style=custom_style['card']),
    ])

def register_callbacks(app):
    @app.callback(
        [Output('profit-margin-chart', 'figure'),
         Output('discount-impact-chart', 'figure'),
         Output('category-profitability', 'figure'),
         Output('discount-distribution', 'figure'),
         Output('loss-products-table', 'children')],
        [Input('current-page', 'data')]
    )
    def update_profit_charts(current_page):
        df, _, _, _, _, _, _ = get_data()
        print(f"Profit callback - current_page: {current_page}, df rows: {len(df)}")
        
        if current_page != 'profit':
            return {}, {}, {}, {}, []
        
        # Profit Margin by Category
        category_profit = df.groupby('category').agg({
            'sales': 'sum',
            'profit': 'sum'
        }).reset_index()
        category_profit['profit_margin'] = (category_profit['profit'] / category_profit['sales'] * 100).round(2)
        
        margin_chart = px.bar(category_profit, x='category', y='profit_margin',
                             title='📊 Profit Margin by Category (%)',
                             color='profit_margin',
                             color_continuous_scale='RdYlGn')
        margin_chart.update_layout(plot_bgcolor='white', paper_bgcolor='white')
        
        # Discount Impact
        df['discount_range'] = pd.cut(df['discount'], bins=[0, 0.1, 0.2, 0.3, 1.0], 
                                     labels=['0-10%', '10-20%', '20-30%', '30%+'])
        discount_impact = df.groupby('discount_range').agg({
            'sales': 'sum',
            'profit': 'sum'
        }).reset_index()
        
        impact_chart = px.bar(discount_impact, x='discount_range', y=['sales', 'profit'],
                             title='💸 Discount Impact on Sales & Profit',
                             barmode='group',
                             color_discrete_sequence=['#667eea', '#f5576c'])
        impact_chart.update_layout(plot_bgcolor='white', paper_bgcolor='white')
        
        # Category Profitability
        groupby_columns = ['category']
        if 'sub_category' in df.columns:
            groupby_columns.append('sub_category')
        
        cat_profit_detail = df.groupby(groupby_columns).agg({
            'profit': 'sum',
            'sales': 'sum'
        }).reset_index()
        
        hover_data = {}
        if 'sub_category' in df.columns:
            hover_data['sub_category'] = True
        
        profitability_chart = px.scatter(cat_profit_detail, x='sales', y='profit',
                                       color='category', size='profit',
                                       hover_data=hover_data,
                                       title='💎 Category Profitability Matrix')
        profitability_chart.update_layout(plot_bgcolor='white', paper_bgcolor='white')
        
        # Discount Distribution
        discount_dist = px.histogram(df, x='discount', nbins=20,
                                   title='📈 Discount Distribution',
                                   color_discrete_sequence=['#f5576c'])
        discount_dist.update_layout(plot_bgcolor='white', paper_bgcolor='white')
        
        # Loss Products Table
        loss_products = df.groupby('product_name')['profit'].sum().reset_index()
        loss_products = loss_products[loss_products['profit'] < 0].nsmallest(10, 'profit')
        loss_products.columns = ['Product', 'Loss ($)']
        loss_products['Loss ($)'] = loss_products['Loss ($)'].round(2)
        
        if not loss_products.empty:
            loss_table = dash_table.DataTable(
                data=loss_products.to_dict('records'),
                columns=[{"name": i, "id": i, "type": "numeric", "format": {"specifier": ",.2f"}} if 'Loss' in i else {"name": i, "id": i} for i in loss_products.columns],
                style_cell={'textAlign': 'left', 'padding': '10px'},
                style_header={'backgroundColor': '#e74c3c', 'color': 'white', 'fontWeight': 'bold'},
                style_data={'backgroundColor': '#fdf2f2'},
            )
        else:
            loss_table = html.P("🎉 No products with losses found!", style={'text-align': 'center', 'color': '#27ae60'})
        
        return margin_chart, impact_chart, profitability_chart, discount_dist, loss_table