import pandas as pd
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
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
    
    # Professional animation style for metric updates
    animation_style = {
        'animation': 'pulseGlow 0.6s cubic-bezier(0.4, 0, 0.2, 1)',
        '@keyframes pulseGlow': {
            '0%': {
                'opacity': 0.7,
                'transform': 'scale(0.95)',
                'box-shadow': '0 0 0 rgba(0, 0, 0, 0.2)'
            },
            '50%': {
                'opacity': 1,
                'transform': 'scale(1.05)',
                'box-shadow': '0 0 15px rgba(102, 126, 234, 0.5)'  # Glow effect with color #667eea
            },
            '100%': {
                'opacity': 1,
                'transform': 'scale(1)',
                'box-shadow': '0 0 5px rgba(0, 0, 0, 0.1)'
            }
        }
    }

    return html.Div([
        html.H1("🏠 Sales Overview Dashboard", style={'color': '#2c3e50', 'margin-bottom': '30px'}),
        
        # Filter Status Display
        html.Div(id="filter-status", 
                style={
                    'background': '#e8f4fd',
                    'border-left': '4px solid #667eea',
                    'padding': '15px',
                    'margin-bottom': '20px',
                    'border-radius': '5px',
                    'display': 'none'  # Hidden by default
                }),
        
        # Reset Button
        html.Div([
            html.Button("🔄 Reset Filters", 
                       id="reset-filters-btn", 
                       n_clicks=0,
                       style={
                           'background': '#f5576c',
                           'color': 'white',
                           'border': 'none',
                           'padding': '10px 20px',
                           'border-radius': '5px',
                           'cursor': 'pointer',
                           'font-weight': 'bold',
                           'margin-bottom': '20px',
                           'transition': 'all 0.3s ease'
                       })
        ]),
        
        # Key Metrics Row with Dynamic IDs and Animation
        html.Div([
            html.Div([
                html.H3(id="total-sales-metric", style={**{'margin': '0', 'font-size': '28px'}, **animation_style}),
                html.P("Total Sales", style={'margin': '5px 0 0 0'})
            ], style={**custom_style['metric-card'], 'background': color_schemes['gradient_backgrounds'][0]}),
            
            html.Div([
                html.H3(id="total-profit-metric", style={**{'margin': '0', 'font-size': '28px'}, **animation_style}),
                html.P("Total Profit", style={'margin': '5px 0 0 0'})
            ], style={**custom_style['metric-card'], 'background': color_schemes['gradient_backgrounds'][1]}),
            
            html.Div([
                html.H3(id="total-orders-metric", style={**{'margin': '0', 'font-size': '28px'}, **animation_style}),
                html.P("Total Orders", style={'margin': '5px 0 0 0'})
            ], style={**custom_style['metric-card'], 'background': color_schemes['gradient_backgrounds'][2]}),
            
            html.Div([
                html.H3(id="avg-discount-metric", style={**{'margin': '0', 'font-size': '28px'}, **animation_style}),
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
        
        # Hidden div to store current filter state
        html.Div(id='current-filter-state', style={'display': 'none'}),
    ])

def register_callbacks(app):
    @app.callback(
        [Output('sales-trend-chart', 'figure'),
         Output('category-pie-chart', 'figure'),
         Output('top-products-chart', 'figure'),
         Output('segment-performance-chart', 'figure'),
         Output('filter-status', 'children'),
         Output('filter-status', 'style')],
        [Input('current-page', 'data'),
         Input('current-filter-state', 'children')]
    )
    def update_overview_charts(current_page, filter_state):
        df, _, _, _, _, _, _ = get_data()
        print(f"Overview callback - current_page: {current_page}, df rows: {len(df)}")
        
        if current_page != 'overview':
            return {}, {}, {}, {}, "", {'display': 'none'}
        
        # Parse filter state
        filtered_df = df.copy()
        filter_info = ""
        filter_display_style = {'display': 'none'}
        
        if filter_state and filter_state.strip():
            filter_parts = filter_state.split('|')
            filter_type = filter_parts[0]
            
            if filter_type == 'sales_trend' and len(filter_parts) >= 3:
                year = int(filter_parts[1])
                month = int(filter_parts[2])
                filtered_df = filtered_df[
                    (filtered_df['year'] == year) &
                    (filtered_df['month'] == month)
                ]
                month_name = pd.to_datetime(f"{year}-{month:02d}-01").strftime("%B %Y")
                filter_info = f"📅 Filtered by: {month_name}"
            
            elif filter_type == 'category' and len(filter_parts) >= 2:
                category = filter_parts[1]
                filtered_df = filtered_df[filtered_df['category'] == category]
                filter_info = f"🏷️ Filtered by Category: {category}"
            
            elif filter_type == 'product' and len(filter_parts) >= 2:
                product = filter_parts[1]
                filtered_df = filtered_df[filtered_df['product_name'] == product]
                filter_info = f"🏆 Filtered by Product: {product}"
            
            elif filter_type == 'segment' and len(filter_parts) >= 2:
                segment = filter_parts[1]
                filtered_df = filtered_df[filtered_df['segment'] == segment]
                filter_info = f"💼 Filtered by Segment: {segment}"
            
            filter_display_style = {
                'background': '#e8f4fd',
                'border-left': '4px solid #667eea',
                'padding': '15px',
                'margin-bottom': '20px',
                'border-radius': '5px',
                'display': 'block'
            }
        
        # Sales Trend Chart
        monthly_sales = filtered_df.groupby(['year', 'month'])['sales'].sum().reset_index()
        monthly_sales['date'] = pd.to_datetime(monthly_sales[['year', 'month']].assign(day=1))
        
        # Create sales trend with highlighting
        sales_trend = px.line(monthly_sales, x='date', y='sales', 
                             title='📈 Monthly Sales Trend',
                             color_discrete_sequence=['#667eea'])
        
        # Highlight selected point if filtered by sales trend
        if filter_state and filter_state.startswith('sales_trend'):
            filter_parts = filter_state.split('|')
            if len(filter_parts) >= 3:
                selected_year = int(filter_parts[1])
                selected_month = int(filter_parts[2])
                selected_date = pd.to_datetime(f"{selected_year}-{selected_month:02d}-01")
                
                # Add highlighted point
                selected_sales = monthly_sales[monthly_sales['date'] == selected_date]['sales'].iloc[0] if len(monthly_sales[monthly_sales['date'] == selected_date]) > 0 else 0
                sales_trend.add_trace(go.Scatter(
                    x=[selected_date],
                    y=[selected_sales],
                    mode='markers',
                    marker=dict(size=15, color='#f5576c', symbol='circle', line=dict(width=3, color='white')),
                    name='Selected Point',
                    showlegend=False
                ))
        
        sales_trend.update_layout(plot_bgcolor='white', paper_bgcolor='white')
        sales_trend.update_traces(line=dict(width=3))
        
        # Category Pie Chart
        category_sales = filtered_df.groupby('category')['sales'].sum().reset_index()
        
        # Create color mapping for highlighting
        colors = px.colors.qualitative.Set3
        if filter_state and filter_state.startswith('category'):
            selected_category = filter_state.split('|')[1]
            pie_colors = []
            for cat in category_sales['category']:
                if cat == selected_category:
                    pie_colors.append('#f5576c')  # Highlight color
                else:
                    pie_colors.append('#d3d3d3')  # Muted color
        else:
            pie_colors = colors
        
        category_pie = px.pie(category_sales, values='sales', names='category',
                             title='🏷️ Sales by Category',
                             color_discrete_sequence=pie_colors)
        category_pie.update_layout(plot_bgcolor='white', paper_bgcolor='white')
        
        # Top Products Chart
        top_products = filtered_df.groupby('product_name')['sales'].sum().nlargest(10).reset_index()
        
        # Create color mapping for highlighting
        if filter_state and filter_state.startswith('product'):
            selected_product = filter_state.split('|')[1]
            bar_colors = ['#f5576c' if prod == selected_product else '#667eea' for prod in top_products['product_name']]
        else:
            bar_colors = '#667eea'
        
        top_products_chart = px.bar(top_products, x='sales', y='product_name',
                                   title='🏆 Top 10 Products by Sales',
                                   orientation='h',
                                   color_discrete_sequence=[bar_colors] if isinstance(bar_colors, str) else None)
        
        if isinstance(bar_colors, list):
            top_products_chart.update_traces(marker_color=bar_colors)
        
        top_products_chart.update_layout(plot_bgcolor='white', paper_bgcolor='white', height=400)
        
        # Segment Performance Chart
        segment_metrics = filtered_df.groupby('segment').agg({
            'sales': 'sum',
            'profit': 'sum',
            'quantity': 'sum'
        }).reset_index()
        
        # Create segment chart with highlighting
        if filter_state and filter_state.startswith('segment'):
            selected_segment = filter_state.split('|')[1]
            # Create separate traces for highlighted and normal segments
            segment_chart = go.Figure()
            
            for i, segment in enumerate(segment_metrics['segment']):
                color_sales = '#f5576c' if segment == selected_segment else '#667eea'
                color_profit = '#ff6b8a' if segment == selected_segment else '#7e8ef0'
                
                segment_chart.add_trace(go.Bar(
                    name='Sales' if i == 0 else None,
                    x=[segment],
                    y=[segment_metrics[segment_metrics['segment'] == segment]['sales'].iloc[0]],
                    marker_color=color_sales,
                    legendgroup='sales',
                    showlegend=(i == 0)
                ))
                
                segment_chart.add_trace(go.Bar(
                    name='Profit' if i == 0 else None,
                    x=[segment],
                    y=[segment_metrics[segment_metrics['segment'] == segment]['profit'].iloc[0]],
                    marker_color=color_profit,
                    legendgroup='profit',
                    showlegend=(i == 0)
                ))
        else:
            segment_chart = px.bar(segment_metrics, x='segment', y=['sales', 'profit'],
                                  title='💼 Performance by Customer Segment',
                                  barmode='group',
                                  color_discrete_sequence=['#667eea', '#f5576c'])
        
        segment_chart.update_layout(
            title='💼 Performance by Customer Segment',
            plot_bgcolor='white', 
            paper_bgcolor='white',
            barmode='group'
        )
        
        return sales_trend, category_pie, top_products_chart, segment_chart, filter_info, filter_display_style

    @app.callback(
        Output('current-filter-state', 'children'),
        [Input('sales-trend-chart', 'clickData'),
         Input('category-pie-chart', 'clickData'),
         Input('top-products-chart', 'clickData'),
         Input('segment-performance-chart', 'clickData'),
         Input('reset-filters-btn', 'n_clicks')]
    )
    def update_filter_state(sales_click, category_click, product_click, segment_click, reset_clicks):
        """Update the current filter state based on chart clicks"""
        from dash import callback_context
        
        if not callback_context.triggered:
            return ""
        
        trigger_id = callback_context.triggered[0]['prop_id'].split('.')[0]
        
        # Reset button clicked
        if trigger_id == 'reset-filters-btn' and reset_clicks > 0:
            return ""
        
        # Determine which chart was clicked and extract filter info
        if trigger_id == 'sales-trend-chart' and sales_click and sales_click['points']:
            clicked_date = sales_click['points'][0]['x']
            clicked_date = pd.to_datetime(clicked_date)
            return f"sales_trend|{clicked_date.year}|{clicked_date.month}"
        
        elif trigger_id == 'category-pie-chart' and category_click and category_click['points']:
            clicked_category = category_click['points'][0]['label']
            return f"category|{clicked_category}"
        
        elif trigger_id == 'top-products-chart' and product_click and product_click['points']:
            clicked_product = product_click['points'][0]['y']
            return f"product|{clicked_product}"
        
        elif trigger_id == 'segment-performance-chart' and segment_click and segment_click['points']:
            clicked_segment = segment_click['points'][0]['x']
            return f"segment|{clicked_segment}"
        
        return ""

    @app.callback(
        [Output('total-sales-metric', 'children'),
         Output('total-profit-metric', 'children'),
         Output('total-orders-metric', 'children'),
         Output('avg-discount-metric', 'children')],
        [Input('current-filter-state', 'children')]
    )
    def update_metrics(filter_state):
        """Update metrics based on current filter state"""
        df, _, _, _, _, _, _ = get_data()
        filtered_df = df.copy()  # Start with full DataFrame
        
        # Apply filter based on current state
        if filter_state and filter_state.strip():
            filter_parts = filter_state.split('|')
            filter_type = filter_parts[0]
            
            if filter_type == 'sales_trend' and len(filter_parts) >= 3:
                year = int(filter_parts[1])
                month = int(filter_parts[2])
                filtered_df = filtered_df[
                    (filtered_df['year'] == year) &
                    (filtered_df['month'] == month)
                ]
            
            elif filter_type == 'category' and len(filter_parts) >= 2:
                category = filter_parts[1]
                filtered_df = filtered_df[filtered_df['category'] == category]
            
            elif filter_type == 'product' and len(filter_parts) >= 2:
                product = filter_parts[1]
                filtered_df = filtered_df[filtered_df['product_name'] == product]
            
            elif filter_type == 'segment' and len(filter_parts) >= 2:
                segment = filter_parts[1]
                filtered_df = filtered_df[filtered_df['segment'] == segment]
        
        # Calculate metrics for filtered DataFrame
        if not filtered_df.empty:
            total_sales = filtered_df['sales'].sum()
            total_profit = filtered_df['profit'].sum()
            total_orders = filtered_df['order_key'].nunique()
            avg_discount = filtered_df['discount'].mean() * 100
        else:
            total_sales = total_profit = total_orders = avg_discount = 0
        
        return (
            f"${total_sales:,.0f}",
            f"${total_profit:,.0f}",
            f"{total_orders:,}",
            f"{avg_discount:.1f}%"
        )