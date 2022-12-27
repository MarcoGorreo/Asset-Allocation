# Libraries

import pandas as pd
import yfinance as yf
import datetime
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import math 

# Settings

initial_investment = 30000
monthly_investment = 250
rebalacing_frequency = 4

allocation_name = "AW Vittorio 250M 4R"

tickers = ["IBGL.AS", "EM13.MI", "D3V3.DE", 'IBTS.AS',"IBCI.AS", "CSSPX.MI", "XCS6.DE",'SWDA.MI', "SGLD.L", "CRB.PA"]
asset_class_original_percentage = [12.5,5,5,5,7.5,10,7.5,25,10,7.5]

# Date

start_backtest = date(2012,1,1)
end_date = date(2022,12,1)

# Variables and Arrays

arrays = []
portfolio_value_array = []
dates = []

# Functions Declaration

def adjust_date(datetime):
    return str((str(datetime.year) + "-" + str(datetime.month) + "-" + str(datetime.day)))

def construct_portfolio(tickers_current_price,asset_class_original_percentage,initial_investment):

    available_liquidity = 0
    shares_owned = []
    value_of_shares = 0 

    for asset in range(len(tickers_current_price)):
        shares_for_ticker = ((initial_investment / 100) * asset_class_original_percentage[asset]) / tickers_current_price['Price'][asset]
        shares_for_ticker = int(shares_for_ticker)
        value_of_shares += (shares_for_ticker * tickers_current_price['Price'][asset])
        shares_owned.append(shares_for_ticker)

    available_liquidity = initial_investment - value_of_shares
    
    array_list = list(zip(tickers_current_price['Ticker Name'], shares_owned))
    portfolio = pd.DataFrame(array_list, columns=['Ticker Name', 'Shares Owned'])


    return[portfolio,available_liquidity]
        
def calculate_portfolio_shares_value(portfolio, tickers_current_price):
    
    portfolio_shares_value = 0

    for i in range(len(portfolio)):
        portfolio_shares_value += portfolio['Shares Owned'][i] * tickers_current_price['Price'][i]

    return portfolio_shares_value

def portfolio_rebalance(value_of_shares, available_liquidity, asset_class_original_percentage,tickers_current_price):

    portfolio_value = value_of_shares + available_liquidity
    new_available_liquidity = 0
    new_value_of_shares = 0
    shares_owned = []

    for asset in range(len(tickers_current_price)):
        shares_for_ticker = ((portfolio_value / 100) * asset_class_original_percentage[asset]) / tickers_current_price['Price'][asset]
        shares_for_ticker = int(shares_for_ticker)
        shares_owned.append(shares_for_ticker) 
        new_value_of_shares += (shares_for_ticker * float(tickers_current_price['Price'][asset])) 
    array_list = list(zip(tickers_current_price['Ticker Name'], shares_owned))
    portfolio = pd.DataFrame(array_list, columns=['Ticker Name', 'Shares Owned'])

    new_available_liquidity = portfolio_value - new_value_of_shares

    return[portfolio, new_available_liquidity]
     
# Dataframe Download 

tickers_to_download = ""

for ticker in tickers:
    tickers_to_download = tickers_to_download + ticker + " "

df = yf.download(tickers = tickers_to_download, start= adjust_date(start_backtest), end= adjust_date(end_date), interval="1mo")

# Data Check

for i in range(len(df)):
    for ticker in tickers:
        data_check = df['Adj Close'][ticker][df.index[i]]
        if math.isnan(data_check) == True:
            print(ticker, " datas are corrupted")

# Data Cleaning

df.drop('Volume', axis=1, inplace=True)
df.drop('Open', axis=1, inplace=True)
df.drop('Close', axis=1, inplace=True)

# Backtesting

for i in range(len(df)):

    tickers_price = []

    for ticker in tickers:
        tickers_price.append(round(df['Adj Close'][ticker][df.index[i]],2))

    dates.append(df.index[i])
    arrays_price = list(zip(tickers, tickers_price))
    tickers_current_price = pd.DataFrame(arrays_price, columns=["Ticker Name","Price"])
    tickers_current_price['Price'] = tickers_current_price['Price'].astype(float)

    if i == 0:
        portfolio_infos = construct_portfolio(tickers_current_price, asset_class_original_percentage, initial_investment)
        portfolio = portfolio_infos[0]
        available_liquidity = float(portfolio_infos[1])

    value_of_shares = calculate_portfolio_shares_value(portfolio,tickers_current_price)

    available_liquidity += monthly_investment

    if i%rebalacing_frequency == 0 and i != 0:
        portfolio_infos = portfolio_rebalance(value_of_shares, available_liquidity, asset_class_original_percentage, tickers_current_price)
        portfolio = portfolio_infos[0]
        available_liquidity = portfolio_infos[1]
        value_of_shares = calculate_portfolio_shares_value(portfolio,tickers_current_price)

    portfolio_value = value_of_shares + available_liquidity
    portfolio_value_array.append(portfolio_value)

list_tuples = list(zip(dates, portfolio_value_array))
portfolio_result = pd.DataFrame(list_tuples, columns=['Date', 'Value'])

plt.style.use('ggplot')
fig, ax = plt.subplots()
ax.grid(False)
ax.plot(portfolio_result['Date'],portfolio_result['Value'], color='Green')
ax.set_ylabel('Portfolio Value')
ax.set_title("Portfolio Performance")

df_save_location = "Portfolios/" + allocation_name + ".xlsx"
portfolio_result.to_excel(df_save_location, sheet_name=allocation_name) 