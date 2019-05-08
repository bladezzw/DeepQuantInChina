#!/usr/bin/python
# -*- coding: utf-8 -*-

# portfolio.py

from __future__ import print_function

import datetime
from math import floor

try:
    import Queue as queue
except ImportError:
    import queue

import numpy as np
import pandas as pd

from backtesting.event import EventFill, EventOrder
from backtesting.performance import create_sharpe_ratio, create_drawdowns


class Portfolio(object):
    """
    The Portfolio class handles the positions and market
    value of all instruments at a resolution of a "bar",
    i.e. secondly, minutely, 5-min, 30-min, 60 min or EOD.

    The positions DataFrame stores a time-index of the 
    quantity of positions held. 

    The holdings DataFrame stores the cash and total market
    holdings value of each symbol for a particular 
    time-index, as well as the percentage change in 
    portfolio total across bars.
    """

    def __init__(self, bars, events, start_date, initial_capital=100000.0, lever = 1):
        """
        Initialises the portfolio with bars and an event queue. 
        Also includes a starting datetime index and initial capital 
        (USD unless otherwise stated).

        Parameters:
        bars - The DataHandler object with current market data.
        events - The Event Queue object.
        start_date - The start date (bar) of the portfolio.
        initial_capital - The starting capital in USD.
        """
        self.bars = bars
        self.events = events
        self.symbol_list = self.bars.symbol_list
        self.start_date = start_date
        self.initial_capital = initial_capital

        self.all_positions = []
        self.current_positions = dict((k, v) for k, v in [(s, 0) for s in self.symbol_list])

        self.all_holdings = []
        self.current_holdings = self.construct_current_holdings()

    def construct_current_holdings(self):
        """
        This constructs the dictionary which will hold the instantaneous
        value of the portfolio across all symbols.
        """
        d = dict((k, v) for k, v in [(s, 0.0) for s in self.symbol_list])
        d['cash'] = self.initial_capital
        d['commission'] = 0.0
        d['signal'] = 0
        d['total'] = self.initial_capital
        return d

    def update_timeindex(self, event):
        """
        Adds a new record to the positions matrix for the current 
        market data bar. This reflects the PREVIOUS bar, i.e. all
        current market data at this stage is known (OHLCV).

        Makes use of a MarketEvent from the events queue.
        """
        latest_datetime = self.bars.get_latest_bar_datetime(self.symbol_list[0])

        # Update positions
        # ================
        dp = dict((k, v) for k, v in [(s, 0) for s in self.symbol_list])
        # e.g. dp = {'000001': 0, '000001.SH': 0}

        dp['datetime'] = latest_datetime
        # e.g. {'000001': 0, '000001.SH': 0, 'datetime': Timestamp('2010-08-06 00:00:00')}

        for s in self.symbol_list:
            dp[s] = self.current_positions[s]
        # {'000001': 0, '000001.SH': 0, 'datetime': Timestamp('2010-08-06 00:00:00')}

        # Append the current positions
        self.all_positions.append(dp)

        # Update holdings
        # ===============
        dh = dict((k, v) for k, v in [(s, 0) for s in self.symbol_list])
        dh['datetime'] = latest_datetime
        dh['cash'] = self.current_holdings['cash']
        dh['commission'] = self.current_holdings['commission']
        dh['total'] = self.current_holdings['cash']
        dh['signal'] = self.current_holdings['signal']

        for s in self.symbol_list:
            # Approximation to the real value
            market_value = self.current_positions[s] * self.bars.get_latest_bar_value(s, "close")
            dh[s] = market_value
            dh['total'] += market_value

        # Append the current holdings
        self.all_holdings.append(dh)
        self.current_holdings['signal'] = 0  # reset the signal

    # ======================
    # FILL/POSITION HANDLING
    # ======================

    def update_positions_from_fill(self, fill):
        """
        Takes a Fill object and updates the position matrix to
        reflect the new position.

        Parameters:
        fill - The Fill object to update the positions with.
        """
        # Check whether the fill is a buy or sell
        fill_dir = 0
        if fill.direction == 'BUY':
            fill_dir = 1
        if fill.direction == 'SELL':
            fill_dir = -1

        # Update positions list with new quantities
        self.current_positions[fill.symbol] += fill_dir * fill.quantity

    def update_holdings_from_fill(self, fill):
        """
        Takes a Fill object and updates the holdings matrix to
        reflect the holdings value.

        Parameters:
        fill - The Fill object to update the holdings with.
        """
        # Check whether the fill is a buy or sell
        fill_dir = 0
        if fill.direction == 'BUY':
            fill_dir = 1
        if fill.direction == 'SELL':
            fill_dir = -1

        # Update holdings list with new quantities
        fill_cost = self.bars.get_latest_bar_value(
            fill.symbol, "close"
        )
        cost = fill_dir * fill_cost * fill.quantity
        self.current_holdings[fill.symbol] += cost
        self.current_holdings['commission'] += fill.commission
        self.current_holdings['cash'] -= (cost + fill.commission)
        self.current_holdings['total'] -= (cost + fill.commission)
        self.all_holdings[-1]['signal'] = fill_dir

    def update_fill(self, event):
        """
        Updates the portfolio current positions and holdings 
        from a FillEvent.
        """
        if event.type_ == 'FILL':
            self.update_positions_from_fill(event)
            self.update_holdings_from_fill(event)

    def generate_naive_order(self, signal):
        """
        Simply files an Order object as a constant quantity
        sizing of the signal object, without risk management or
        position sizing considerations.

        Parameters:
        signal - The tuple containing Signal information.
        """
        order = None

        symbol = signal.symbol
        direction = signal.signal_type
        strength = signal.strength
        # the quantity of a certain symbol
        mkt_quantity = signal.mkt_quantity

        cur_quantity = self.current_positions[symbol]
        order_type = 'MKT'

        if direction == 'LONG' and cur_quantity == 0:
            order = EventOrder(symbol, order_type, mkt_quantity, 'BUY')
        if direction == 'SHORT' and cur_quantity == 0:
            order = EventOrder(symbol, order_type, mkt_quantity, 'SELL')

        if direction == 'EXIT' and cur_quantity > 0:
            order = EventOrder(symbol, order_type, abs(cur_quantity), 'SELL')
        if direction == 'EXIT' and cur_quantity < 0:
            order = EventOrder(symbol, order_type, abs(cur_quantity), 'BUY')
        return order

    def update_signal(self, event):
        """
        Acts on a SignalEvent to generate new orders 
        based on the portfolio logic.
        """
        if event.type_ == 'SIGNAL':
            order_event = self.generate_naive_order(event)
            self.events.put(order_event)

    # ========================
    # POST-BACKTEST STATISTICS
    # ========================

    def create_equity_curve_dataframe(self):
        """
        Creates a pandas DataFrame from the all_holdings
        list of dictionaries.
        """
        curve = pd.DataFrame(self.all_holdings)
        curve.set_index('datetime', inplace=True)
        curve['returns'] = curve['total'].pct_change()
        curve['equity_curve'] = (1.0 + curve['returns']).cumprod()
        self.ohlcv = self.bars.symbol_data_dict
        self.equity_curve = curve

    def output_summary_stats(self):
        """
        Creates a list of summary statistics for the portfolio.
        """
        total_return = self.equity_curve['equity_curve'][-1]
        returns = self.equity_curve['returns']
        pnl = self.equity_curve['equity_curve']

        sharpe_ratio = create_sharpe_ratio(returns, periods=252 * 60 * 6.5)
        drawdown, max_dd, dd_duration = create_drawdowns(pnl)
        self.equity_curve['drawdown'] = drawdown
        self.all_data = pd.concat([self.ohlcv, self.equity_curve], axis=1)

        stats = [("Total Return", "%0.2f%%" % ((total_return - 1.0) * 100.0)),
                 ("Sharpe Ratio", "%0.2f" % sharpe_ratio),
                 ("Max Drawdown", "%0.2f%%" % (max_dd * 100.0)),
                 ("Drawdown Duration", "%d" % dd_duration)]

        self.all_data.to_csv('equity.csv')  # the csv's path is where the process is running
        return stats, self.all_data

