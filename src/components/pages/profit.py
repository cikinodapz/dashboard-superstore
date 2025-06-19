import dash
import pandas as pd
import numpy as np
from dash import html, dcc, dash_table
from dash.dependencies import Input, Output, State
import plotly.express as px
from src.config.styles import custom_style
from src.data.data_loader import get_data
import pickle
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define fallback values for dropdowns based on provided counts
FALLBACK_SHIP_MODES = ['Standard Class', 'Second Class', 'First Class', 'Same Day']
FALLBACK_CATEGORIES = ['Office Supplies', 'Technology', 'Furniture']
FALLBACK_SUBCATEGORIES = [
    'Binders', 'Storage', 'Art', 'Paper', 'Chairs', 'Phones', 'Furnishings',
    'Accessories', 'Fasteners', 'Labels', 'Bookcases', 'Supplies', 'Envelopes',
    'Copiers', 'Appliances', 'Machines', 'Tables'
]

# Load ML models and encoders
reg_model = clf_model = scaler = le_ship_mode = le_category = le_subcategory = selector_reg = selector_clf = None
try:
    with open('src/models/reg_model.pkl', 'rb') as f:
        reg_model = pickle.load(f)
    with open('src/models/clf_model.pkl', 'rb') as f:
        clf_model = pickle.load(f)
    with open('src/models/scaler.pkl', 'rb') as f:
        scaler = pickle.load(f)
    with open('src/models/le_ship_mode.pkl', 'rb') as f:
        le_ship_mode = pickle.load(f)
    with open('src/models/le_category.pkl', 'rb') as f:
        le_category = pickle.load(f)
    with open('src/models/le_subcategory.pkl', 'rb') as f:
        le_subcategory = pickle.load(f)
    with open('src/models/selector_reg.pkl', 'rb') as f:
        selector_reg = pickle.load(f)
    with open('src/models/selector_clf.pkl', 'rb') as f:
        selector_clf = pickle.load(f)
    logger.info("All models and encoders loaded successfully.")
except FileNotFoundError as e:
    logger.error(f"Error loading model or encoder: {e}")
except Exception as e:
    logger.error(f"Unexpected error loading models: {e}")

def predict_profit_and_loss(quantity, discount, shipping_cost, ship_mode, category, sub_category):
    if any(v is None for v in [reg_model, clf_model, scaler, le_ship_mode, le_category, le_subcategory, selector_reg, selector_clf]):
        return {'error': 'Model or encoder not loaded. Check the models directory and logs.'}
    
    try:
        # Prepare input data
        input_data = pd.DataFrame({
            'Quantity': [quantity],
            'Discount': [discount],
            'Shipping Cost': [shipping_cost],
            'Ship Mode': [le_ship_mode.transform([ship_mode])[0]],
            'Category': [le_category.transform([category])[0]],
            'Sub-Category': [le_subcategory.transform([sub_category])[0]],
            'Quantity_Discount': [quantity * discount],
            'Shipping_Discount': [shipping_cost * discount]
        })
        
        # Scale numerical features
        numerical_features = ['Quantity', 'Discount', 'Shipping Cost', 'Quantity_Discount', 'Shipping_Discount']
        input_data[numerical_features] = scaler.transform(input_data[numerical_features])
        
        # Apply feature selection
        input_data_reg = selector_reg.transform(input_data)
        input_data_clf = selector_clf.transform(input_data)
        
        # Make predictions
        profit_pred = reg_model.predict(input_data_reg)[0]
        loss_prob = clf_model.predict_proba(input_data_clf)[0][1]
        status = "Berpotensi Rugi" if profit_pred < 0 or loss_prob > 0.5 else "Aman"
        
        return {
            'Predicted Profit': profit_pred,
            'Loss Probability': loss_prob,
            'Status': status
        }
    except ValueError as e:
        logger.error(f"ValueError in prediction: {e}")
        return {'error': f"Invalid input: {str(e)}. Ensure all inputs match expected values."}
    except Exception as e:
        logger.error(f"Unexpected error in prediction: {e}")
        return {'error': f"Prediction failed: {str(e)}"}

