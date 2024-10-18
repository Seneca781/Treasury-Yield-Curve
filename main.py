import dash
from dash import dcc, html, Input, Output
import plotly.graph_objs as go
import ycnbc

# Initialize the Dash app
app = dash.Dash(__name__)

# Current Federal Funds Rate
CURRENT_FED_RATE = 5.13  # Update as necessary

# Create the layout
app.layout = html.Div(children=[
    html.H1(children='Daily Economics', style={'textAlign': 'center', 'color': '#4a4a4a', 'fontSize': '36px'}),

    dcc.Graph(id='yield-curve'),

    dcc.Interval(
        id='interval-component',
        interval=1 * 1000,  # Update every 1 second
        n_intervals=0  # This counts how many times the interval has triggered
    ),

    html.Div(children=[
        html.H2(children='Key Slopes of the Yield Curve', style={'textAlign': 'center'}),
        html.Div(id='slope-info', style={'textAlign': 'center', 'fontSize': '20px', 'margin': '10px 0'})
    ]),

    # Macro indicators section
    html.Div(id='macro-indicators', style={
        'textAlign': 'center',
        'marginTop': '20px',
        'padding': '20px',
        'border': '1px solid #dcdcdc',
        'borderRadius': '10px',
        'backgroundColor': '#f9f9f9'
    }),
])


# Define callback to update graph, slopes, and macro indicators
@app.callback(
    Output('yield-curve', 'figure'),
    Output('slope-info', 'children'),
    Output('macro-indicators', 'children'),
    Input('interval-component', 'n_intervals')
)
def update_graph(n):
    # Fetch bond data
    markets = ycnbc.Markets()
    bonds_data = markets.bonds()

    # Prepare data for the yield curve
    maturities = []
    yields = []

    for bond in bonds_data:
        if bond['symbol'].startswith('US'):
            maturities.append(bond['symbol'])
            yields.append(float(bond['last'].replace('%', '').strip()))

    # Create the yield curve graph
    yield_curve_fig = go.Figure()
    yield_curve_fig.add_trace(go.Scatter(x=maturities, y=yields, mode='lines+markers'))

    # Update layout with axis titles
    yield_curve_fig.update_layout(
        xaxis_title='Maturity',
        yaxis_title='Yield (%)',
        title='U.S. Treasury Yield Curve',
        transition_duration=500
    )

    # Fetch yields for 2-year and 10-year bonds
    yield_2yr = next((float(bond['last'].replace('%', '').strip()) for bond in bonds_data if bond['symbol'] == 'US2Y'),
                     None)
    yield_10yr = next(
        (float(bond['last'].replace('%', '').strip()) for bond in bonds_data if bond['symbol'] == 'US10Y'), None)

    # Calculate slope (2-year to 10-year)
    slope_2_10 = yield_10yr - yield_2yr if yield_2yr and yield_10yr else None

    # Update slope info
    slope_info = f'2-Year to 10-Year Slope: {slope_2_10:.2f}%' if slope_2_10 is not None else 'Data not available'

    # Determine if the curve is flattening, steepening, or flat
    curve_trend = 'Steepening' if slope_2_10 > 0 else 'Flattening' if slope_2_10 < 0 else 'Flat'

    # Create macro indicators text
    macro_info = html.Div(children=[
        html.P(f'Current Fed Rate: {CURRENT_FED_RATE}%', style={'fontSize': '20px'}),
        html.P(f'Yield Curve Trend: {curve_trend}', style={'fontSize': '20px'})
    ])

    return yield_curve_fig, slope_info, macro_info


# Run the app
if __name__ == '__main__':
    app.run(debug=True)