class Portfolio_For_stock_real(Portfolio):

    def __init__(self):
        super(Portfolio_For_stock_real, self).__init__()


    def generate_naive_order(self, signal):
        """
        for real trade
        :param signal:
        :return:
        """
        pass


class Portfolio_For_futures(object):
    """
    The Portfolio class handles the positions and market
    value of all instruments at a resolution of a "bar",
    i.e. secondly, minutely, 5-min, 30-min, 60 min or EOD.

    The positions DataFrame stores a time-index of the
    quantity of positions held.

    The holdings DataFrame stores the cash and total market
    holdings value of each symbol for a particular
    time-index, as well as the percentage change in
    portfolio total across bars.
    """

    def __init__(self, bars, events, start_date, initial_capital=100000.0, lever = 1.):
        """
        Initialises the portfolio with bars and an event queue.
        Also includes a starting datetime index and initial capital
        (USD unless otherwise stated).

        Parameters:
        bars - The DataHandler object with current market data.
        events - The Event Queue object.
        start_date - The start date (bar) of the portfolio.
        initial_capital - The starting capital in USD.
        """
        self.bars = bars
        self.events = events
        self.symbol_list = self.bars.symbol_list
        self.start_date = start_date
        self.initial_capital = initial_capital

        self.lever = lever

        self.all_positions = []
        self.current_positions = dict((k, v) for k, v in [(s, 0) for s in self.symbol_list])

        self.all_holdings = []
        self.current_holdings = self.construct_current_holdings()
        self.pre_holding_price = {}

        self.trade_count = 0

    def construct_current_holdings(self):
        """
        This constructs the dictionary which will hold the instantaneous
        value of the portfolio across all symbols.
        """
        d = dict((k, v) for k, v in [(s, 0.0) for s in self.symbol_list])
        d['cash'] = self.initial_capital
        d['commission'] = 0.0
        d['signal'] = 0
        d['direction'] = 0
        d['total'] = self.initial_capital
        return d

    def update_timeindex(self, event):
        """
        Adds a new record to the positions matrix for the current
        market data bar. This reflects the PREVIOUS bar, i.e. all
        current market data at this stage is known (OHLCV).

        Makes use of a MarketEvent from the events queue.
        """
        latest_datetime = self.bars.get_latest_bar_datetime(self.symbol_list[0])

        # Update positions
        # ================
        dp = dict((k, v) for k, v in [(s, 0) for s in self.symbol_list])
        # e.g. dp = {'000001': 0, '000001.SH': 0}

        dp['datetime'] = latest_datetime
        # e.g. {'000001': 0, '000001.SH': 0, 'datetime': Timestamp('2010-08-06 00:00:00')}

        for s in self.symbol_list:
            dp[s] = self.current_positions[s]
        # {'000001': 0, '000001.SH': 0, 'datetime': Timestamp('2010-08-06 00:00:00')}

        # Append the current positions
        self.all_positions.append(dp)

        # Update holdings
        # ===============
        dh = dict((k, v) for k, v in [(s, 0) for s in self.symbol_list])
        dh['datetime'] = latest_datetime
        dh['cash'] = self.current_holdings['cash']
        dh['commission'] = self.current_holdings['commission']
        dh['signal'] = self.current_holdings['signal']
        dh['direction'] = self.current_holdings['direction']
        dh['total'] = self.current_holdings['cash']

        for s in self.symbol_list:
            # Approximation to the real value
            c = self.bars.get_latest_bar_value(s, "close")
            if dh['direction'] == 1:
                market_value = self.current_positions[s] * (
                            (c - self.pre_holding_price[s]) * self.lever + self.pre_holding_price[s])
                dh[s] = market_value
                dh['total'] += market_value  # (拥有在险资产时)动态的总资产= 当前的现金 + 在险资产
                self.current_holdings['total'] = dh['total']

            elif dh['direction'] == -1:
                market_value = - self.current_positions[s] * (
                            (self.pre_holding_price[s] - c) * self.lever + self.pre_holding_price[s])
                dh[s] = market_value
                dh['total'] += market_value  # (拥有在险资产时)动态的总资产= 当前的现金 + 在险资产
                self.current_holdings['total'] = dh['total']

        # Append the current holdings
        self.all_holdings.append(dh)
        self.current_holdings['signal'] = 0  # reset the signal

    # ======================
    # FILL/POSITION HANDLING
    # ======================

    def update_positions_from_fill(self, fill):
        """
        Takes a Fill object and updates the position matrix to
        reflect the new position.

        Parameters:
        fill - The Fill object to update the positions with.
        """
        # Check whether the fill is a buy or sell
        fill_dir = 0
        if fill.direction == 'BUY':
            fill_dir = 1
        if fill.direction == 'SELL':
            fill_dir = -1

        # Update positions list with new quantities
        self.current_positions[fill.symbol] = fill_dir * fill.quantity

    def update_holdings_from_fill(self, fill):
        """
        Takes a Fill object and updates the holdings matrix to
        reflect the holdings value.

        Parameters:
        fill - The Fill object to update the holdings with.
        目前只处理单边交易(只买或只卖一个品种)
        """
        # Check whether the fill is a buy or sell

        # 默认以后都只交易1手,信号出现时,交换多空头寸.
        fill_dir = 0
        if fill.direction == 'BUY':
            fill_dir = 1
            # Update holdings list with new quantities
            fill_cost = self.bars.get_latest_bar_value(
                fill.symbol, "close"
            )
            cost = fill_dir * fill_cost * fill.quantity
        if fill.direction == 'SELL':
            fill_dir = -1
            fill_cost = self.bars.get_latest_bar_value(
                fill.symbol, "close"
            )
            cost = -fill_dir * fill_cost * fill.quantity

        self.current_holdings['commission'] += fill.commission
        self.current_holdings[fill.symbol] += cost  # 当前持仓价值
        self.current_holdings['commission'] += fill.commission  # 总共的交易费
        self.current_holdings['cash'] = self.current_holdings['total'] - cost - fill.commission

        self.current_holdings['total'] -= fill.commission  # (买入的时候)总资产:=总资产-交易费
        self.current_holdings['direction'] = fill_dir  # 持仓方向,当前只处理1个品种的持仓方向
        self.all_holdings[-1]['signal'] = fill_dir  # 当前只处理1个品种的信号
        self.pre_holding_price[fill.symbol] = fill_cost

    def update_fill(self, event):
        """
        Updates the portfolio current positions and holdings
        from a FillEvent.
        """
        if event.type_ == 'FILL':
            self.trade_count += 1
            self.update_positions_from_fill(event)
            self.update_holdings_from_fill(event)

    def generate_naive_order(self, signal):
        """
        Simply files an Order object as a constant quantity
        sizing of the signal object, without risk management or
        position sizing considerations.

        Parameters:
        signal - The tuple containing Signal information.
        """
        order = None

        symbol = signal.symbol
        direction = signal.signal_type
        strength = signal.strength
        # the quantity of a certain symbol
        mkt_quantity = signal.mkt_quantity  # TODO:以后可以加入自适应买入手数(能买多少买多少)

        cur_quantity = self.current_positions[symbol]
        order_type = 'MKT'

        if direction == 'LONG' and cur_quantity == 0:
            order = EventOrder(symbol, order_type, mkt_quantity, 'BUY')
        if direction == 'SHORT' and cur_quantity == 0:
            order = EventOrder(symbol, order_type, mkt_quantity, 'SELL')

        if direction == 'EXIT' and cur_quantity > 0:
            order = EventOrder(symbol, order_type, abs(cur_quantity), 'SELL')
        if direction == 'EXIT' and cur_quantity < 0:
            order = EventOrder(symbol, order_type, abs(cur_quantity), 'BUY')
        return order

    def update_signal(self, event):
        """
        Acts on a SignalEvent to generate new orders
        based on the portfolio logic.
        """
        if event.type_ == 'SIGNAL':
            order_event = self.generate_naive_order(event)
            self.events.put(order_event)

    # ========================
    # POST-BACKTEST STATISTICS
    # ========================

    def create_equity_curve_dataframe(self):
        """
        Creates a pandas DataFrame from the all_holdings
        list of dictionaries.
        """
        curve = pd.DataFrame(self.all_holdings)
        curve.set_index('datetime', inplace=True)
        curve['returns'] = curve['total'].pct_change()
        curve['equity_curve'] = (1.0 + curve['returns']).cumprod()
        self.ohlcv = self.bars.symbol_data_dict
        self.equity_curve = curve

    def output_summary_stats(self):
        """
        Creates a list of summary statistics for the portfolio.
        """
        total_return = self.equity_curve['equity_curve'][-1]
        returns = self.equity_curve['returns']
        pnl = self.equity_curve['equity_curve']

        sharpe_ratio = create_sharpe_ratio(returns, periods=252 * 60 * 6.5)
        drawdown, max_dd, dd_duration = create_drawdowns(pnl)
        self.equity_curve['drawdown'] = drawdown  # 这里用当前的总资产/最高价值时候的总资产
        self.all_data = pd.concat([self.ohlcv, self.equity_curve], axis=1)

        stats = [("Total Return", "%0.2f%%" % ((total_return - 1.0) * 100.0)),
                 ("Sharpe Ratio", "%0.2f" % sharpe_ratio),
                 ("Max Drawdown", "%0.2f%%" % (max_dd * 100.0)),
                 ("Drawdown Duration", "%d" % dd_duration)]

        self.all_data.to_csv('equity.csv')  # the csv's path is where the process is running
        return stats, self.all_data

class Portfolio_For_futures_real(Portfolio_For_futures):

    def __init__(self):
        super(Portfolio_For_futures, self).__init__()

    def update_signal(self, event):
        """
        Acts on a SignalEvent to generate new orders
        based on the portfolio logic.
        """
        if event.type_ == 'SIGNAL':
            order_event = self.generate_naive_order(event)
            self.events.put(order_event)


    def generate_naive_order(self, signal):
        """
        for real trade
        :param signal:
        :return:
        """
        pass

