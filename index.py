import sqlite3
import pandas as pd

from dash import dcc, html
from dash.dependencies import Input, Output

from app import app, dropdown
from apps import instance_comparison, timeline, latest_data


cnx = sqlite3.connect('data/lemmy.db')
df = pd.read_sql(f"""SELECT max(timestamp)
                     FROM historical""", cnx)
get_updated_timestamp = df.to_dict('list')['max(timestamp)'][0][:-4]

server = app.server
app.layout = html.Div(children=[
    dropdown,
    html.Br(),
    dcc.Location(id='url', refresh=True),
    html.Div(children=[
        dcc.Markdown(f"Last refresh: {get_updated_timestamp}"),
        html.Div(id='page-content')
    ], style={"max-width": "90%",
              "margin": "auto"})
])

homepage = html.Div([
                    dcc.Markdown('''
                    - [Click here to see how lemmy activity has changed over time](/timeline)
                    
                    - [Click here to see the latest activity for each instance](/instance_comparison)
                    ''')])


@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/instance_comparison':
        return instance_comparison.layout
    elif pathname == '/timeline':
        return timeline.layout
    elif pathname == '/latest_data':
        return latest_data.layout
    elif pathname in ["", "/"]:
        return homepage
    else:
        return '404'





layout = app.layout
if __name__ == '__main__':
    app.run_server(debug=True)
