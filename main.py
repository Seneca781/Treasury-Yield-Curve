import dash
from dash import dcc, html, Input, Output
import plotly.graph_objs as go
import ycnbc

# Initialize the Dash app
app = dash.Dash(__name__)

# Function to fetch bond data
def fetch_bond_data():
    markets = ycnbc.Markets()
    bonds_data = markets.bonds()
    return bonds_data

# Prepare initial data for the yield curve
def prepare_yield_curve(bonds_data):
    maturities = []
    yields = []

    # Filter U.S. bonds and extract maturity and yield
    for bond in bonds_data:
        if bond['symbol'].startswith('US'):
            maturities.append(bond['symbol'])
            yields.append(float(bond['last'].replace('%', '').strip()) / 100)  # Convert to decimal

    return maturities, yields

# Create dashboard layout
app.layout = html.Div(children=[
    html.H1(children='Treasury Yield Curve', style={'textAlign': 'center'}),

    dcc.Graph(id='yield-curve'),

    html.Div(children=[
        html.H2(children='Key Slopes of the Yield Curve', style={'textAlign': 'center'}),
        html.Div(id='slope-info', style={'textAlign': 'center'})
    ]),

    # Centered and styled button
    html.Div(
        html.Button('Refresh Data', id='refresh-button', n_clicks=0,
                    style={
                        'margin-top': '20px',
                        'padding': '10px 20px',
                        'font-size': '16px',
                        'color': 'white',
                        'background-color': '#007BFF',
                        'border': 'none',
                        'border-radius': '5px',
                        'cursor': 'pointer',
                        'box-shadow': '0 4px 6px rgba(0, 0, 0, 0.1)',
                    }),
        style={'textAlign': 'center'}  # Center the button
    ),
    # Disclaimer section
    html.Div(children='Data sourced from CNBC. This dashboard is for educational and informational purposes only.',
             style={'textAlign': 'center', 'marginTop': '20px', 'fontSize': '12px', 'color': 'gray'})
])

# Callback to update the yield curve graph and slopes when the button is clicked
@app.callback(
    Output('yield-curve', 'figure'),
    Output('slope-info', 'children'),
    Input('refresh-button', 'n_clicks')
)
def update_graph(n_clicks):
    bonds_data = fetch_bond_data()  # Fetch new data
    maturities, yields = prepare_yield_curve(bonds_data)  # Prepare data for graph

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

    # Set layout for the graph with axis titles
    yield_curve_fig.update_layout(
        xaxis={'title': 'Maturity'},
        yaxis={'title': 'Yield (%)'},
        hovermode='closest')

    return yield_curve_fig, slope_info  # Return updated figure and slope info

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
