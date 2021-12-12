from dash import dcc
from dash import html
import plotly.express as px
import pandas as pd
import sqlite3
from dash.dependencies import Input, Output
from app import app, template

server = app.server
time_unit_list = ['hour', 'day', 'month']
strftime_dict = {'hour': '%Y-%m-%d %H:00', 'day': '%Y-%m-%d', 'month': '%Y-%m'}

selected_urls = sqlite3.connect('data/lemmy.db').execute("""SELECT distinct url from historical
                                                            where status = "Success"
                                                            order by users DESC""")
unique_urls = ['all instances'] + [instance[0] for instance in selected_urls]
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
                        select time,
                               url,
                               name,
                               avg(online) as 'average online',
                               sum(new_comments) as 'new comments/{time_unit}',
                               sum(new_posts) as 'new posts/{time_unit}',
                               sum(users) as 'new users/{time_unit}',
                               sum(new_communities) as 'new communities/{time_unit}'
                        from (SELECT timestamp, 
                                     STRFTIME('{strftime_string}', timestamp) as 'time',
                                     url, 
                                     name,
                                     online, 
                                     comments-lag(comments) OVER win1 as new_comments,
                                     posts-lag(posts) OVER win1 as new_posts,
                                     users-lag(users) OVER win1 as users,
                                     communities-lag(communities) OVER win1 as new_communities
                               FROM historical
                        where status == 'Success' and not (comments == 0 and posts = 0 and users = 0 and communities = 0)
                        WINDOW win1 AS (PARTITION BY url ORDER BY datetime(timestamp)))
                        group by time, url
                        having time>(select min(STRFTIME('{strftime_string}', timestamp)) from historical)
                               and time < (select max(STRFTIME('{strftime_string}', timestamp)) from historical)
                        """, cnx)

    all_instances = df.copy(deep=True).query('url != "https://sopuli.xyz"')\
        .assign(name='all instances', url='all instances')\
        .groupby(['time', 'url'], as_index=False)\
        .sum()
    df = df.append(all_instances, ignore_index=True).query(f"""url in ({', '.join([f'"{url}"' for url in instance_url])})""")
    fig = px.line(df, x="time", y=y_axis_name, template=template, color='url')
    fig = fig.update_layout(font=font, title=title, showlegend=False, margin=dict(l=0, r=0))
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
