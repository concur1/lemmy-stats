import dash
import dash_bootstrap_components as dbc

template = "plotly"
app = dash.Dash(__name__,
                meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
                external_stylesheets=[dbc.themes.BOOTSTRAP],
                suppress_callback_exceptions=True)

server = app.server

dropdown = dbc.NavbarSimple(
            children=[
                dbc.NavItem(dbc.NavLink("Latest Data", href="/latest_data")),
                dbc.NavItem(dbc.NavLink("Latest Values", href="/latest_values")),
                dbc.NavItem(dbc.NavLink("Timeline", href="/timeline"))],
            brand="Lemmy-Stats",
            brand_href="/",
            color="darkblue",
            dark=True)