def create_profit_page():
    df, _, _, _, _, _, _ = get_data()
    if df.empty:
        logger.warning("Profit page: DataFrame is empty")
        return html.Div([
            html.H1("💰 Discount & Profit Analysis", style={'color': '#2c3e50', 'margin-bottom': '30px'}),
            html.P("⚠️ Tidak ada data tersedia. Periksa koneksi database atau file data_loader.py.", 
                   style={'color': '#e74c3c', 'text-align': 'left'})
        ])
    
    # Log DataFrame columns for debugging
    logger.info(f"DataFrame columns: {df.columns.tolist()}")
    
    # Dynamically detect column names
    category_col = next((col for col in df.columns if 'category' in col.lower()), 'Category')
    subcategory_col = next((col for col in df.columns if 'sub' in col.lower() and 'category' in col.lower()), 'Sub-Category')
    discount_col = next((col for col in df.columns if 'discount' in col.lower()), 'Discount')
    sales_col = next((col for col in df.columns if 'sales' in col.lower()), 'Sales')
    profit_col = next((col for col in df.columns if 'profit' in col.lower()), 'Profit')
    product_col = next((col for col in df.columns if 'product' in col.lower() and 'name' in col.lower()), 'Product Name')
    ship_mode_col = next((col for col in df.columns if 'ship' in col.lower() and 'mode' in col.lower()), 'Ship Mode')
    
    logger.info(f"Detected columns: Category={category_col}, Sub-Category={subcategory_col}, Discount={discount_col}, "
                f"Sales={sales_col}, Profit={profit_col}, Product Name={product_col}, Ship Mode={ship_mode_col}")
    
    # Get unique values for dropdowns from DataFrame or fallback
    ship_modes = df[ship_mode_col].unique().tolist() if ship_mode_col in df.columns else FALLBACK_SHIP_MODES
    categories = df[category_col].unique().tolist() if category_col in df.columns else FALLBACK_CATEGORIES
    subcategories = df[subcategory_col].unique().tolist() if subcategory_col in df.columns else FALLBACK_SUBCATEGORIES
    
    # Use encoder classes if available and valid
    if le_ship_mode and hasattr(le_ship_mode, 'classes_'):
        ship_modes = [sm for sm in le_ship_mode.classes_.tolist() if sm in FALLBACK_SHIP_MODES]
    if le_category and hasattr(le_category, 'classes_'):
        categories = [cat for cat in le_category.classes_.tolist() if cat in FALLBACK_CATEGORIES]
    if le_subcategory and hasattr(le_subcategory, 'classes_'):
        subcategories = [sub for sub in le_subcategory.classes_.tolist() if sub in FALLBACK_SUBCATEGORIES]
    
    # Ensure no empty lists
    ship_modes = ship_modes or FALLBACK_SHIP_MODES
    categories = categories or FALLBACK_CATEGORIES
    subcategories = subcategories or FALLBACK_SUBCATEGORIES
    
    logger.info(f"Dropdown values: Ship Modes={ship_modes}, Categories={categories}, Subcategories={subcategories}")

    return html.Div([
        html.H1("💰 Discount & Profit Analysis", style={
            'color': '#2c3e50', 
            'margin-bottom': '30px', 
            'font-size': '32px', 
            'font-weight': '600', 
            'text-align': 'left'
        }),
        
        # Filter Indicator
        html.Div(id="profit-filter-indicator", style={
            'color': '#2c3e50', 
            'font-size': '16px', 
            'margin-bottom': '20px', 
            'text-align': 'center',
            'background-color': '#f1f5f9', 
            'padding': '12px', 
            'border-radius': '8px', 
            'border': '1px solid #e2e8f0'
        }),
        
        html.Button("🔄 Reset", id="profit-reset-button", n_clicks=0, style={
            'background': 'linear-gradient(to right, #3b82f6, #1e40af)',
            'color': 'white',
            'padding': '12px 28px',
            'border': 'none',
            'border-radius': '8px',
            'cursor': 'pointer',
            'font-size': '16px',
            'font-weight': '500',
            'margin-bottom': '30px',
            'display': 'block',
            'margin-left': 'auto',
            'margin-right': 'auto',
            'box-shadow': '0 4px 6px rgba(0, 0, 0, 0.1)'
        }),
        
        # Hidden div to store filter state
        dcc.Store(id='profit-filter-state', data={
            'selected_category': None,
            'selected_discount_range': None,
            'selected_product': None
        }),
        
        # Profit Metrics
        html.Div([
            html.Div([
                dcc.Graph(id="profit-margin-chart")
            ], style={**custom_style['card'], 'width': '50%', 'padding': '10px'}),
            
            html.Div([
                dcc.Graph(id="discount-impact-chart")
            ], style={**custom_style['card'], 'width': '50%', 'padding': '10px'}),
        ], style={'display': 'flex', 'gap': '20px', 'margin-bottom': '30px'}),
        
        # Detailed Analysis
        html.Div([
            html.Div([
                dcc.Graph(id="category-profitability")
            ], style={**custom_style['card'], 'width': '60%', 'padding': '10px'}),
            
            html.Div([
                dcc.Graph(id="discount-distribution")
            ], style={**custom_style['card'], 'width': '40%', 'padding': '10px'}),
        ], style={'display': 'flex', 'gap': '20px', 'margin-bottom': '30px'}),
        
        # Loss Analysis
        html.Div([
            html.H3("⚠️ Products with Losses", style={
                'color': '#dc2626', 
                'margin-bottom': '20px', 
                'font-size': '24px', 
                'font-weight': '600'
            }),
            html.Div(id="loss-products-table")
        ], style={**custom_style['card'], 'margin-bottom': '30px', 'padding': '20px'}),
        
        # Profit Prediction Section (Moved to Bottom)
        html.Div([
            html.H3("🔮 Profit & Loss Predictor", style={
                'color': '#2c3e50', 
                'margin-bottom': '25px', 
                'font-size': '24px', 
                'font-weight': '600', 
                'text-align': 'center',
                'padding': '15px',
                'background': 'linear-gradient(to right, #f5f7fa, #c3cfe2)',
                'border-radius': '10px',
                'box-shadow': '0 4px 6px rgba(0, 0, 0, 0.1)'
            }),
            
            html.Div([
                # Input Card with improved styling
                html.Div([
                    html.Div([
                        html.H4("📝 Input Parameters", style={
                            'color': '#ffffff',
                            'margin-bottom': '20px',
                            'padding': '10px',
                            'background': 'linear-gradient(to right, #4f6b92, #3a516d)',
                            'border-radius': '8px',
                            'text-align': 'center'
                        }),
                        
                        # Input Fields Grid
                        html.Div([
                            # Quantity Input
                            html.Div([
                                html.Label("Quantity", style={
                                    'font-weight': '600', 
                                    'color': '#1e293b', 
                                    'margin-bottom': '8px', 
                                    'font-size': '14px',
                                    'display': 'block'
                                }),
                                dcc.Input(
                                    id='predict-quantity', 
                                    type='number', 
                                    value=5, 
                                    min=1,
                                    className='prediction-input',
                                    style={
                                        'width': '100%', 
                                        'padding': '12px', 
                                        'border': '2px solid #e2e8f0', 
                                        'border-radius': '8px', 
                                        'margin-bottom': '20px', 
                                        'font-size': '14px',
                                        'transition': 'all 0.3s'
                                    }
                                ),
                            ], style={'grid-column': '1'}),
                            
                            # Discount Input
                            html.Div([
                                html.Label("Discount (%)", style={
                                    'font-weight': '600', 
                                    'color': '#1e293b', 
                                    'margin-bottom': '8px', 
                                    'font-size': '14px',
                                    'display': 'block'
                                }),
                                dcc.Input(
                                    id='predict-discount', 
                                    type='number', 
                                    value=20, 
                                    min=0, 
                                    max=100, 
                                    step=1,
                                    className='prediction-input',
                                    style={
                                        'width': '100%', 
                                        'padding': '12px', 
                                        'border': '2px solid #e2e8f0', 
                                        'border-radius': '8px', 
                                        'margin-bottom': '20px', 
                                        'font-size': '14px',
                                        'transition': 'all 0.3s'
                                    }
                                ),
                            ], style={'grid-column': '2'}),
                            
                            # Shipping Cost Input
                            html.Div([
                                html.Label("Shipping Cost ($)", style={
                                    'font-weight': '600', 
                                    'color': '#1e293b', 
                                    'margin-bottom': '8px', 
                                    'font-size': '14px',
                                    'display': 'block'
                                }),
                                dcc.Input(
                                    id='predict-shipping-cost', 
                                    type='number', 
                                    value=10.0, 
                                    min=0, 
                                    step=0.1,
                                    className='prediction-input',
                                    style={
                                        'width': '100%', 
                                        'padding': '12px', 
                                        'border': '2px solid #e2e8f0', 
                                        'border-radius': '8px', 
                                        'margin-bottom': '20px', 
                                        'font-size': '14px',
                                        'transition': 'all 0.3s'
                                    }
                                ),
                            ], style={'grid-column': '3'}),
                        ], style={
                            'display': 'grid',
                            'grid-template-columns': 'repeat(3, 1fr)',
                            'gap': '20px',
                            'margin-bottom': '20px'
                        }),
                        
                        # Dropdowns Grid
                        html.Div([
                            # Ship Mode Dropdown
                            html.Div([
                                html.Label("Ship Mode", style={
                                    'font-weight': '600', 
                                    'color': '#1e293b', 
                                    'margin-bottom': '8px', 
                                    'font-size': '14px',
                                    'display': 'block'
                                }),
                                dcc.Dropdown(
                                    id='predict-ship-mode',
                                    options=[{'label': sm, 'value': sm} for sm in ship_modes],
                                    value=ship_modes[0] if ship_modes else None,
                                    placeholder="Select Ship Mode",
                                    className='prediction-dropdown',
                                    style={
                                        'margin-bottom': '20px', 
                                        'border': '2px solid #e2e8f0', 
                                        'border-radius': '8px', 
                                        'font-size': '14px',
                                        'transition': 'all 0.3s'
                                    }
                                ),
                            ], style={'grid-column': '1'}),
                            
                            # Category Dropdown
                            html.Div([
                                html.Label("Category", style={
                                    'font-weight': '600', 
                                    'color': '#1e293b', 
                                    'margin-bottom': '8px', 
                                    'font-size': '14px',
                                    'display': 'block'
                                }),
                                dcc.Dropdown(
                                    id='predict-category',
                                    options=[{'label': cat, 'value': cat} for cat in categories],
                                    value=categories[0] if categories else None,
                                    placeholder="Select Category",
                                    className='prediction-dropdown',
                                    style={
                                        'margin-bottom': '20px', 
                                        'border': '2px solid #e2e8f0', 
                                        'border-radius': '8px', 
                                        'font-size': '14px',
                                        'transition': 'all 0.3s'
                                    }
                                ),
                            ], style={'grid-column': '2'}),
                            
                            # Sub-Category Dropdown
                            html.Div([
                                html.Label("Sub-Category", style={
                                    'font-weight': '600', 
                                    'color': '#1e293b', 
                                    'margin-bottom': '8px', 
                                    'font-size': '14px',
                                    'display': 'block'
                                }),
                                dcc.Dropdown(
                                    id='predict-subcategory',
                                    options=[{'label': sub, 'value': sub} for sub in subcategories],
                                    value=subcategories[0] if subcategories else None,
                                    placeholder="Select Sub-Category",
                                    className='prediction-dropdown',
                                    style={
                                        'margin-bottom': '20px', 
                                        'border': '2px solid #e2e8f0', 
                                        'border-radius': '8px', 
                                        'font-size': '14px',
                                        'transition': 'all 0.3s'
                                    }
                                ),
                            ], style={'grid-column': '3'}),
                        ], style={
                            'display': 'grid',
                            'grid-template-columns': 'repeat(3, 1fr)',
                            'gap': '20px',
                            'margin-bottom': '20px'
                        }),
                        
                        # Predict Button
                        html.Div([
                            html.Button(
                                "✨ Predict Profit & Loss", 
                                id='predict-button', 
                                n_clicks=0, 
                                style={
                                    'background': 'linear-gradient(to right, #667eea, #764ba2)',
                                    'color': 'white',
                                    'padding': '15px 30px',
                                    'border': 'none',
                                    'border-radius': '8px',
                                    'cursor': 'pointer',
                                    'font-size': '16px',
                                    'font-weight': '600',
                                    'width': '100%',
                                    'box-shadow': '0 4px 6px rgba(0, 0, 0, 0.1)',
                                    'transition': 'all 0.3s',
                                    ':hover': {
                                        'transform': 'translateY(-2px)',
                                        'box-shadow': '0 6px 8px rgba(0, 0, 0, 0.15)'
                                    }
                                }
                            ),
                        ], style={'text-align': 'center'})
                    ], style={
                        'padding': '25px',
                        'background-color': '#ffffff',
                        'border-radius': '12px',
                        'box-shadow': '0 4px 12px rgba(0, 0, 0, 0.08)',
                        'border': '1px solid #e2e8f0'
                    })
                ], style={'width': '45%'}),
                
                # Prediction Output Card (Enhanced)
                dcc.Loading(
                    id="prediction-loading",
                    type="circle",
                    color="#667eea",
                    children=html.Div(
                        id='prediction-output',
                        style={
                            'width': '55%',
                            'padding': '0px',
                            'background-color': '#ffffff',
                            'border-radius': '12px',
                            'box-shadow': '0 4px 12px rgba(0, 0, 0, 0.08)',
                            'border': '1px solid #e2e8f0',
                            'display': 'flex',
                            'flex-direction': 'column',
                            'justify-content': 'center',
                            'min-height': '400px'
                        }
                    ),
                    style={'width': '100%', 'margin': '0 auto'}
                ),
            ], style={
                'display': 'flex', 
                'gap': '25px',
                'margin-bottom': '30px'
            }),
            
            # Information Box
            html.Div([
                html.Div([
                    html.H4("ℹ️ How It Works", style={
                        'color': '#2c3e50',
                        'margin-bottom': '15px',
                        'display': 'flex',
                        'align-items': 'center',
                        'gap': '10px'
                    }),
                    html.Ul([
                        html.Li("The predictor uses machine learning models trained on historical sales data"),
                        html.Li("Profit prediction is based on regression analysis of similar transactions"),
                        html.Li("Loss probability indicates the chance of making a loss based on classification models"),
                        html.Li("Results are estimates - actual outcomes may vary based on market conditions")
                    ], style={
                        'color': '#4a5568',
                        'padding-left': '20px',
                        'line-height': '1.6'
                    })
                ], style={
                    'padding': '20px',
                    'background-color': '#f8fafc',
                    'border-radius': '8px',
                    'border-left': '4px solid #667eea'
                })
            ], style={'width': '100%'})
        ], style={
            **custom_style['card'], 
            'margin-bottom': '20px', 
            'padding': '30px', 
            'background-color': '#ffffff', 
            'border-radius': '12px',
            'box-shadow': '0 8px 20px rgba(0, 0, 0, 0.08)'
        }),
    ])

