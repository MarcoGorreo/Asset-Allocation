# Libraries -->

import numpy as np
import pandas as pd
import yfinance as yf 
import numpy as np
from matplotlib import pyplot as plt

plt.style.use('ggplot')

# Portfolios To Analyze -->

portfolios = ['All Weather Portfolio']
benchmark = 'SPY'

# Functions

def adjust_date(datetime):
    return str((str(datetime.year) + "-" + str(datetime.month) + "-" + str(datetime.day)))

def calculate_VaR(portfolio_to_analyze,years):

    for i in range(len(portfolio_to_analyze)):

        yearly_var = []

        for y in years:
            
            annual_values = []

            for k in range(len(portfolio_to_analyze)):

                if str(portfolio_to_analyze['Date'][k])[0:4] == y:
                    annual_values.append(portfolio_to_analyze['Value'][k])

            annual_value_serie = pd.Series(annual_values)
            lowest_of_year = annual_value_serie.min()
            var_for_year = lowest_of_year * 100 / annual_value_serie[0]
            yearly_var.append(round(var_for_year - 100,2))

    total_yearly_performance_serie = pd.Series(yearly_var)
    portfolio_var = round(float(total_yearly_performance_serie.min()),2)

    return[portfolio_var, yearly_var]

def calculate_average_return(portfolio_to_analyze,years):
    
    portfolio_return = round((portfolio_to_analyze['Value'][len(portfolio_to_analyze)-1] * 100) / portfolio_to_analyze['Value'][0],2)
    
    return (portfolio_return/len(years))

# Arrays 

sharpe_ratios = []
var_list = []
portoflio_value_list = []
final_returns = []
dates_list = []
average_returns = []

# Script -->

# Risk Free

risk_free_datas = pd.read_excel("Risk-Free Rate.xls")
risk_free_datas_serie = pd.Series(risk_free_datas['VALUE'])
average_risk_free = round(float(risk_free_datas_serie.mean()),3)

# Portfolio Analysis

for portfolio in range(len(portfolios)):

    years = []
    months = []

    directory = "Portfolios/" + portfolios[portfolio] + ".xlsx"
    portfolio_to_analyze = pd.read_excel(directory, index_col=[0])

    for i in range(len(portfolio_to_analyze)):
        year = str(portfolio_to_analyze['Date'][i])[0:4]
        if str(portfolio_to_analyze['Date'][i])[0:4] not in years:
            years.append(year)
    
    for i in range(1,len(portfolio_to_analyze)):
        months.append(portfolio_to_analyze['Date'][i])

    dates_list.append(months)

    # VaR

    var_infos = calculate_VaR(portfolio_to_analyze,years)
    total_portfolio_var = var_infos[0]
    var_for_year = var_infos[1]
    var_list.append(total_portfolio_var)

    # Standard Deviation

    portfolio_value_serie = pd.Series(portfolio_to_analyze["Value"])
    portfolio_percentage_changes = portfolio_value_serie.pct_change()
    portfolio_standard_deviation = portfolio_percentage_changes.std() * 100

    portfolio_value = 100 
    portfolio_value_history = []

    for value_change in range(1,len(portfolio_percentage_changes)):
        portfolio_value += (portfolio_value * portfolio_percentage_changes[value_change])
        portfolio_value_history.append(float(portfolio_value))

    portoflio_value_list.append(portfolio_value_history)

    # Calculate Return 

    average_annual_return = calculate_average_return(portfolio_to_analyze, years)
    
    # Sharpe Ratio

    sharpe_ratio = (average_annual_return - average_risk_free) / portfolio_standard_deviation
    sharpe_ratios.append(float(round(sharpe_ratio,2)))

    # Final Return 
 
    final_return = (portfolio_to_analyze['Value'][len(portfolio_to_analyze)-1] * 100 / portfolio_to_analyze['Value'][0]) - 100
    final_returns.append(round(final_return,2))

    # Average Return

    average_return = float(final_return / (len(years)))
    average_returns.append(round(average_return,2))

    # Get Tickers

    second_directory = "Portfolios/" + portfolios[portfolio] + " tickers" + ".xlsx"
    ticker_df = pd.read_excel(second_directory)

# Final Dataframe 

list_tuples = list(zip(portfolios,sharpe_ratios,var_list,final_returns,average_returns, portoflio_value_list,dates_list))
portfolio_analysis = pd.DataFrame(list_tuples,columns=['Portfolio Name','Sharpe Ratio','VaR',"Final Return",'Average Return','Portfolio History','Dates'])

# Find Oldest Data

dates_max = []
dates_min = []

for i in range(len(dates_list)):
    dates_list_series = pd.Series(dates_list[i])
    dates_min.append(dates_list_series.min())
    dates_max.append(dates_list_series.max())

dates_min_series = pd.Series(dates_min)
dates_max_series = pd.Series(dates_max)

oldest_data = dates_min_series.min()
latest_data = dates_max_series.max()

# Download Benchmark Data

benchmark_df = yf.download(benchmark, start= adjust_date(oldest_data), end= adjust_date(latest_data), interval="1mo")
benchmark_series = pd.Series(benchmark_df['Adj Close'])
benchmark_dates = list(benchmark_df.index)
benchmark_dates.pop(0)
benchmark_pct_change = benchmark_series.pct_change()

benchmark_value = 100 
benchmark_value_history = []

for value_change in range(1,len(benchmark_pct_change)):
    benchmark_value += (benchmark_value * benchmark_pct_change[value_change])
    benchmark_value_history.append(float(benchmark_value))

# Graph Plot -->

for portfolio in range(len(portfolio_analysis)):
    label = str(portfolio_analysis['Portfolio Name'][portfolio] + " - Sharpe Ratio: " + str(portfolio_analysis['Sharpe Ratio'][portfolio]) + ' - VaR: ' + str(portfolio_analysis['VaR'][portfolio]) + ' - Avg Return: ' + str(portfolio_analysis['Average Return'][portfolio]) + "%")
    plt.plot(portfolio_analysis['Dates'][portfolio],portfolio_analysis['Portfolio History'][portfolio], label=label)

# Benchmark Plot

benchmark_years = []

for i in range(len(benchmark_dates)):
    year = str(benchmark_dates[i])[0:4]
    if str(benchmark_dates[i])[0:4] not in benchmark_years:
        benchmark_years.append(year)

average_benchmark_performance = round((benchmark_value_history[len(benchmark_value_history) - 1] - 100)/ (len(benchmark_years)),2)
benchmark_label = benchmark + " benchmark performance - Average Performance: " + str(average_benchmark_performance) + "%"
plt.plot(benchmark_dates, benchmark_value_history, linestyle="--" ,color = 'grey', label=benchmark_label)

# Plot Settings

plt.grid(alpha = 0)
plt.xlabel('Date')
plt.ylabel('Performance %')
plt.legend()
plt.rcParams["figure.figsize"] = (18,12)
plt.show()

# Pie Chart Plot

plt.pie(ticker_df['% Allocation'],labels = ticker_df['Ticker'])
plt.show()



