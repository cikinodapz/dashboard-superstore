import pandas as pd
from src.config.database import get_db_connection

# Global variables
_df = None
_dim_customer = None
_dim_product = None
_dim_order = None
_dim_time = None
_dim_region = None
_fact_sales = None

def load_data():
    global _df, _dim_customer, _dim_product, _dim_order, _dim_time, _dim_region, _fact_sales
    if _df is None:  # Load only if not already loaded
        engine = get_db_connection()
        try:
            _dim_customer = pd.read_sql("SELECT * FROM dim_customer", engine)
            _dim_product = pd.read_sql("SELECT * FROM dim_product", engine)
            _dim_order = pd.read_sql("SELECT * FROM dim_order", engine)
            _dim_time = pd.read_sql("SELECT * FROM dim_time", engine)
            _dim_region = pd.read_sql("SELECT * FROM dim_region", engine)
            _fact_sales = pd.read_sql("SELECT * FROM fact_sales", engine)
            
            print(f"dim_customer: {len(_dim_customer)} rows")
            print(f"dim_product: {len(_dim_product)} rows")
            print(f"dim_order: {len(_dim_order)} rows")
            print(f"dim_time: {len(_dim_time)} rows")
            print(f"dim_region: {len(_dim_region)} rows")
            print(f"fact_sales: {len(_fact_sales)} rows")
            
            _df = (_fact_sales
                   .merge(_dim_customer, on='customer_key', how='left')
                   .merge(_dim_product, on='product_key', how='left')
                   .merge(_dim_order, on='order_key', how='left')
                   .merge(_dim_time, on='time_key', how='left')
                   .merge(_dim_region, on='region_key', how='left'))
            
            print(f"Merged df: {len(_df)} rows")
            print("Columns in df:", _df.columns.tolist())
            
            if 'order_date' in _df.columns:
                _df['order_date'] = pd.to_datetime(_df['order_date'])
        except Exception as e:
            print(f"Error loading data: {str(e)}")
            _df = pd.DataFrame()
            _dim_customer = pd.DataFrame()
            _dim_product = pd.DataFrame()
            _dim_order = pd.DataFrame()
            _dim_time = pd.DataFrame()
            _dim_region = pd.DataFrame()
            _fact_sales = pd.DataFrame()
    
    return _df, _dim_customer, _dim_product, _dim_order, _dim_time, _dim_region, _fact_sales

def get_data():
    """Getter function to access loaded data"""
    if _df is None:
        load_data()
    return _df, _dim_customer, _dim_product, _dim_order, _dim_time, _dim_region, _fact_sales