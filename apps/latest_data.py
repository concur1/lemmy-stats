import sqlite3
import pandas as pd
from dash import html, dash_table
from app import app

server = app.server

cnx = sqlite3.connect('data/lemmy.db')
df = pd.read_sql(f"""SELECT "["||IIF(name != "None", name, url)||"]("||url||")" as instance, 
                    comments,
                    users, 
                    posts, 
                    communities,
                    status,
                    description,
                    name
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
            if row['description'] == "None":
                description = "No Description"
            else:
                description = row['description']
            row_tooltip_markdown = f"\n {row['name']}: {description}"
        else:
            row_tooltip_markdown = f"\n {row['status']}"
        row_dict[column] = {'value': row_tooltip_markdown, 'type': 'markdown'}
    tooltip_data.append(row_dict)

layout = html.Div(children=[
    dash_table.DataTable(
        id='data_table',
        columns=[{"name": i, "id": i, 'type': 'text', 'presentation': 'markdown'} for i in df.columns
                 if i in ["instance",  "comments", "posts", "users", "communities"]],
        data=df.to_dict('records'),
        tooltip_data=tooltip_data,
        tooltip_delay=0,
        tooltip_duration=None
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)
