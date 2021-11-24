from dash import dcc
from dash import html
import plotly.express as px
from dash.dependencies import Input, Output
from app import app, dropdown, template
import sqlite3
import pandas as pd

server = app.server

metrics = ["online", "users_active_day", "users_active_week", "users_active_month",
           "users_active_half_year"]
title = {'y': 0.9,
        'x': 0.5,
        'text': "Latest Values",
        'xanchor': 'center',
        'yanchor': 'top'}

css = {'width': '48%', 'display': 'inline-block'}
font = dict(family="Helvetica",
            size=12)

layout = html.Div(children=[
    dropdown,
    html.Br(),
    dcc.Dropdown(
        id='yaxis_column',
        options=[{'label': i, 'value': i} for i in metrics],
        value='users_active_half_year'),
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
    ORDER BY users_active_half_year""", cnx)
    df = df.query("timestamp == timestamp.max()")
    fig = px.bar(df, x="url", y=yaxis_column, color="url", template=template)
    fig = fig.update_layout(font=font, showlegend=False, title=title)
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
