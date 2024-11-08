import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

#price data for german index thing
df = yf.download('^GDAXI', start='2020-01-01')

#20 day moving average
df['MA20'] = df['Adj Close'].rolling(20).mean()

#50 day moving average
df['MA50'] = df['Adj Close'].rolling(50).mean()

#drop nan values
df = df.dropna()

df = df[['Adj Close', 'MA20', 'MA50']]

Buy = []
Sell = []

for i in range(len(df)):
    if df.MA20.iloc[i] > df.MA50.iloc[i] and df.MA20.iloc[i-1] < df.MA50.iloc[i-1]:
        Buy.append(i)
    elif df.MA20.iloc[i] < df.MA50.iloc[i] and df.MA20.iloc[i-1] > df.MA50.iloc[i-1]:
        Sell.append(i)

#print(df['MA20'].iloc[5])

BuyPrices = []
SellPrices = []

for poo in Buy:
    BuyPrices.append(df['Adj Close'].iloc[poo])

for poo in Sell:
    SellPrices.append(df['Adj Close'].iloc[poo])

if Buy[0] > Sell [0]:
    SellPrices = SellPrices[1:]
if len(BuyPrices) > len(SellPrices):
    BuyPrices = BuyPrices[:len(BuyPrices)-1]

money = 1
tradeW = 0
tradeL = 0

for i in range(len(BuyPrices)):
    trade = SellPrices[i] / BuyPrices[i]
    if trade > 1:
        tradeW += 1
    else:
        tradeL += 1
    money = money * (SellPrices[i] / BuyPrices[i])

print('Wins:', tradeW, 'Losses:', tradeL)
print('profit:', money)
print('growth:', df['Adj Close'].iloc[len(df['Adj Close'])-1]/df['Adj Close'].iloc[0])

plt.plot(df['Adj Close'], label='Asset price', c='blue', alpha=0.5)
plt.plot(df['MA20'], label='20 day moving average', c='k', alpha=0.9)
plt.plot(df['MA50'], label='50 day moving average', c='magenta', alpha=0.9)

plt.scatter(df.iloc[Buy].index, df.iloc[Buy]['Adj Close'], marker='^', color='g', s=100)

plt.scatter(df.iloc[Sell].index, df.iloc[Sell]['Adj Close'], marker='v', color='r', s=100)
plt.legend()
plt.show()