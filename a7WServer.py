# Published at:https://render-a7.onrender.com/

import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd

#Initialize Dash 
app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server

df = pd.read_csv('WorldCupData.csv', skiprows=1)
df = df.dropna(subset=['Year'])  # Remove empty rows

#replace West Germany with Germany
df['Winners'] = df['Winners'].str.replace('West Germany', 'Germany').str.strip()
df['Runners-up'] = df['Runners-up'].str.replace('West Germany', 'Germany').str.strip()

#Convert Year to integer and clean up
df['Year'] = df['Year'].astype(int)
df['Attendance'] = df['Attendance'].str.replace('"', '').str.replace(',', '').astype(int)

win_counts = df['Winners'].value_counts().reset_index()
win_counts.columns = ['country', 'wins']

#Map country names to ISO-3 
country_iso_mapping = {
    'Uruguay': 'URY',
    'Italy': 'ITA',
    'Brazil': 'BRA',
    'Germany': 'DEU',
    'England': 'GBR',
    'Argentina': 'ARG',
    'France': 'FRA',
    'Spain': 'ESP'
}
win_counts['iso_code'] = win_counts['country'].map(country_iso_mapping)

# Create choropleth 
fig = px.choropleth(
    win_counts,
    locations="iso_code",
    locationmode="ISO-3",
    color="wins",
    color_continuous_scale="Reds",
    scope="world",
    title="World Cup Wins by Country (Red=Most Wins)"
)

#App layout remains the same
app.layout = html.Div([
    html.H1("FIFA World Cup Dashboard"),
    dcc.Graph(figure= fig),
    html.H3("All Countries That Have Won the World Cup"),
    html.Ul([html.Li(country) for country in sorted(win_counts['country'])]),
    html.H3("Select a Country to view Number of Wins that they have"),
    dcc.Dropdown(
        id='country-dropdown',
        options=[{'label': country, 'value': country} for country in win_counts['country']],
        placeholder="Select country"),
    html.Div(id='win-count-output'),
    html.H3("Select a Year to View World Cup Final Details"),
    dcc.Dropdown(
        id='year-dropdown',
        options=[{'label': year, 'value': year} for year in df['Year']],
        placeholder="Select a year"
    ),
    html.Div(id='year-details-output')
])
# Callbacks remain the same
@app.callback(
    Output('win-count-output', 'children'),
    Input('country-dropdown','value')
)
def update_win_count(selected_country):  
    if not selected_country: 
        return 'Please select a country to see the number of wins.'
    count = win_counts[win_counts['country'] == selected_country]['wins'].values[0]
    return f'{selected_country} has won the World Cup {count} times.' 

@app.callback(
    Output('year-details-output', 'children'),
    Input('year-dropdown', 'value')
)
def update_year_details(selected_year): 
    if not selected_year:
        return 'Please select a year to see the World Cup final details.'
    row = df[df['Year']== selected_year]
    if row.empty:
        return 'No data available for this year.'
    data = row.iloc[0]
    return html.Div([
        html.P(f"Winner: {data['Winners']}"),
        html.P(f"Runner-up: {data['Runners-up']}"),
        html.P(f"Score: {data['Score']}"),
        html.P(f"Venue: {data['Venue']}"),
        html.P(f"Location: {data['Location']}"),
        html.P(f"Attendance: {data['Attendance']:,}")])

#Run
if __name__ == '__main__':
    app.run(debug=True)
