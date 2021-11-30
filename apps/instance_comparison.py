from dash import dcc
from dash import html
import plotly.express as px
from dash.dependencies import Input, Output
from app import app, dropdown, template
import sqlite3
import pandas as pd

server = app.server

metrics = ["online", "comments", "posts", "users", "communities"]
title = {'y': 0.9,
        'x': 0.5,
        'text': "Latest Values",
        'xanchor': 'center',
        'yanchor': 'top'}

css = {'width': '48%', 'display': 'inline-block'}
font = dict(family="Helvetica",
            size=12)

layout = html.Div(children=[
    dcc.Dropdown(
        id='yaxis_column',
        options=[{'label': i, 'value': i} for i in metrics],
        value='users'),
    dcc.Graph(id='combined-instances')])


@app.callback(
    Output('combined-instances', 'figure'),
    Input('yaxis_column', 'value'),
)
def update_combined_instances(yaxis_column):
    cnx = sqlite3.connect('data/lemmy.db')
    df = pd.read_sql(f"""SELECT timestamp, url, {', '.join(metrics)} 
    FROM historical
    WHERE status == 'Success'
    ORDER BY {yaxis_column} DESC""", cnx)
    df = df.query("timestamp == timestamp.max()")
    fig = px.bar(df, y="url", x=yaxis_column, color="url", orientation='h', height=len(df)*50, template=template)
    fig = fig.update_layout(font=font, showlegend=False)
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
