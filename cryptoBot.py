from alpaca_trade_api.rest import REST, TimeFrame
import pandas as pd
from datetime import datetime, timedelta
import math
import time

BASE_URL = "https://paper-api.alpaca.markets"
KEY_ID = "PKRLMELQEU9T5VYOQG49"
SECRET_KEY = "w9i1JQngBbCOjUu1BlWd890AAGuOxH6X0ygkg586"

# REST API Connection
api = REST(key_id=KEY_ID, secret_key=SECRET_KEY, base_url="https://paper-api.alpaca.markets")

SYMBOL = 'BTCUSD'
SMA_FAST = 12
SMA_SLOW = 24
QTY_PER_TRADE = 1


# Run loop every 60 seconds because I am trading on 1 minute data
def get_pause():
    now = datetime.now()
    next_min = now.replace(second=0, microsecond=0) + timedelta(minutes=1)
    pause = math.ceil((next_min - now).seconds)
    print(f"Sleep for {pause}")
    return pause


# Retrieves current positions
def get_position(symbol):
    positions = api.list_positions()
    for p in positions:
        if p.symbol == symbol:
            return float(p.qty)
    return 0


# Returns a series with the moving average
def get_sma(series, periods):
    return series.rolling(periods).mean()


# Checks whether we should buy (fast moving average > slow moving average)
def get_signal(fast, slow):
    print(f"Fast {fast[-1]}  /  Slow: {slow[-1]}")
    return fast[-1] > slow[-1]


# Get up-to-date 1 minute data from Alpaca and add the moving averages
def get_bars(symbol):
    bars = api.get_crypto_bars(symbol, TimeFrame.Minute).df
    bars = bars[bars.exchange == 'CBSE']
    bars[f'sma_fast'] = get_sma(bars.close, SMA_FAST)
    bars[f'sma_slow'] = get_sma(bars.close, SMA_SLOW)
    return bars


# Two moving averages strategy: Fast will consist of calculating the average of the closing price during the previous
# 12 minutes. Slow moving average, which acts the same but based the closing price of the previous 24 minutes.

while True:
    # Get Data
    bars = get_bars(symbol=SYMBOL)
    # Check positions
    position = get_position(symbol=SYMBOL)
    should_buy = get_signal(bars.sma_fast, bars.sma_slow)
    print(f"Position: {position} / Should Buy: {should_buy}")
    if position == 0 and should_buy == True:
        # I buy one Bitcoin
        api.submit_order(SYMBOL, qty=QTY_PER_TRADE, side='buy')  # Submits order to buy 1 Bitcoin if conditions are met
        print(f'Symbol: {SYMBOL} / Side: BUY / Quantity: {QTY_PER_TRADE}')
    elif position > 0 and should_buy == False:
        # I sell one Bitcoin
        api.submit_order(SYMBOL, qty=QTY_PER_TRADE, side='sell')  # Submits order to sell 1 Bitcoin if conditions are met
        print(f'Symbol: {SYMBOL} / Side: SELL / Quantity: {QTY_PER_TRADE}')

    time.sleep(get_pause())
    print("*" * 20)
