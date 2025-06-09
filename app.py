import dash
from dash import dcc, html
from src.components.sidebar import create_sidebar
from src.components.pages.overview import create_overview_page, register_callbacks as register_overview_callbacks
from src.components.pages.region import create_region_page, register_callbacks as register_region_callbacks
from src.components.pages.customer import create_customer_page, register_callbacks as register_customer_callbacks
from src.components.pages.profit import create_profit_page, register_callbacks as register_profit_callbacks
from dash.dependencies import Input, Output

# Inisialisasi aplikasi Dash
app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = "Superstore BI Dashboard"

# Daftarkan callback dari setiap halaman
register_overview_callbacks(app)
register_region_callbacks(app)
register_customer_callbacks(app)
register_profit_callbacks(app)

# Layout utama
app.layout = html.Div([
    dcc.Store(id='current-page', data='overview'),
    create_sidebar(),
    html.Div(id='page-content', style={'margin-left': '270px', 'padding': '20px', 'background-color': '#f8f9fa', 'min-height': '100vh'})
])

# Callback untuk navigasi halaman
@app.callback(
    Output('page-content', 'children'),
    [Input('current-page', 'data')]
)
def display_page(current_page):
    print(f"Rendering page: {current_page}")
    if current_page == 'overview':
        return create_overview_page()
    elif current_page == 'region':
        return create_region_page()
    elif current_page == 'customer':
        return create_customer_page()
    elif current_page == 'profit':
        return create_profit_page()
    return create_overview_page()

# Callback untuk navigasi sidebar
@app.callback(
    [Output('current-page', 'data'),
     Output('nav-overview', 'style'),
     Output('nav-region', 'style'),
     Output('nav-customer', 'style'),
     Output('nav-profit', 'style')],
    [Input('nav-overview', 'n_clicks'),
     Input('nav-region', 'n_clicks'),
     Input('nav-customer', 'n_clicks'),
     Input('nav-profit', 'n_clicks')]
)
def update_page(overview_clicks, region_clicks, customer_clicks, profit_clicks):
    from src.config.styles import custom_style
    ctx = dash.callback_context
    
    if not ctx.triggered:
        print("No navigation triggered, defaulting to overview")
        return 'overview', {**custom_style['nav-link'], **custom_style['nav-link-active']}, custom_style['nav-link'], custom_style['nav-link'], custom_style['nav-link']
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    print(f"Navigation triggered by: {button_id}")
    
    styles = [custom_style['nav-link']] * 4
    if button_id == 'nav-overview':
        styles[0] = {**custom_style['nav-link'], **custom_style['nav-link-active']}
        return 'overview', *styles
    elif button_id == 'nav-region':
        styles[1] = {**custom_style['nav-link'], **custom_style['nav-link-active']}
        return 'region', *styles
    elif button_id == 'nav-customer':
        styles[2] = {**custom_style['nav-link'], **custom_style['nav-link-active']}
        return 'customer', *styles
    elif button_id == 'nav-profit':
        styles[3] = {**custom_style['nav-link'], **custom_style['nav-link-active']}
        return 'profit', *styles
    
    return 'overview', {**custom_style['nav-link'], **custom_style['nav-link-active']}, custom_style['nav-link'], custom_style['nav-link'], custom_style['nav-link']

if __name__ == '__main__':
    app.run(debug=True, port=8050)

