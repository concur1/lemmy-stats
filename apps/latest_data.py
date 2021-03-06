import sqlite3
import pandas as pd
from dash import html, dash_table
from app import app

server = app.server

cnx = sqlite3.connect('data/lemmy.db')
df = pd.read_sql(f"""SELECT "["||IIF(name != "None", name, url)||"]("||url||")" as instance, 
"<a href='"||url||"'>test</a>" as instance2, 
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
        # style_table={'overflowX': 'auto', 'fontSize': '11px'},
        css=[{'selector': 'table', 'rule': 'table-layout: fixed'}],
        style_table={'font-size': '11px'},
        style_cell={
            'width': '25%',
            'textAlign': 'left'
        },
        style_header={
            'fontWeight': 'bold',
            'font-size': '12px',
        },
        style_as_list_view=True,
        id='data_table',
        columns=[{"name": i, "id": i, 'type': 'text', 'presentation': 'markdown'} for i in df.columns
                 if i in ["instance",  "comments", "posts", "users"]],
        data=df.to_dict('records'),
        tooltip_data=tooltip_data,
        tooltip_delay=0,
        tooltip_duration=None
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)
