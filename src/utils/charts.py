import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from src.data.data_loader import df

def create_advanced_charts():
    """Create more sophisticated chart visualizations"""
    
    def correlation_heatmap():
        corr_data = df[['sales', 'profit', 'discount', 'quantity', 'shipping_cost']].corr()
        
        heatmap = px.imshow(corr_data, 
                           title='🔥 Correlation Heatmap',
                           color_continuous_scale='RdBu',
                           aspect='auto')
        heatmap.update_layout(plot_bgcolor='white', paper_bgcolor='white')
        return heatmap
    
    def sales_decomposition():
        monthly_sales = df.groupby(['year', 'month'])['sales'].sum().reset_index()
        monthly_sales['date'] = pd.to_datetime(monthly_sales[['year', 'month']].assign(day=1))
        monthly_sales = monthly_sales.set_index('date').sort_index()
        
        monthly_sales['trend'] = monthly_sales['sales'].rolling(window=3, center=True).mean()
        
        decomp_fig = make_subplots(rows=2, cols=1, 
                                  subplot_titles=['Original Sales', 'Trend'],
                                  vertical_spacing=0.1)
        
        decomp_fig.add_trace(go.Scatter(x=monthly_sales.index, y=monthly_sales['sales'],
                                       name='Original', line=dict(color='#667eea')), row=1, col=1)
        decomp_fig.add_trace(go.Scatter(x=monthly_sales.index, y=monthly_sales['trend'],
                                       name='Trend', line=dict(color='#f5576c')), row=2, col=1)
        
        decomp_fig.update_layout(title='📈 Sales Time Series Analysis',
                               plot_bgcolor='white', paper_bgcolor='white')
        return decomp_fig
    
    def profit_sales_scatter():
        product_metrics = df.groupby('product_name').agg({
            'sales': 'sum',
            'profit': 'sum',
            'category': 'first'
        }).reset_index()
        
        scatter_fig = px.scatter(product_metrics, x='sales', y='profit', 
                               color='category', 
                               hover_name='product_name',
                               title='💰 Profit vs Sales Analysis',
                               trendline='ols')
        scatter_fig.update_layout(plot_bgcolor='white', paper_bgcolor='white')
        return scatter_fig
    
    return {
        'correlation_heatmap': correlation_heatmap(),
        'sales_decomposition': sales_decomposition(), 
        'profit_sales_scatter': profit_sales_scatter()
    }