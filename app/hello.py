# Run this app with `python hello.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
from dash import dcc
from dash import html
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output
import flask
server = flask.Flask(__name__)
app = dash.Dash(__name__, server=server)

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options

df = pd.read_csv("../data/historical.csv", delimiter='|')
unique_urls = df['url'].unique()
metrics = ["online", "users", "posts", "comments", "communities", "users_active_day", "users_active_week", "users_active_month",
          "users_active_half_year"]
template = "seaborn"


app.layout = html.Div(children=[
    html.H1(children='Lemmy Stats'),
    dcc.Dropdown(
        id='yaxis_column',
        options=[{'label': i, 'value': i} for i in metrics],
        value='online'),
    dcc.Graph(id='combined-instances'),
    html.Div([
    dcc.Dropdown(
        id='xaxis-column',
        options=[{'label': i, 'value': i} for i in unique_urls],
        value='https://lemmy.ml')], style={'width': '48%', 'display': 'inline-block'}),
    html.Div([
    dcc.Dropdown(
        id='metric',
        options=[{'label': i, 'value': i} for i in metrics],
        value='online')], style={'width': '48%', 'display': 'inline-block'}),
    dcc.Graph(id='each-instance'),

])
@app.callback(
    Output('combined-instances', 'figure'),
    Input('yaxis_column', 'value'),
)
def update_combined_instances(yaxis_column):
    df = pd.read_csv("../data/historical.csv", delimiter='|')
    df = df.sort_values(yaxis_column, ascending=False).query("timestamp == timestamp.max()")
    fig = px.bar(df, x="url", y=yaxis_column, color="url", template=template)
    return fig

@app.callback(
    Output('each-instance', 'figure'),
    Input('xaxis-column', 'value'),
    Input('metric', 'value'),
)
def update_each_instance(xaxis_column_name, metric):
    df = pd.read_csv("../data/historical.csv", delimiter='|').query(f"url == '{xaxis_column_name}'")
    df = df[['timestamp', metric]].sort_values('timestamp', ascending=False)
    fig = px.line(df, x="timestamp", y=metric, template=template)
    return fig


@server.route('/hello')
def hello():
    return 'Hello, World!'
