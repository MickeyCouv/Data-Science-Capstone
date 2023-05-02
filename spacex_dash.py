# Import required libraries
import pandas as pd
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
from jupyter_dash import JupyterDash
import plotly.graph_objects as go
import plotly.express as px
from dash import no_update

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv('spacex_launch_dash.csv')
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = JupyterDash(__name__)
JupyterDash.infer_jupyter_proxy_config()

# Clear the layout and do not display exception till callback gets executed
app.config.suppress_callback_exceptions = True

# Create an app layout
app.layout = html.Div([
		html.H1(
			'SpaceX Launch Records Dashboard',
			style={
				'textAlign': 'center',
				'color':'#503D36',
				'font-size': 40
			}
		),
		# TASK 1: Add a dropdown list to enable Launch Site selection
		# The default select value is for ALL sites
		# Get a list of unique launch sites
		html.Div([
			dcc.Dropdown(
				id='site-dropdown',
				options=[{'label':'All Sites','value':'ALL'}]+[{'label': i,'value': i}
																  for i in spacex_df['Launch Site'].unique()],
				value='ALL',
				placeholder='Select a Launch Site',
				searchable=True
			)
		]),
		# Create the pie chart division
		html.Div(
			dcc.Graph(
				id='success-pie-chart'
			)
		),
		# Create the range slider division
		html.P("Payload range (Kg):"),
			dcc.RangeSlider(
			id='payload-slider',
			min=0,
			max=10000,
			step=1000,
			marks={0: '0', 2500: '2500', 5000: '5000', 7500: '7500', 10000:'10000'},
			value=[min_payload, max_payload]
		),
		html.Div(
			dcc.Graph(
				id='success-payload-scatter-chart'
			)
		),
	])
# Function decorator to specify function input and output
@app.callback(
	Output(
		component_id='success-pie-chart',
		component_property='figure'),
	Input(
		component_id='site-dropdown',
		component_property='value'))
# Success Pie Chart
def get_pie_chart(entered_site):
	if entered_site == 'ALL':
		site_counts = spacex_df.groupby(['Launch Site', 'class'])['class'].count().unstack()
		site_counts = site_counts.fillna(0)
		site_counts['Success Rate'] = site_counts[1] / (site_counts[0] + site_counts[1]) * 100
		site_counts = site_counts.reset_index()
		fig = px.pie(site_counts, values='Success Rate', names='Launch Site', title='All Sites')
	else:
		filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
		counts = filtered_df['class'].value_counts()
		success_count = counts[1]
		failure_count = counts[0]
		labels = ['Success', 'Failure']
		values = [success_count, failure_count]
		fig = go.Figure(data=[go.Pie(labels=labels, values=values, marker=dict(colors=['green', 'red']))])
		fig.update_layout(title=entered_site)
	return fig
@app.callback(
	Output(
		component_id='success-payload-scatter-chart',
		component_property='figure'),
	[Input(
		component_id='site-dropdown',
		component_property='value'
	),
	 Input(
		 component_id='payload-slider',
		 component_property='value')
	]
)
# Payload Scatter Plot
def get_scatter_plot(entered_site, payload_range):
    if entered_site == 'ALL':
        filtered_df = spacex_df
        title = 'Correlation between Payload and Success for all Sites'
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        title = entered_site
        filtered_df = filtered_df[(filtered_df['Payload Mass (kg)'] >= payload_range[0]) &
                                  (filtered_df['Payload Mass (kg)'] <= payload_range[1])]
    if filtered_df.empty:
        return no_update
    
    categories = filtered_df['Booster Version Category'].unique()
    colors = px.colors.qualitative.Alphabet[:len(categories)]
    category_color_map = {category: color for category, color in zip(categories, colors)}
    
    fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class', color='Booster Version Category',
                     color_discrete_map=category_color_map)
    
    fig.update_layout(title=title, xaxis_title='Payload Mass (kg)', yaxis_title='Class',
                      legend=dict(title=dict(text='Booster Version Category')))
    
    return fig
# Run the app
if __name__ == '__main__':
	 # REVIEW8: Adding dev_tools_ui=False, dev_tools_props_check=False can prevent error appearing before calling callback function
	app.run_server(mode='inline', host='localhost', debug=False, dev_tools_ui=False, dev_tools_props_check=False)
