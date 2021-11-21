from dash import dcc, html
from dash.dependencies import Input, Output

from app import app
from apps import latest_values, timelines

server=app.server
app.layout = html.Div([
    dcc.Location(id='url', refresh=True),
    html.Div(id='page-content')
])


@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/latest_values':
        return latest_values.layout
    elif pathname == '/timelines':
        return timelines.layout
    elif pathname in ["", "/"]:
        return latest_values.layout
    else:
        return '404'


if __name__ == '__main__':
    app.run_server(debug=True)
