import pandas
import numpy
import requests
import math
from scipy import stats
from statistics import mean


composite_columns = [
                     "Ticker",
                     "Price",
                     "Shares to Buy",
                     "Price-to-Earnings Ratio",
                     "Price-to-Earnings Percentile",
                     "Price-to-Book Ratio",
                     "Price-to-Book Percentile",
                     "Price-to-Sales Ratio",
                     "Price-to-Sales Percentile",
                     "EV/EBITDA",
                     "EV/EBITDA Percentile",
                     "EV/Gross Profit",
                     "EV/Gross Profit Percentile",
                     "Robust Value Score"
]

composite_dataframe = pandas.DataFrame(columns = composite_columns)

tables = pandas.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")

stocks_table = tables[0]

IEX_CLOUD_API_TOKEN = "TOKEN"

def split_list(list, number_per_group):

  for index in range(0, len(list), number_per_group):

    yield list[index:index + number_per_group]

NUMBER_OF_STOCKS_PER_GROUP = 100

stock_symbols_groups = list(split_list(stocks_table["Symbol"], 
                                       NUMBER_OF_STOCKS_PER_GROUP))

print(stock_symbols_groups)

stock_symbols_strings = []

for index in range(0, len(stock_symbols_groups)):

  stock_symbols_strings.append(",".join(stock_symbols_groups[index]))

for symbol_string in stock_symbols_strings:

  batch_api_call_url = f"https://sandbox.iexapis.com/stable/stock/market/batch?symbols={symbol_string}&types=quote,advanced-stats&token={IEX_CLOUD_API_TOKEN}"

  data = requests.get(batch_api_call_url).json()

  for symbol in symbol_string.split(","):

    enterprise_value = data[symbol]["advanced-stats"]["enterpriseValue"]

    ebitda = data[symbol]["advanced-stats"]["EBITDA"]

    gross_profit = data[symbol]["advanced-stats"]["grossProfit"]

    try:

      ev_over_ebitda = enterprise_value / ebitda

    except TypeError:

      ev_over_ebitda = numpy.NaN

    try:

      ev_over_gross_profit = enterprise_value / gross_profit

    except TypeError:

      ev_over_gross_profit = numpy.NaN

    composite_dataframe = composite_dataframe.append(pandas.Series([symbol,
                                                                    data[symbol]["quote"]["latestPrice"],
                                                                    "N/A",
                                                                    data[symbol]["quote"]["peRatio"],
                                                                    "N/A",
                                                                    data[symbol]["advanced-stats"]["priceToBook"],
                                                                    "N/A",
                                                                    data[symbol]["advanced-stats"]["priceToSales"],
                                                                    "N/A",
                                                                    ev_over_ebitda,
                                                                    "N/A",
                                                                    ev_over_gross_profit,
                                                                    "N/A",
                                                                    "N/A"], 
                                                                   index = composite_columns),
                                                     ignore_index = True)

composite_dataframe[composite_dataframe.isnull().any(axis = 1)]

for column in ["Price-to-Earnings Ratio", 
               "Price-to-Book Ratio", 
               "Price-to-Sales Ratio",
               "EV/EBITDA",
               "EV/Gross Profit"]:

  composite_dataframe[column].fillna(composite_dataframe[column].mean(), inplace = True)

composite_dataframe[composite_dataframe.isnull().any(axis = 1)]

ratios_and_percentiles = {
    "Price-to-Earnings Ratio": "Price-to-Earnings Percentile",
    "Price-to-Book Ratio":     "Price-to-Book Percentile",
    "Price-to-Sales Ratio":    "Price-to-Sales Percentile",
    "EV/EBITDA":               "EV/EBITDA Percentile",
    "EV/Gross Profit":         "EV/Gross Profit Percentile"
}

for row in composite_dataframe.index:

  for ratio in ratios_and_percentiles.keys():

    composite_dataframe.loc[row, ratios_and_percentiles[ratio]] = stats.percentileofscore(composite_dataframe[ratio],
                                                                                          composite_dataframe.loc[row,
                                                                                                                  ratio])

for row in composite_dataframe.index:

  percentiles = []

  for ratio in ratios_and_percentiles.keys():

    percentiles.append(composite_dataframe.loc[row,
                                               ratios_and_percentiles[ratio]])
    
  composite_dataframe.loc[row,
                          "Robust Value Score"] = mean(percentiles)

composite_dataframe.sort_values(by = "Robust Value Score",
                                inplace = True)

composite_dataframe = composite_dataframe[:50]

composite_dataframe.reset_index(drop = True, inplace = True)

def get_portfolio_value():

  global portfolio_value

  portfolio_value = input("Enter portfolio value: ")

  try: 

    portfolio_value_float = float(portfolio_value)

  except ValueError:

    print("Not a number")

    portfolio_value = input("Enter portfolio value: ")

get_portfolio_value()

position_size = float(portfolio_value) / len(composite_dataframe.index)

for row in range(0, len(composite_dataframe["Ticker"]) - 1):

  composite_dataframe.loc[row,
                          "Shares to Buy"] = math.floor(position_size / composite_dataframe["Price"][row])

composite_dataframe