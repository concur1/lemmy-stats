# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from dash import dcc
from dash import html
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output
from app import app, dropdown, template

server = app.server

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options

df = pd.read_csv("data/historical.csv", delimiter='|')
unique_urls = df['url'].unique()
metrics = ["online", "users", "posts", "comments", "communities", "users_active_day", "users_active_week", "users_active_month",
          "users_active_half_year"]
title = {'y': 0.9,
        'x': 0.5,
    'text': "Timeline",
    'xanchor': 'center',
    'yanchor': 'top'}
css = {'width': '48%', 'display': 'inline-block'}
font = dict(family="Helvetica",
            size=12)

layout = html.Div(children=[
    dropdown,
    html.Br(),
    html.Div([
        dcc.Dropdown(
            id='xaxis-column',
            options=[{'label': i, 'value': i} for i in unique_urls],
            value='https://lemmy.ml')], style=css),
    html.Div([
        dcc.Dropdown(
            id='metric',
            options=[{'label': i, 'value': i} for i in metrics],
            value='online')], style=css),
    dcc.Graph(id='each-instance'),
])


@app.callback(
    Output('each-instance', 'figure'),
    Input('xaxis-column', 'value'),
    Input('metric', 'value'),
)
def update_each_instance(xaxis_column_name, metric):
    df = pd.read_csv("data/historical.csv", delimiter='|').query(f"url == '{xaxis_column_name}'")
    df = df[['timestamp', metric]].sort_values('timestamp', ascending=False)
    fig = px.line(df, x="timestamp", y=metric, template=template)
    fig = fig.update_layout(font=font, title=title)
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
