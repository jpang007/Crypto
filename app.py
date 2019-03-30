import dash
#responsible for setting up the app
#external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__)
server = app.server
app.config.suppress_callback_exceptions = True
