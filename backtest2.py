#!/usr/bin/env python2.7
''' do some optimization
'''


__author__ = 'fantasy <pkuqiuning@gmail.com>'
__created__ = '2015-05-18 11:44:53 -0400'


import zipline
from zipline.api import order_target_percent, record, get_datetime
from zipline import TradingAlgorithm

import numpy as np
import pandas as pd
import matplotlib.pyplot as pyplot
import pytz
from datetime import datetime
from zipline.utils.factory import load_bars_from_yahoo
from functools import partial


start = '2014-1-4'
end = '2015-2-19'
#end = '2015-2-18'
#stocks = ['DLTR', 'GOOGL', 'SPY']
stocks = pd.read_csv('data/stocklist.csv', header=None)


#ind_data = pd.read_csv('DLTR.csv', index_col = 'harvested_at', parse_dates=True)
ind_data = pd.read_csv('data/NASDAQ100_MarketNeutral.csv', index_col = 'start_date', parse_dates=True)
start = datetime.strptime(start, '%Y-%m-%d')
end = datetime.strptime(end, '%Y-%m-%d')
data = load_bars_from_yahoo(stocks=stocks, start=start, end=end)

data = data.fillna(method='ffill', axis=2)
data = data.fillna(method='bfill', axis=2)

#data.dropna(axis=1, inplace=True)


def initialize_template(context, parameters):
    context.stocks = stocks
    context.parameters = parameters


def handle_data(context, data):
    now_minute = get_datetime().strftime('%Y-%m-%d %H:%M')
    for i, v in ind_data[now_minute].iterrows():
        # iter through all the indicators in this minute
        #stock = v['entities_ticker_1']
        stock = v['symbol']
        nlong = 0
        nshort = 0
        # trade
        if stock in context.stocks:
            print stock, v['article_sentiment']
            # select stocks in the context
            if (v['article_sentiment'] > context.parameters['article_sentiment_upper']):
                order_target_percent(stock, 0.1)
                nlong += 1
            elif (v['article_sentiment'] < context.parameters['article_sentiment_lower']):
                order_target_percent(stock, -0.1)
                nshort += -1
        # record trade
        record(long=nlong, short=nshort)


def para2sharpe(para):
    initialize = partial(initialize_template, parameters=para)
    algo_obj = TradingAlgorithm(initialize=initialize, handle_data=handle_data)
    result = algo_obj.run(data)
    score = result2sharpe(result)
    return score


def result2sharpe(result):
    '''extract performance from backtest result'''
    sharpe = (result.returns.mean()*252) / (result.returns.std() * np.sqrt(252))
    return sharpe


#uppers = np.linspace(0, 1, 11)
#lowers = -uppers
uppers = [0.35]
lowers = [-0.35]

#: Create a dictionary to hold all the results of our algorithm run
all_sharpes = {}
for upper, lower in zip(uppers, lowers):
    parameters = {
        'article_sentiment_upper': upper,
        'article_sentiment_lower': lower,
    }
    sharpe = para2sharpe(parameters)
    all_sharpes[upper] = sharpe

#all_sharpes = pd.DataFrame(all_sharpes)
#all_sharpes.index.name = "article sentiment upper"
#all_sharpes.columns.name = "AAPL Weight"
print all_sharpes


def heat_map(df):
    pass