def register_callbacks(app):
    @app.callback(
        Output('profit-filter-state', 'data'),
        [
            Input('profit-reset-button', 'n_clicks'),
            Input('profit-margin-chart', 'clickData'),
            Input('discount-impact-chart', 'clickData'),
            Input('category-profitability', 'clickData'),
            Input('loss-products-table', 'active_cell')
        ],
        [State('profit-filter-state', 'data')]
    )
    def update_profit_filter_state(reset_clicks, margin_click, discount_click, category_click, table_click, current_state):
        ctx = dash.callback_context
        
        if not ctx.triggered:
            return current_state
            
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        if trigger_id == 'profit-reset-button':
            return {
                'selected_category': None,
                'selected_discount_range': None,
                'selected_product': None
            }
        
        new_state = current_state.copy()
        
        if trigger_id == 'profit-margin-chart' and margin_click and 'points' in margin_click:
            new_state['selected_category'] = margin_click['points'][0]['x']
            new_state['selected_discount_range'] = None
            new_state['selected_product'] = None
            
        elif trigger_id == 'discount-impact-chart' and discount_click and 'points' in discount_click:
            new_state['selected_discount_range'] = discount_click['points'][0]['x']
            new_state['selected_category'] = None
            new_state['selected_product'] = None
            
        elif trigger_id == 'category-profitability' and category_click and 'points' in category_click:
            point = category_click['points'][0]
            if 'customdata' in point and point['customdata']:
                new_state['selected_category'] = point['customdata'][0]
            elif 'hovertext' in point:
                new_state['selected_category'] = point['hovertext']
            elif 'x' in point:
                new_state['selected_category'] = point['x']
            new_state['selected_discount_range'] = None
            new_state['selected_product'] = None
            
        elif trigger_id == 'loss-products-table' and table_click:
            pass
            
        return new_state

    @app.callback(
        [
            Output('profit-margin-chart', 'figure'),
            Output('discount-impact-chart', 'figure'),
            Output('category-profitability', 'figure'),
            Output('discount-distribution', 'figure'),
            Output('loss-products-table', 'children'),
            Output('profit-filter-indicator', 'children')
        ],
        [
            Input('current-page', 'data'),
            Input('profit-filter-state', 'data')
        ]
    )
    def update_profit_charts(current_page, filter_state):
        df, _, _, _, _, _, _ = get_data()
        
        if current_page != 'profit':
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
        
        if df.empty:
            logger.warning("DataFrame is empty in update_profit_charts")
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, "No data available"
        
        # Dynamically detect column names
        category_col = next((col for col in df.columns if 'category' in col.lower()), 'Category')
        subcategory_col = next((col for col in df.columns if 'sub' in col.lower() and 'category' in col.lower()), 'Sub-Category')
        discount_col = next((col for col in df.columns if 'discount' in col.lower()), 'Discount')
        sales_col = next((col for col in df.columns if 'sales' in col.lower()), 'Sales')
        profit_col = next((col for col in df.columns if 'profit' in col.lower()), 'Profit')
        product_col = next((col for col in df.columns if 'product' in col.lower() and 'name' in col.lower()), 'Product Name')
        
        selected_category = filter_state.get('selected_category')
        selected_discount_range = filter_state.get('selected_discount_range')
        
        if selected_category:
            filter_text = f"Filtered by Category: {selected_category}"
        elif selected_discount_range:
            filter_text = f"Filtered by Discount Range: {selected_discount_range}"
        else:
            filter_text = "No filter applied. Click on charts to filter data."
        
        filtered_df = df
        if selected_category and category_col in df.columns:
            filtered_df = df[df[category_col] == selected_category]
        elif selected_discount_range and discount_col in df.columns:
            range_map = {
                '0-10%': (0, 0.1),
                '10-20%': (0.1, 0.2),
                '20-30%': (0.2, 0.3),
                '30%+': (0.3, 1.0)
            }
            min_d, max_d = range_map.get(selected_discount_range, (0, 1))
            filtered_df = df[(df[discount_col] >= min_d) & (df[discount_col] < max_d)]
        
        # Profit Margin by Category
        if category_col in filtered_df.columns and sales_col in filtered_df.columns and profit_col in filtered_df.columns:
            category_profit = filtered_df.groupby(category_col).agg({
                sales_col: 'sum',
                profit_col: 'sum'
            }).reset_index()
            category_profit['profit_margin'] = (category_profit[profit_col] / category_profit[sales_col] * 100).round(2)
            
            margin_chart = px.bar(category_profit, x=category_col, y='profit_margin',
                                 title=f'📊 Profit Margin by Category {"- " + selected_category if selected_category else "- " + selected_discount_range if selected_discount_range else ""} (%)',
                                 color='profit_margin',
                                 color_continuous_scale='RdYlGn')
            margin_chart.update_layout(plot_bgcolor='white', paper_bgcolor='white')
        else:
            margin_chart = px.bar(title="📊 Profit Margin by Category - Data Unavailable")
        
        # Discount Impact
        if discount_col in filtered_df.columns:
            filtered_df['discount_range'] = pd.cut(filtered_df[discount_col], bins=[0, 0.1, 0.2, 0.3, 1.0], 
                                         labels=['0-10%', '10-20%', '20-30%', '30%+'])
            discount_impact = filtered_df.groupby('discount_range').agg({
                sales_col: 'sum',
                profit_col: 'sum'
            }).reset_index()
            
            impact_chart = px.bar(discount_impact, x='discount_range', y=[sales_col, profit_col],
                                 title=f'💸 Discount Impact on Sales & Profit {"- " + selected_category if selected_category else ""}',
                                 barmode='group',
                                 color_discrete_sequence=['#667eea', '#f5576c'])
            impact_chart.update_layout(plot_bgcolor='white', paper_bgcolor='white')
        else:
            impact_chart = px.bar(title="💸 Discount Impact - Data Unavailable")
        
        # Category Profitability
        groupby_columns = [category_col]
        if subcategory_col in filtered_df.columns:
            groupby_columns.append(subcategory_col)
        
        if all(c in filtered_df.columns for c in groupby_columns + [sales_col, profit_col]):
            cat_profit_detail = filtered_df.groupby(groupby_columns).agg({
                profit_col: 'sum',
                sales_col: 'sum'
            }).reset_index()
            
            # Transform profit for size to ensure non-negative values
            cat_profit_detail['profit_size'] = np.abs(cat_profit_detail[profit_col])  # Use absolute value
            cat_profit_detail['profit_size'] = cat_profit_detail['profit_size'] + 1  # Shift to avoid zero
            
            hover_data = {category_col: True, sales_col: ':.2f', profit_col: ':.2f'}
            if subcategory_col in groupby_columns:
                hover_data[subcategory_col] = True
            
            profitability_chart = px.scatter(
                cat_profit_detail, 
                x=sales_col, 
                y=profit_col,
                color=category_col, 
                size='profit_size',  # Use transformed column
                hover_name=category_col,
                hover_data=hover_data,
                custom_data=[category_col],
                title=f'💎 Category Profitability Matrix {"- " + selected_category if selected_category else "- " + selected_discount_range if selected_discount_range else ""}'
            )
            profitability_chart.update_layout(plot_bgcolor='white', paper_bgcolor='white')
        else:
            profitability_chart = px.scatter(title="💎 Category Profitability - Data Unavailable")
        
        # Discount Distribution
        if discount_col in filtered_df.columns:
            discount_dist = px.histogram(filtered_df, x=discount_col, nbins=20,
                                       title=f'📈 Discount Distribution {"- " + selected_category if selected_category else ""}',
                                       color_discrete_sequence=['#f5576c'])
            discount_dist.update_layout(plot_bgcolor='white', paper_bgcolor='white')
        else:
            discount_dist = px.histogram(title="📈 Discount Distribution - Data Unavailable")
        
        # Loss Products Table
        if product_col in filtered_df.columns and profit_col in filtered_df.columns:
            loss_products = filtered_df.groupby(product_col)[profit_col].sum().reset_index()
            loss_products = loss_products[loss_products[profit_col] < 0].nsmallest(10, profit_col)
            loss_products.columns = ['Product', 'Loss ($)']
            loss_products['Loss ($)'] = loss_products['Loss ($)'].round(1)
            
            if not loss_products.empty:
                loss_table = dash_table.DataTable(
                    data=loss_products.to_dict('records'),
                    columns=[{"name": i, "id": i, "type": "numeric", "format": {"specifier": ",.2f"}} if 'Loss' in i else {"name": i, "id": i} for i in loss_products.columns],
                    style_cell={'textAlign': 'left', 'padding': '10px', 'fontSize': 14},
                    style_header={
                        'backgroundColor': '#e74c3c',
                        'color': 'white',
                        'fontWeight': 'bold',
                        'textAlign': 'center'
                    },
                    style_data={'backgroundColor': '#fdf2f2'},
                    style_data_conditional=[
                        {
                            'if': {'row_index': i},
                            'backgroundColor': '#fdf2f2' if i % 2 == 0 else '#ffffff',
                            'color': 'black'
                        } for i in range(len(loss_products))
                    ],
                    tooltip_data=[
                        {
                            col: {'value': f"{row[col]:,.2f}" if 'Loss' in col else row[col], 'type': 'markdown'}
                            for col in loss_products.columns
                        } for _, row in loss_products.iterrows()
                    ],
                    style_table={'overflowX': 'auto'},
                )
            else:
                loss_table = html.P("🎉 No products with losses found!", style={'text-align': 'center', 'color': '#27ae60'})
        else:
            loss_table = html.P("⚠️ Product or profit data unavailable", style={'text-align': 'center', 'color': '#e74c3c'})
        
        return margin_chart, impact_chart, profitability_chart, discount_dist, loss_table, filter_text

    @app.callback(
    Output('prediction-output', 'children'),
    Input('predict-button', 'n_clicks'),
    [
        State('predict-quantity', 'value'),
        State('predict-discount', 'value'),
        State('predict-shipping-cost', 'value'),
        State('predict-ship-mode', 'value'),
        State('predict-category', 'value'),
        State('predict-subcategory', 'value')
    ]
)
    def update_prediction_output(n_clicks, quantity, discount, shipping_cost, ship_mode, category, subcategory):
        if n_clicks == 0:
            return html.Div([
                html.Div([
                    html.Img(src='assets/prediction_placeholder.png', style={
                        'width': '150px',
                        'opacity': '0.6',
                        'margin-bottom': '20px'
                    }),
                    html.H4("Ready to Predict", style={
                        'color': '#4a5568',
                        'margin-bottom': '10px'
                    }),
                    html.P("Fill in all parameters and click the predict button to see results", style={
                        'color': '#718096',
                        'text-align': 'center'
                    })
                ], style={
                    'display': 'flex',
                    'flex-direction': 'column',
                    'align-items': 'center',
                    'justify-content': 'center',
                    'height': '100%',
                    'padding': '40px'
                })
            ])
        
        if any(v is None for v in [quantity, discount, shipping_cost, ship_mode, category, subcategory]):
            return html.Div([
                html.Div([
                    html.I(className="fas fa-exclamation-triangle", style={
                        'color': '#e53e3e',
                        'font-size': '48px',
                        'margin-bottom': '20px'
                    }),
                    html.H4("Missing Information", style={
                        'color': '#2d3748',
                        'margin-bottom': '10px'
                    }),
                    html.P("Please fill in all fields to get a prediction", style={
                        'color': '#718096'
                    })
                ], style={
                    'display': 'flex',
                    'flex-direction': 'column',
                    'align-items': 'center',
                    'text-align': 'center',
                    'padding': '40px'
                })
            ])
        
        # Convert discount from percentage to decimal
        try:
            discount_decimal = float(discount) / 100
            if not (0 <= discount_decimal <= 1):
                raise ValueError("Discount must be between 0% and 100%")
        except ValueError:
            return html.Div([
                html.Div([
                    html.I(className="fas fa-exclamation-circle", style={
                        'color': '#dd6b20',
                        'font-size': '48px',
                        'margin-bottom': '20px'
                    }),
                    html.H4("Invalid Discount", style={
                        'color': '#2d3748',
                        'margin-bottom': '10px'
                    }),
                    html.P("Please enter a discount value between 0 and 100", style={
                        'color': '#718096'
                    })
                ], style={
                    'display': 'flex',
                    'flex-direction': 'column',
                    'align-items': 'center',
                    'text-align': 'center',
                    'padding': '40px'
                })
            ])
        
        result = predict_profit_and_loss(quantity, discount_decimal, shipping_cost, ship_mode, category, subcategory)
        
        if 'error' in result:
            return html.Div([
                html.Div([
                    html.I(className="fas fa-times-circle", style={
                        'color': '#e53e3e',
                        'font-size': '48px',
                        'margin-bottom': '20px'
                    }),
                    html.H4("Prediction Error", style={
                        'color': '#2d3748',
                        'margin-bottom': '10px'
                    }),
                    html.P(result['error'], style={
                        'color': '#718096',
                        'text-align': 'center'
                    })
                ], style={
                    'display': 'flex',
                    'flex-direction': 'column',
                    'align-items': 'center',
                    'padding': '40px'
                })
            ])
        
        # Determine colors and icons based on results
        if result['Predicted Profit'] >= 0 and result['Loss Probability'] < 0.5:
            profit_color = '#38a169'
            status_color = '#38a169'
            status_icon = 'fas fa-check-circle'
            status_bg = '#f0fff4'
            card_bg = 'linear-gradient(to right, #f0fff4, #c6f6d5)'
        elif result['Predicted Profit'] < 0:
            profit_color = '#e53e3e'
            status_color = '#e53e3e'
            status_icon = 'fas fa-exclamation-triangle'
            status_bg = '#fff5f5'
            card_bg = 'linear-gradient(to right, #fff5f5, #fed7d7)'
        else:
            profit_color = '#d69e2e'
            status_color = '#d69e2e'
            status_icon = 'fas fa-exclamation-circle'
            status_bg = '#fffaf0'
            card_bg = 'linear-gradient(to right, #fffaf0, #feebc8)'
        
        return html.Div([
            html.Div([
                # Header
                html.Div([
                    html.I(className="fas fa-chart-line", style={
                        'font-size': '24px',
                        'color': '#4a5568',
                        'margin-right': '10px'
                    }),
                    html.H4("Prediction Results", style={
                        'color': '#2d3748',
                        'margin': '0',
                        'font-weight': '600'
                    })
                ], style={
                    'display': 'flex',
                    'align-items': 'center',
                    'margin-bottom': '25px',
                    'padding-bottom': '15px',
                    'width': '800px'      # <--- Ubah atau tambahkan ini
                }),
                
                # Results Grid
                html.Div([
                    # Profit Card
                    html.Div([
                        html.Div([
                            html.P("Predicted Profit", style={
                                'color': '#4a5568',
                                'margin-bottom': '10px',
                                'font-size': '14px',
                                'font-weight': '600'
                            }),
                            html.Div([
                                html.Span("$", style={
                                    'font-size': '20px',
                                    'color': '#4a5568',
                                    'margin-right': '5px'
                                }),
                                html.Span(f"{result['Predicted Profit']:,.2f}", style={
                                    'font-size': '28px',
                                    'font-weight': '700',
                                    'color': profit_color
                                })
                            ], style={
                                'display': 'flex',
                                'align-items': 'baseline'
                            })
                        ], style={
                            'padding': '20px',
                            'background-color': '#ffffff',
                            'border-radius': '8px',
                            'border': '1px solid #e2e8f0',
                            'box-shadow': '0 2px 4px rgba(0, 0, 0, 0.05)'
                        })
                    ], style={'grid-column': '1'}),
                    
                    # Loss Probability Card
                    html.Div([
                        html.Div([
                            html.P("Loss Probability", style={
                                'color': '#4a5568',
                                'margin-bottom': '10px',
                                'font-size': '14px',
                                'font-weight': '600'
                            }),
                            html.Div([
                                html.Span(f"{result['Loss Probability']:.1%}", style={
                                    'font-size': '28px',
                                    'font-weight': '700',
                                    'color': '#e53e3e' if result['Loss Probability'] > 0.5 else '#4a5568'
                                })
                            ])
                        ], style={
                            'padding': '20px',
                            'background-color': '#ffffff',
                            'border-radius': '8px',
                            'border': '1px solid #e2e8f0',
                            'box-shadow': '0 2px 4px rgba(0, 0, 0, 0.05)'
                        })
                    ], style={'grid-column': '2'}),
                    
                    # Status Card
                    html.Div([
                        html.Div([
                            html.P("Recommendation", style={
                                'color': '#4a5568',
                                'margin-bottom': '10px',
                                'font-size': '14px',
                                'font-weight': '600'
                            }),
                            html.Div([
                                html.I(className=status_icon, style={
                                    'font-size': '20px',
                                    'color': status_color,
                                    'margin-right': '10px'
                                }),
                                html.Span(result['Status'], style={
                                    'font-size': '20px',
                                    'font-weight': '600',
                                    'color': status_color
                                })
                            ], style={
                                'display': 'flex',
                                'align-items': 'center'
                            })
                        ], style={
                            'padding': '20px',
                            'background-color': status_bg,
                            'border-radius': '8px',
                            'border': f'1px solid {status_color}',
                            'box-shadow': '0 2px 4px rgba(0, 0, 0, 0.05)'
                        })
                    ], style={'grid-column': '3'}),
                ], style={
                    'display': 'grid',
                    'grid-template-columns': 'repeat(3, 1fr)',
                    'gap': '20px',
                    'margin-bottom': '25px'
                }),
                
                # Insights Section
                html.Div([
                    html.P("Insights & Recommendations", style={
                        'color': '#2d3748',
                        'font-weight': '600',
                        'margin-bottom': '15px',
                        'font-size': '16px'
                    }),
                    
                    html.Ul([
                        html.Li([
                            html.Span("Profitability: ", style={'font-weight': '600'}),
                            html.Span("This transaction is " + ("likely to be profitable" if result['Predicted Profit'] >= 0 
                                    else "likely to result in a loss") + " based on historical data.")
                        ]),
                        html.Li([
                            html.Span("Risk Level: ", style={'font-weight': '600'}),
                            html.Span("There's a " + ("low" if result['Loss Probability'] < 0.3 
                                    else "moderate" if result['Loss Probability'] < 0.5 
                                    else "high") + " chance of making a loss with these parameters.")
                        ]),
                        html.Li([
                            html.Span("Recommendation: ", style={'font-weight': '600'}),
                            html.Span("Consider " + ("proceeding with this transaction" if result['Status'] == 'Aman' 
                                    else "adjusting discount, quantity, or shipping options") + " for better results.")
                        ])
                    ], style={
                        'color': '#4a5568',
                        'padding-left': '20px',
                        'line-height': '1.8',
                        'margin-bottom': '0'
                    })
                ], style={
                    'padding': '20px',
                    'background-color': '#f8fafc',
                    'border-radius': '8px',
                    'border-left': '4px solid #667eea'
                })
            ], style={
                'padding': '30px',
                'background': card_bg,
                'border-radius': '10px',
                'height': '100%'
            })
        ])