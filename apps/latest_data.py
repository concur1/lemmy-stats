from IPython.core.display import display, HTML
import sqlite3
import pandas as pd
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
from collections import OrderedDict
from app import app, dropdown
from apps import latest_values, timeline

server = app.server

cnx = sqlite3.connect('data/lemmy.db')
df = pd.read_sql(f"""SELECT "["||IIF(name != "None", name, url)||"]("||url||")" as instance, *
                    FROM historical
                    GROUP BY url
                    HAVING timestamp = max(timestamp)
                    ORDER BY status DESC, users DESC
                    """, cnx)

tooltip_data = []
for row in df.to_dict('records'):
    row_dict = {}
    for column, value in row.items():
        if row['status'] == "Success":
            row_tooltip_markdown = f"\n {row['name']}: {row['description']}"
        else:
            row_tooltip_markdown = f"\n {row['status']}"
        row_dict[column] = {'value': row_tooltip_markdown, 'type': 'markdown'}
    tooltip_data.append(row_dict)

layout = html.Div(children=[
    dash_table.DataTable(
        id='data_table',
        columns=[{"name": i, "id": i,'type':'text','presentation':'markdown'} for i in df.columns if i in ["instance", "version", "online", "users", "posts", "communities"]],
        data=df.to_dict('records'),
        tooltip_data=tooltip_data,
        tooltip_delay=0,
        tooltip_duration=None
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)
