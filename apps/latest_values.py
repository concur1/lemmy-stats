from dash import dcc
from dash import html
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output
from app import app, dropdown, template

server = app.server

df = pd.read_csv("data/historical.csv", delimiter='|')
unique_urls = df['url'].unique()
metrics = ["online", "users", "posts", "comments", "communities", "users_active_day", "users_active_week", "users_active_month",
          "users_active_half_year"]
title = {'y': 0.95,
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
    df = pd.read_csv("data/historical.csv", delimiter='|')
    df = df.sort_values(yaxis_column, ascending=False).query("timestamp == timestamp.max()")
    fig = px.bar(df, x="url", y=yaxis_column, color="url", template=template)
    fig = fig.update_layout(font=font, showlegend=False, title=title)
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
