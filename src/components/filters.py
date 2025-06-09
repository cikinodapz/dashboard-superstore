from dash import dcc
from src.data.data_loader import df

def create_date_filter():
    """Create date range filter component"""
    return dcc.DatePickerRange(
        id='date-picker-range',
        start_date=df['order_date'].min(),
        end_date=df['order_date'].max(),
        display_format='YYYY-MM-DD',
        style={'margin': '10px'}
    )

def create_category_filter():
    """Create category filter dropdown"""
    return dcc.Dropdown(
        id='category-filter',
        options=[{'label': cat, 'value': cat} for cat in df['category'].unique()],
        value=df['category'].unique().tolist(),
        multi=True,
        placeholder="Select Categories",
        style={'margin': '10px'}
    )