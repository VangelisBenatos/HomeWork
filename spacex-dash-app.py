# Import required libraries
import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")

# Get min and max payload for the slider
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Prepare dropdown options for launch sites, including 'ALL'
launch_sites = spacex_df['Launch Site'].unique().tolist()
dropdown_options = [{'label': 'All Sites', 'value': 'ALL'}] + [{'label': site, 'value': site} for site in launch_sites]

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    
    # TASK 1: Launch Site Dropdown
    dcc.Dropdown(
        id='site-dropdown',
        options=dropdown_options,
        value='ALL',
        placeholder="Select a Launch Site here",
        searchable=True
    ),
    html.Br(),
    
    # TASK 2: Success Pie Chart
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),
    
    html.P("Payload range (Kg):"),
    
    # TASK 3: Payload Range Slider
    dcc.RangeSlider(
        id='payload-slider',
        min=0, max=10000, step=1000,
        marks={i: f'{i}' for i in range(0, 10001, 2500)},
        value=[min_payload, max_payload]
    ),
    html.Br(),
    
    # TASK 4: Success-Payload Scatter Chart
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])


# TASK 2: Callback for updating the success pie chart based on selected launch site
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        # For all sites: Show total successful launches by site
        fig = px.pie(spacex_df[spacex_df['class'] == 1], 
                     names='Launch Site', 
                     title='Total Successful Launches by Site')
        return fig
    else:
        # Filter for the selected site and show success vs failure counts
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        success_fail_counts = filtered_df['class'].value_counts().reset_index()
        success_fail_counts.columns = ['class', 'count']
        success_fail_counts['class'] = success_fail_counts['class'].map({1: 'Success', 0: 'Failure'})
        fig = px.pie(success_fail_counts, 
                     names='class', 
                     values='count',
                     title=f'Success vs Failure for site {entered_site}')
        return fig


# TASK 4: Callback for updating scatter plot based on selected site and payload range
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def get_scatter_chart(entered_site, payload_range):
    low, high = payload_range
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) & 
                            (spacex_df['Payload Mass (kg)'] <= high)]
    
    if entered_site == 'ALL':
        fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class',
                         color='Booster Version Category',
                         title='Payload vs Outcome for All Sites',
                         labels={'class': 'Launch Outcome'})
    else:
        filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class',
                         color='Booster Version Category',
                         title=f'Payload vs Outcome for site {entered_site}',
                         labels={'class': 'Launch Outcome'})
    return fig


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
