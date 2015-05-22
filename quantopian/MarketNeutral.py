import numpy as np
import pandas as pd
from datetime import timedelta

def initialize(context):
    set_symbol_lookup_date('2015-04-01')
    context.stocks=symbols('FOXA','ATVI','ADBE','AKAM','ALXN','ALTR','AMGN','ADI','AMAT','ADSK','ADP','AVGO','BIDU','BBBY','BIIB','BRCM','CHRW','CA','CTRX','CELG','CERN','CHTR','CHKP','CSCO','CTXS','CTSH','COST','DTV','DISH','DLTR','EBAY','EQIX','EXPE','EXPD','ESRX','FFIV','FAST','FISV','GRMN','GILD','HSIC','ILMN','INTC','INTU','ISRG','KLAC','GMCR','KRFT','LMCK','LMCA','LLTC','MAR','MAT','MXIM','MU','MDLZ','MNST','MYL','NTAP','NFLX','NVDA','NXPI','ORLY','PCAR','PAYX','QCOM','REGN','ROST','SNDK','SBAC','STX','SIAL','SIRI','SPLS','SBUX','SRCL','SYMC','TSLA','TXN','PCLN','TSCO','TRIP','VRSK','VRTX','VIAB','VIP','VOD','WDC','WFM','WYNN','XLNX')
    
    set_benchmark(symbol('SPY'))
   
    set_commission(commission.PerShare(cost=0.014, min_trade_cost=1.4))
    
    set_slippage(slippage.FixedSlippage(spread=0))
    
    fetch_csv("https://dl.dropboxusercontent.com/u/70792051/Accern%20Backtest/NASDAQ100_MarketNeutral.csv",
                 date_column ='start_date',
                 date_format ='%m/%-d/%Y %H:%M')
        
    
    schedule_function(long_bulls_short_bears,
                      date_rules.week_start(),
                      time_rules.market_open())
    
    schedule_function(close_all_positions,
                      date_rules.week_end(),
                      time_rules.market_close(minutes=15))
    
    """#Only needed in testing/debugging to ensure orders are closed like in IB
    schedule_function(end_of_day, 
                      date_rules.every_day(), 
                      time_rules.market_close(minutes=1))"""
    
    
    #Story Sentiment
    context.upper_bound = 0.35
    context.lower_bound = -0.35
    #Impact Score
    context.upper_bound_a = 85
    context.lower_bound_a = 85
    
    
        
    
def long_bulls_short_bears(context, data):
    
    #exchange_time = pd.Timestamp(get_datetime()).tz_convert('US/Eastern')
    
    bulls = []
    bears = []
    
    for stock in context.stocks:
        if ('story_sentiment' and 'event_impact_score_entity_1') in data[stock]:
            if (data[stock]['story_sentiment'] > context.upper_bound) and (data[stock]['event_impact_score_entity_1'] > context.upper_bound_a):
                bulls.append(stock)
                log.info(get_datetime())
                log.info("lala")
              
            elif (data[stock]['story_sentiment'] < context.lower_bound) and (data[stock]['event_impact_score_entity_1'] > context.lower_bound_a):
                bears.append(stock)
               
           
    if len(bulls) == 0 or len(bears) == 0:
        return
    
    for stock in bulls:
        if len(bulls) != 0:
            order_target_percent(stock, 1.0/len(bulls))
            
    for stock in bears:
        if len(bears) != 0:
            order_target_percent(stock, -1.0/len(bears))    
       
    #: Record our positions
    record(longs=len(bulls))
    record(shorts=len(bears))
    log.info(get_datetime())
    
def close_all_positions(context, data):
    for stock in data:
        if context.portfolio.positions[stock.sid].amount != 0:
            order_target_percent(stock, 0)
                   
def handle_data(context, data):
    pass
                
"""def end_of_day(context, data):
    # cancle any order at the end of day. Do it ourselves so we can see slow moving stocks.
    open_orders = get_open_orders()
    
    if open_orders:# or context.portfolio.positions_value > 0.:
        #log.info("")
        log.info("*** EOD: Stoping Orders & Printing Held ***")

    # Print what positions we are holding overnight
    #for stock in data:
    #    if context.portfolio.positions[stock.sid].amount != 0:
    #        log.info("{0:s} has remaining {1:,d} Positions worth ${2:,.2f}"\
    #                 .format(stock.symbol,
    #                         context.portfolio.positions[stock.sid].amount,
    #                         context.portfolio.positions[stock.sid].cost_basis\
    #                         *context.portfolio.positions[stock.sid].amount))
    # Cancle any open orders ourselves(In live trading this would be done for us, soon in backtest too)
    if open_orders:  
        # Cancle any open orders ourselves(In live trading this would be done for us, soon in backtest too)
        for security, orders in open_orders.iteritems():
            for oo in orders:
                log.info("X CANCLED {0:s} with {1:,d} / {2:,d} filled"\
                                     .format(security.symbol,
                                             oo.filled,
                                             oo.amount))
                cancel_order(oo)
    #"""
            
    
        
        
        
        
        
