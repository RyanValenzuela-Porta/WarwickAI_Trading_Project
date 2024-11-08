import yfinance as yf
import numpy as np
import pandas as pd
import pytz

#defining starting date for analysis
start = '2023-01-01'

#Reading list of all S&P companies from wikipedia, creates data frame 'overall'
overall = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]

#Extracting symbols (eg AAPL for apple) from the data set
stocks = overall.Symbol

#changes to list for yfinance, yf needs it as a list
stocks = stocks.to_list()

#filter the dataset to be after the start date. The others are not relevant
overall = overall[overall['Date added'] >= start]

#download stock prices for all symbols, including removed symbols
df = yf.download(stocks, start=start)['Close']

#Transform the stock price index to UTC timezone
df.index = df.index.tz_convert('UTC')

#calculates daily returns, relative daily price changes
ret_df = df.pct_change()

#Using returns to cumulate them on a monthly base (monthly returns)
mtl_ret = (ret_df + 1).resample('ME').prod()

#Using returns to cumulate them on a weekly base (weekly returns)
wkl_ret = (ret_df + 1).resample('W').prod()

#rolling over weekly return data frame for 4 weeks, and applying product function (np.prod), dropping nan values
wkl_4 = wkl_ret.rolling(4).apply(np.prod).dropna()

#rolling over monthly return data frame for 12 months, and applying product function (np.prod), dropping nan values (null) in the first 11 rows, as its once every 12
mtl_12 = mtl_ret.rolling(12).apply(np.prod).dropna()

#Function doing the above steps with a date as a parameter. Always pass portfolio formation date. The returned profit is the profit for the subsequent month
def monthly_top_performers(date):
    all_ = mtl_12.loc[date]
    top = all_.nlargest(5)
    relevant_ret = mtl_ret[top.name:][1:2][top.index]
    return (relevant_ret).mean(axis=1).values[0]

def weekly_top_performers(date):
    all_ = wkl_4.loc[date]
    top = all_.nlargest(5)
    relevant_ret = wkl_ret[top.name:][1:2][top.index]
    return (relevant_ret).mean(axis=1).values[0]

# Get the current date and make it timezone-aware
current_date = pd.Timestamp.now(tz=pytz.UTC).floor('D')

# Check if mtl_12 is empty
if mtl_12.empty:
    print("No data available for monthly analysis. Try adjusting the start date.")
else:
 
    # Find the most recent date in mtl_12 that's not in the future
    latest_available_date_monthly = mtl_12.index[mtl_12.index <= current_date].max()
    
    # Get top performers for the current month
    current_top_performers_monthly = mtl_12.loc[latest_available_date_monthly].nlargest(5)

    print("Top performers for the current month to be invested in:")
    print(current_top_performers_monthly)

    # Get latest stock prices for top monthly performers
    monthly_prices = []  # New list to store prices
    print("\nLatest stock prices for top monthly performers:")

    for ticker in current_top_performers_monthly.index:
        try:
            history = yf.Ticker(ticker).history(period="1d")
            if not history.empty:
                latest_price = history['Close'].iloc[-1]
                monthly_prices.append(latest_price)  # Add price to the list
                print(f"{ticker}: ${latest_price:.2f}")
            else:
                print(f"No recent data available for {ticker}")
        except Exception as e:
            print(f"Error fetching data for {ticker}: {str(e)}")

    if monthly_prices:
        print('Total:')
        print(f"${sum(monthly_prices):.2f}")  # Sum the list of prices
    else:
        print("No valid prices available for calculation")

# Check if wkl_4 is empty
if wkl_4.empty:
    print("No data available for weekly analysis. Try adjusting the start date.")
else:
    # Find the most recent date in wkl_4 that's not in the future
    latest_available_date_weekly = wkl_4.index[wkl_4.index <= current_date].max()
    
    # Get top performers for the current week
    current_top_performers_weekly = wkl_4.loc[latest_available_date_weekly].nlargest(5)

    print("\nTop performers for the current week to be invested in:")
    print(current_top_performers_weekly)

    # Get latest stock prices for top weekly performers
    weekly_prices = []  # New list to store prices
    print("\nLatest stock prices for top weekly performers:")
    for ticker in current_top_performers_weekly.index:
        try:
            history = yf.Ticker(ticker).history(period="1d")
            if not history.empty:
                latest_price = history['Close'].iloc[-1]
                weekly_prices.append(latest_price)  # Add price to the list
                print(f"{ticker}: ${latest_price:.2f}")
            else:
                print(f"No recent data available for {ticker}")
        except Exception as e:
            print(f"Error fetching data for {ticker}: {str(e)}")

    if weekly_prices:
        print('Total:')
        print(f"${sum(weekly_prices):.2f}")  # Sum the list of prices
    else:
        print("No valid prices available for calculation")

#compared to our 7.01, if you were to buy at the start and sell at the end, you would make 5173/2058 = 2.5 at time of writing. So our strategy outperformed the S&P!!!
#Without taking trading fees into account