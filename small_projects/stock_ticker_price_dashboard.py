import pandas

dataframe = pandas.read_csv("Nasdaq.csv")

print(dataframe)

dataframe.head()

dataframe.info()

dataframe.describe()

!pip install jupyter-dash
!pip install dash

from jupyter_dash import JupyterDash

import dash

import dash_html_components as html

import dash_core_components as dcc

from datetime import datetime

app = JupyterDash(__name__)

options = []

for element in dataframe.index:

  options.append({"label": dataframe["Name"][element],
                  "value": dataframe["Symbol"][element]
                  })

app.layout = html.Div([
                       html.H1("Stock Ticker Web App"),
                       html.Div([
                                 html.H2("Select a stock:"),
                                 dcc.Dropdown(
                                     id = "dropdown",
                                     options = options,
                                     value = ["GOOG"],
                                     multi = True
                                 )
                       ]),
                       html.Div([
                                 html.H2("Select Date"),
                                 dcc.DatePickerRange(
                                     id = "datepicker",
                                     min_date_allowed = datetime(2017, 
                                                                 1, 
                                                                 1),
                                     max_date_allowed = datetime.today(),
                                     start_date = datetime(2020, 1, 1),
                                     end_date = datetime.today()
                                 )
                       ]),
                       html.Div([
                                 html.Button(
                                     id = "submit-button",
                                     n_clicks = 0,
                                     children = "Submit"
                                 )
                       ]),
                       dcc.Graph(
                           id = "stock-graph"
                       )
])

from dash.dependencies import Output, Input, State

import pandas

from pandas_datareader import DataReader

@app.callback(Output("stock-graph", "figure"),
              [Input("submit-button", "n_clicks")],
              [State("dropdown", "value"),
               State("datepicker", "start_date"),
               State("datepicker", "end_date")]
              )
def update_graph(number_of_clicks, stocks, start_date, end_date):

  start = datetime.strptime(start_date[:10], "%Y-%m-%d")

  end   = datetime.strptime(end_date[:10], "%Y-%m-%d")

  data = []

  for stock in stocks:

    dataframe = DataReader(stock, "yahoo", start, end)

    dates = []

    for row in range(len(dataframe)):

      new_date = str(dataframe.index[row])

      new_date = new_date[0:10]

      dates.append(new_date)

    dataframe["Date"] = dates

    data.append({
        "x": dataframe["Date"],
        "y": dataframe["Adj Close"],
        "name": stock
    })

  figure = {
      "data": data,
      "layout": { 
          "title": "Stock Data"
      }
  }

  return figure

app.run_server(port = 3030)