import dash
from dash import dcc, html, Input, Output
import plotly.graph_objs as go
import ycnbc

# Initialize the Dash app
app = dash.Dash(__name__)

# Create the layout
app.layout = html.Div(style={'backgroundColor': '#f9f9f9', 'padding': '20px'}, children=[
    html.H1(children='Daily Economics', style={'textAlign': 'center', 'color': '#2c3e50'}),

    dcc.Graph(id='yield-curve'),

    dcc.Interval(
        id='interval-component',
        interval=1*1000,  # Update every 1 second
        n_intervals=0  # This counts how many times the interval has triggered
    ),

    html.Div(children=[
        html.H2(children='Key Indicators', style={'textAlign': 'center', 'color': '#2980b9'}),
        html.Div(id='slope-info', style={'textAlign': 'center', 'color': '#34495e'}),
        html.Div(id='steepening-info', style={'textAlign': 'center', 'color': '#34495e'}),
        html.Div(id='fed-rate-info', style={'textAlign': 'center', 'color': '#34495e'}),
        html.Div(id='overall-change-info', style={'textAlign': 'center', 'color': '#34495e'}),
    ])
])

# Define callback to update graph and indicators
@app.callback(
    Output('yield-curve', 'figure'),
    Output('slope-info', 'children'),
    Output('steepening-info', 'children'),
    Output('fed-rate-info', 'children'),
    Output('overall-change-info', 'children'),
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

    # Add axis labels
    yield_curve_fig.update_layout(
        xaxis_title='Maturity',
        yaxis_title='Yield (%)',
        title='Treasury Yield Curve',
        plot_bgcolor='#f9f9f9',  # Optional: add a light background for the plot
        font=dict(color='#34495e')  # Font color for the plot text
    )

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

    # Determine steepening or flattening
    steepening_info = 'Curve is Steepening' if slope_2_10 > 0 else 'Curve is Flattening'

    # Current Fed Rate
    fed_rate = 5.13
    fed_rate_info = f'Current Fed Rate: {fed_rate:.2f}%'

    # Overall change logic (this should ideally come from your historical data)
    overall_change = slope_2_10  # This should be based on historical data comparison
    overall_change_color = 'green' if overall_change > 0 else 'red' if overall_change < 0 else 'black'
    overall_change_info = f'Overall Change (2/10YR): {overall_change:.2f}%'
    overall_change_info = html.Div(overall_change_info, style={'color': overall_change_color})

    # Update slope info
    slope_info = f'2-Year to 10-Year Slope: {slope_2_10:.2f}%' if slope_2_10 is not None else 'Data not available'

    return yield_curve_fig, slope_info, steepening_info, fed_rate_info, overall_change_info

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
