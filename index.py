from dash import dcc, html
from dash.dependencies import Input, Output

from app import app, dropdown
from apps import latest_values, timeline, latest_data

server=app.server
app.layout = html.Div(children=[
    dropdown,
    html.Br(),
    dcc.Location(id='url', refresh=True),
    html.Div(id='page-content',
             style={"max-width": "90%",
                    "margin": "auto"}),
])

homepage = html.Div([
                    dcc.Markdown('''
                    - [Click here to see how lemmy activity has changed over time](/timeline)
                    
                    - [Click here to see the latest activity for each instance](/latest_values)
                    ''')])


@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/latest_values':
        return latest_values.layout
    elif pathname == '/timeline':
        return timeline.layout
    elif pathname == '/latest_data':
        return latest_data.layout
    elif pathname in ["", "/"]:
        return homepage
    else:
        return '404'


if __name__ == '__main__':
    app.run_server(debug=True)
