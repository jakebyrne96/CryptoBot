# CryptoBot
Automatic Crypto Trading Bot

Using Two moving averages strategy: Fast will consist of calculating the average of the closing price during the previous 12 minutes. 
Slow moving average, which acts the same but based the closing price of the previous 24 minutes.

It runs this strategy every 60 seconds as I am basing it off the 1 minute historical data, then compares to see if the fast moving function is 
greater than the slow moving function to decide whether to buy or sell.
