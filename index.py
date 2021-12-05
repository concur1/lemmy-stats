import sqlite3
import pandas as pd

from dash import dcc, html
from dash.dependencies import Input, Output

from app import app, dropdown
from apps import instance_comparison, timeline, latest_data


@app.callback(Output('refresh-div', 'children'), [Input('interval', 'n_intervals')])
def trigger_by_modify(n):
    cnx = sqlite3.connect('data/lemmy.db')
    df = pd.read_sql(f"""SELECT max(timestamp)
                         FROM historical""", cnx)
    timestamp = df.to_dict('list')['max(timestamp)'][0][:-4]
    return html.Div([html.H6(f"Latest Data: {timestamp}")], style={"margin": "auto",
                                                                   "max-width": "90%",
                                                                   "text-align": "centre"})


server = app.server
app.layout = html.Div(children=[
    dropdown,
    html.Br(),
    html.Div(id='refresh-div'),
    dcc.Location(id='url', refresh=True),
        html.Div(id='page-content',
                 style={"max-width": "90%",
                        "margin": "auto"}),
    dcc.Interval(id='interval', interval=60000, n_intervals=0)
])
with open("readme.md", "r") as readme:
    readme_str = readme.read()
homepage = html.Div([dcc.Markdown(readme_str)])


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
