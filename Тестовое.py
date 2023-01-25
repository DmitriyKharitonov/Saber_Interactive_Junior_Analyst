import requests
import pandas as pd
import re
import datetime
import time as tm
import dash
from dash import Dash, dcc,html, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px


url_asstes = 'https://api.coincap.io/v2/assets'
respons_asstes = requests.get(url_asstes)
currency = re.findall( r'"id":"(.*?)",', respons_asstes.text)

fig = px.bar()


date_from_input = html.Div([
	html.Div('Date From (DD.MM.YYYY)'),
    dcc.Input(
    	id = 'DateFrom',
	    type = 'text',
	    debounce = True,
	    style = {'width' : '150px'}
	    )
	])
	
date_to_input = html.Div([
	html.Div('Date To (DD.MM.YYYY)'),
    dcc.Input(
    	id = 'DateTo',
	    type = 'text',
	    debounce = True,
	    style = {'width' : '150px'}
	    )
	])

currency_dropdown = html.Div([
	html.Div('Select currency'),
    dcc.Dropdown(currency, id='assets_dropdown', style = {
    		'width' : '300px'
    	})
	])

graph = html.Div([
	dcc.Graph(id = 'value_graph', figure = fig, style = {
	    	'height' : '600px'
    	})
	])

app = dash.Dash(external_stylesheets = [dbc.themes.BOOTSTRAP])
app.layout = html.Div([
	dbc.Row([
		dbc.Col([
				dbc.Row(currency_dropdown, style = {'margin-top' : '130px', 'margin-left' : '30px'}),
				dbc.Row([
						dbc.Col(date_from_input, style = {'margin-top' : '20px', 'margin-left' : '10px'}),
						dbc.Col(date_to_input, style = {'margin-top' : '20px', 'margin-left' : '10px'})
					])
			], width = 3),
		dbc.Col(graph, width = 8)])
	])

@app.callback(
	Output('value_graph', 'figure'),
    [Input('assets_dropdown', 'value'),
    Input('DateFrom', 'value'),
    Input('DateTo', 'value')]
)
def get_new_graph(curency,date_from_value,date_to_value):

	date_from = datetime.datetime.strptime(date_from_value, "%d.%m.%Y").date()
	date_from_unix = (tm.mktime(date_from.timetuple()))*1000

	date_to = datetime.datetime.strptime(date_to_value, "%d.%m.%Y").date()
	date_to_unix = (tm.mktime(date_to.timetuple()))*1000

	url = f'https://api.coincap.io/v2/assets/{curency}/history?interval=d1&start={date_from_unix}&end={date_to_unix}'
	full_respons = requests.get(url)

	price_history = re.findall( r'"priceUsd":"(.*?)",', full_respons.text)

	price_history_final = []
	for price in price_history:
		price_history_final.append(round(float(price),2))

	times = re.findall( r'"time":(.*?),', full_respons.text)
	time_final = []
	for time in times:
		time_final.append(datetime.datetime.fromtimestamp(int(time)/1000).date())

	df = pd.DataFrame({'price': price_history_final, 'time' : time_final})
	fig = px.bar(df, x = 'time', y = 'price')
	return fig


if __name__ == '__main__':
    app.run_server(debug=False)