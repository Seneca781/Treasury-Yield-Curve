import dash
from dash import dcc, html, Input, Output
import plotly.graph_objs as go
import ycnbc

# Initialize the Dash app
app = dash.Dash(__name__)

# Create the layout
app.layout = html.Div(children=[
    html.H1(children='Treasury Yield Curve', style={'textAlign': 'center'}),

    dcc.Graph(id='yield-curve'),

    dcc.Interval(
        id='interval-component',
        interval=1*1000,  # Update every 1 second
        n_intervals=0  # This counts how many times the interval has triggered
    ),

    html.Div(children=[
        html.H2(children='Key Slopes of the Yield Curve', style={'textAlign': 'center'}),
        html.Div(id='slope-info', style={'textAlign': 'center'})
    ])
])

# Define callback to update graph and slopes
@app.callback(
    Output('yield-curve', 'figure'),
    Output('slope-info', 'children'),
    Input('interval-component', 'n_intervals')
)
def update_graph(n):
    # Fetch bond data
    markets = ycnbc.Markets()
    bonds_data = markets.bonds()

    # Prepare data for the yield curve
    maturities = []
    yields = []

    # Filter U.S. bonds and extract maturity and yield
    for bond in bonds_data:
        if bond['symbol'].startswith('US'):
            maturities.append(bond['symbol'])
            yields.append(float(bond['last'].replace('%', '').strip()))

    # Create the yield curve graph
    yield_curve_fig = go.Figure()
    yield_curve_fig.add_trace(go.Scatter(x=maturities, y=yields, mode='lines+markers'))

    # Filter specific yields for 2-year and 10-year
    yield_2yr = None
    yield_10yr = None
    for bond in bonds_data:
        if bond['symbol'] == 'US2Y':
            yield_2yr = float(bond['last'].replace('%', '').strip())
        elif bond['symbol'] == 'US10Y':
            yield_10yr = float(bond['last'].replace('%', '').strip())

    # Calculate slope (2-year to 10-year)
    slope_2_10 = yield_10yr - yield_2yr if yield_2yr and yield_10yr else None

    # Update slope info
    slope_info = f'2-Year to 10-Year Slope: {slope_2_10:.2f}%' if slope_2_10 is not None else 'Data not available'

    return yield_curve_fig, slope_info

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
