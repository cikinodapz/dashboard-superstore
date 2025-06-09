import pandas as pd
from itertools import combinations

def calculate_customer_lifetime_value(df):
    """Calculate Customer Lifetime Value"""
    customer_metrics = df.groupby('customer_name').agg({
        'sales': 'sum',
        'profit': 'sum',
        'order_key': 'nunique',
        'order_date': ['min', 'max']
    }).reset_index()
    
    customer_metrics.columns = ['customer_name', 'total_sales', 'total_profit', 
                               'total_orders', 'first_order', 'last_order']
    
    # Calculate customer lifespan in days
    customer_metrics['lifespan_days'] = (
        pd.to_datetime(customer_metrics['last_order']) - 
        pd.to_datetime(customer_metrics['first_order'])
    ).dt.days + 1
    
    # Calculate CLV metrics
    customer_metrics['avg_order_value'] = customer_metrics['total_sales'] / customer_metrics['total_orders']
    customer_metrics['purchase_frequency'] = customer_metrics['total_orders'] / (customer_metrics['lifespan_days'] / 365)
    customer_metrics['clv'] = customer_metrics['avg_order_value'] * customer_metrics['purchase_frequency'] * 2  # Assuming 2-year projection
    
    return customer_metrics

def seasonal_analysis(df):
    """Analyze seasonal trends"""
    df['season'] = df['month'].map({
        12: 'Winter', 1: 'Winter', 2: 'Winter',
        3: 'Spring', 4: 'Spring', 5: 'Spring',
        6: 'Summer', 7: 'Summer', 8: 'Summer',
        9: 'Fall', 10: 'Fall', 11: 'Fall'
    })
    
    seasonal_data = df.groupby(['season', 'category']).agg({
        'sales': 'sum',
        'profit': 'sum',
        'quantity': 'sum'
    }).reset_index()
    
    return seasonal_data

def market_basket_analysis(df):
    """Simple market basket analysis"""
    order_products = df.groupby('order_id')['product_name'].apply(list).reset_index()
    
    product_pairs = []
    for products in order_products['product_name']:
        if len(products) > 1:
            for pair in combinations(products, 2):
                product_pairs.append(sorted(pair))
    
    pair_counts = pd.Series(product_pairs).value_counts().head(20)
    return pair_counts

def export_dashboard_data(df):
    """Export processed data for external use"""
    export_data = {
        'sales_summary': df.groupby(['year', 'month', 'category']).agg({
            'sales': 'sum',
            'profit': 'sum',
            'quantity': 'sum'
        }).reset_index(),
        
        'customer_summary': df.groupby(['customer_name', 'segment']).agg({
            'sales': 'sum',
            'profit': 'sum',
            'order_key': 'nunique'
        }).reset_index(),
        
        'product_performance': df.groupby(['product_name', 'category', 'sub_category']).agg({
            'sales': 'sum',
            'profit': 'sum',
            'quantity': 'sum'
        }).reset_index(),
        
        'regional_analysis': df.groupby(['region', 'state', 'city']).agg({
            'sales': 'sum',
            'profit': 'sum',
            'order_key': 'nunique'
        }).reset_index()
    }
    
    return export_data

def create_kpi_dashboard(df):
    """Create comprehensive KPI dashboard"""
    current_year = df['year'].max()
    previous_year = current_year - 1
    
    current_year_data = df[df['year'] == current_year]
    previous_year_data = df[df['year'] == previous_year]
    
    kpis = {
        'sales_growth': {
            'current': current_year_data['sales'].sum(),
            'previous': previous_year_data['sales'].sum(),
            'icon': '📈'
        },
        'profit_growth': {
            'current': current_year_data['profit'].sum(),
            'previous': previous_year_data['profit'].sum(),
            'icon': '💰'
        },
        'customer_growth': {
            'current': current_year_data['customer_id'].nunique(),
            'previous': previous_year_data['customer_id'].nunique(),
            'icon': '👥'
        },
        'order_growth': {
            'current': current_year_data['order_key'].nunique(),
            'previous': previous_year_data['order_key'].nunique(),
            'icon': '📦'
        }
    }
    
    for kpi in kpis:
        if kpis[kpi]['previous'] > 0:
            kpis[kpi]['growth'] = ((kpis[kpi]['current'] - kpis[kpi]['previous']) / kpis[kpi]['previous']) * 100
        else:
            kpis[kpi]['growth'] = 0
    
    return kpis