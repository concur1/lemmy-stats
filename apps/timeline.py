# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.
import os
from dash import dcc
from dash import html
import plotly.express as px
import pandas as pd
import sqlite3
from dash.dependencies import Input, Output
from app import app, dropdown, template

server = app.server

selected_urls = sqlite3.connect('data/lemmy.db').execute("""SELECT distinct url from historical""")
unique_urls = [instance[0] for instance in selected_urls]
metrics = ["online", "new_comments", "new_posts", "new_communities", "users_active_day",
           "users_active_month", "users_active_half_year"]
title = {'y': 0.9,
        'x': 0.5,
    'text': "Timeline",
    'xanchor': 'center',
    'yanchor': 'top'}
css = {'width': '48%', 'display': 'inline-block'}
font = dict(family="Helvetica",
            size=12)

layout = html.Div(children=[
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
    cnx = sqlite3.connect('data/lemmy.db')
    df = pd.read_sql(f"""SELECT timestamp, 
                                url, 
                                online, 
                                users_active_day,
                                users_active_month,
                                users_active_half_year,
                                comments-lag(comments) OVER win1 as new_comments,
                                posts-lag(posts) OVER win1 as new_posts,
                                communities-lag(communities) OVER win1 as new_communities
                        FROM historical
                        where url == '{xaxis_column_name}' and status == 'Success'
                        WINDOW win1 AS (PARTITION BY url ORDER BY datetime(timestamp))
                        order by timestamp""", cnx)
    df = df[['timestamp', metric]].sort_values('timestamp', ascending=False)
    fig = px.line(df, x="timestamp", y=metric, template=template)
    fig = fig.update_layout(font=font, title=title)
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
