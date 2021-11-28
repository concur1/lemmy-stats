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
time_unit_list = ['hour', 'day', 'month']
strftime_dict = {'hour': '%Y-%m-%d %H:00', 'day': '%Y-%m-%d', 'month': '%Y-%m'}

selected_urls = sqlite3.connect('data/lemmy.db').execute("""SELECT distinct url from historical
                                                            where status = "Success"
                                                            order by users DESC""")
unique_urls = [instance[0] for instance in selected_urls]
metrics = ["average online", "comments", "posts", "users", "communities"]
title = {'y': 0.9,
        'x': 0.5,
    'text': "Timeline",
    'xanchor': 'center',
    'yanchor': 'top'}
css = {'width': '50%', 'display': 'inline-block'}
font = dict(family="Helvetica",
            size=12)

layout = html.Div(children=[
    html.Div([
        dcc.Dropdown(
            id='time-unit',
            options=[{'label': i, 'value': i} for i in time_unit_list],
            value='hour')], style=css),
    html.Div([
        dcc.Dropdown(
            id='metric',
            options=[{'label': i, 'value': i} for i in metrics],
            value='average online')], style=css),
    html.Div([
        dcc.Dropdown(
            id='instance-url',
            multi=True,
            options=[{'label': i, 'value': i} for i in unique_urls],
            value=[unique_urls[0]])]),
    dcc.Graph(id='each-instance'),
])


@app.callback(
    Output('each-instance', 'figure'),
    Input('time-unit', 'value'),
    Input('instance-url', 'value'),
    Input('metric', 'value'),
)
def update_each_instance(time_unit, instance_url, metric):
    strftime_string = strftime_dict[time_unit]
    if metric == "average online":
        y_axis_name = "average online"
    else:
        y_axis_name = f"new {metric}/{time_unit}"
    cnx = sqlite3.connect('data/lemmy.db')
    df = pd.read_sql(f"""
                    select STRFTIME('{strftime_string}', timestamp) as 'time',
                    url,
                    avg(online) as 'average online',
                    sum(new_comments) as 'new comments/{time_unit}',
                    sum(new_posts) as 'new posts/{time_unit}',
                    sum(users) as 'new users/{time_unit}',
                    sum(new_communities) as 'new communities/{time_unit}'
                    from (SELECT timestamp, 
                            url, 
                            online, 
                            comments-lag(comments) OVER win1 as new_comments,
                            posts-lag(posts) OVER win1 as new_posts,
                            users-lag(users) OVER win1 as users,
                            communities-lag(communities) OVER win1 as new_communities
                    FROM historical
                    where url in ({', '.join([f'"{url}"' for url in instance_url])}) and status == 'Success'
                    WINDOW win1 AS (PARTITION BY url ORDER BY datetime(timestamp)))
                    group by time, url
                        """, cnx)
    fig = px.bar(df, x="time", y=y_axis_name, template=template, color='url')
    fig = fig.update_layout(font=font, title=title)
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
