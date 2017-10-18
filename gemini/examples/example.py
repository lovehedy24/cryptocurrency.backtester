import pandas as pd

import gemini.gemini as gemini
from gemini.helpers import helpers, poloniex as px

pair = "BTC_ETH"  # Use ETH pricing data on the BTC market
period = 1800  # Use 1800 second candles
days_back = 0  # Grab data starting 30 days ago
days_data = 100  # From there collect 60 days of data
lookback_period = 1  # How many days to lookback for momentum
trading_interval = 1  # Run trading logic every X days

# Request data from Poloniex
data = px.get_past(pair, period, days_back, days_data)
# print(data)
# Convert to Pandas dataframe with datetime format
data = pd.DataFrame(data)

data['date'] = pd.to_datetime(data['date'], unit='s')


def logic(account, lookback, lookback_period):
    # Process dataframe to collect signals
    # lookback = helpers.getSignals(lookback)

    # Load into period class to simplify indexing
    lookback = helpers.Period(lookback)

    today = lookback.loc(0)  # Current candle
    yesterday = lookback.loc(-1)  # Previous candle
    print('from {} to {}'.format(yesterday['date'], today['date']))

    # print(Today)
    if today['close'] < yesterday['close']:
        exit_price = today['close']
        for position in account.positions:
            if position.order_type == 'Long':
                account.close_position(position, 0.5, exit_price)

    elif today['close'] > yesterday['close']:
        risk = 0.03
        entry_price = today['close']
        entry_capital = account.buying_power * risk
        if entry_capital >= 0:
            account.enter_position('Long', entry_capital, entry_price)


# Load the data into a backtesting class called Run
r = gemini.Run(data)

# start backtesting custom logic with 1000 (BTC) intital capital
r.start(1000, logic, trading_interval, lookback_period)

r.results()
r.chart(show_trades=False)
