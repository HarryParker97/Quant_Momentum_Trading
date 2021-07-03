import numpy as np
import pandas as pd
import requests
import math
from scipy.stats import percentileofscore as score
import xlsxwriter
import os
print(os.getcwd())

stocks = pd.read_csv('sp_500_stocks.csv')
from secrets import IEX_CLOUD_API_TOKEN

# symbol = 'AAPL'
# api_url = f'https://sandbox.iexapis.com/stable/stock/{symbol}/stats?token={IEX_CLOUD_API_TOKEN}'
# data = requests.get(api_url).json()

# Parsing Our API Call
# data['year1ChangePercent']

def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i: i+n]

# This will create 6 lists, with 100 stocks, seperated by commas
symbol_groups = list(chunks(stocks['Ticker'],100)) # 100 is the maximum batch API call
symbol_strings = []
for i in range(0, len(symbol_groups)):
    symbol_strings.append(','.join(symbol_groups[i]))

my_columns = ['Ticker', 'Price', 'One-Year Price Return', 'Number of Shares to Buy']

final_df = pd.DataFrame(columns = my_columns)
for symbol_string in symbol_strings:
    batch_api_call_url = f'https://sandbox.iexapis.com/stable/stock/market/batch?types=price,stats,quote&symbols={symbol_string}&token={IEX_CLOUD_API_TOKEN}'
    data = requests.get(batch_api_call_url).json()
    for symbol in symbol_string.split(','):  # This will give the ticker for each stock
        final_df = final_df.append(
            pd.Series(
                [
                    symbol,
                    data[symbol]['price'],
                    data[symbol]['stats']['year1ChangePercent'],
                    'N/A'
                ],
                index=my_columns),
            ignore_index=True
            )
# print(final_df)

# Sort rows based on one year price return
# Highest momentum at the top
final_df.sort_values('One-Year Price Return', ascending=False, inplace=True)
final_df = final_df[:50]
final_df.reset_index(inplace=True)
# print(final_df)

# Now we calculate the number of share to buy!
def portfolio_input():
    global portfolio_size
    portfolio_size = input('Enter the size of your portfolio:')

    try:
        float(portfolio_size)
    except:
        print('This is not a number /nPlease try again: ')
        portfolio_size = input('Enter the size of your portfolio:')

portfolio_input()
print(portfolio_size)

# calucate postion size
position_size = float(portfolio_size)/len(final_df.index)
for i in range(0, len(final_df)):
    final_df.loc[i, 'Number of Shares to Buy'] = position_size/final_df.loc[i, 'Price']

# print(final_df)

# Now we are going to build a high quality quant strategy
# Will build strategy for 1m, 3m, 6m 1y price returns

hqm_columns = [
    'Ticker',
    'Price',
    'Number of Shares to Buy',
    '1y Price Return',
    '1y Return Percentile',
    '6m Price Return',
    '6m Return Percentile',
    '3m Price Return',
    '3m Return Percentile',
    '1m Price Return',
    '1m Return Percentile',
    'HQM Score',
]
hqm_df = pd.DataFrame(columns=hqm_columns)

for symbol_string in symbol_strings:
    batch_api_call_url = f'https://sandbox.iexapis.com/stable/stock/market/batch?types=price,stats,quote&symbols={symbol_string}&token={IEX_CLOUD_API_TOKEN}'
    data = requests.get(batch_api_call_url).json()
    for symbol in symbol_string.split(','):
        hqm_df = hqm_df.append(
            pd.Series(
                [
                    symbol,
                    data[symbol]['price'],
                    'N/A',
                    data[symbol]['stats']['year1ChangePercent'],
                    'N/A',
                    data[symbol]['stats']['month6ChangePercent'],
                    'N/A',
                    data[symbol]['stats']['month3ChangePercent'],
                    'N/A',
                    data[symbol]['stats']['month1ChangePercent'],
                    'N/A',
                    'N/A',
                ],
                index=hqm_columns),
            ignore_index=True
        )
# print(hqm_df)

# Here we calculate the momentum percentile
time_periods = [
    '1y',
    '6m',
    '3m',
    '1m'
]
for row in hqm_df.index:
    for time_period in time_periods:
        change_col = f'{time_period} Price Return'
        percentile_col = f'{time_period} Return Percentile'
        hqm_df.loc[row, f'{time_period} Return Percentile'] = score(hqm_df[change_col], hqm_df.loc[row, change_col])/100

print(hqm_df)

# Calculating HQM score
from statistics import mean

for row in hqm_df.index:
    momentum_percentile = []
    for time_period in time_periods:
        momentum_percentile.append(hqm_df.loc[row, f'{time_period} Return Percentile'])
    hqm_df.loc[row, 'HQM Score'] = mean(momentum_percentile)

# Selecting the 50 Best Momentum Stocks
hqm_df.sort_values('HQM Score', ascending=False, inplace=True)
hqm_df = hqm_df[:50]
hqm_df.reset_index(inplace=True, drop=True)

position_size = float(portfolio_size)/len(hqm_df.index)
for i in hqm_df.index:
    hqm_df.loc[i, 'Number of Shares to Buy'] = math.floor(position_size/hqm_df.loc[i, 'Price'])

print(hqm_df)
hqm_df.to_csv('Data_test.csv')