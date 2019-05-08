#!/usr/bin/python
# -*- coding: utf-8 -*-

# data.py

from __future__ import print_function

from abc import ABCMeta, abstractmethod
import datetime
import os, os.path

import numpy as np
import pandas as pd

from backtesting.event import EventMarket
import time
from MySqlio import mysql_api


class DataHandler(object):
    """
    DataHandler is an abstract base class providing an interface for
    all subsequent (inherited) data handlers (both live and historic).

    The goal of a (derived) DataHandler object is to output a generated
    set of bars (OHLCVI) for each symbol requested. 

    This will replicate how a live strategy would function as current
    market data would be sent "down the pipe". Thus a historic and live
    system will be treated identically by the rest of the backtesting suite.
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def get_latest_bar(self, symbol):
        """
        Returns the last bar updated.返回最新一个数据
        """
        raise NotImplementedError("Should implement get_latest_bar()")

    @abstractmethod
    def get_latest_bars(self, symbol, N=1):
        """
        Returns the last N bars updated.返回最新的N个数据
        """
        raise NotImplementedError("Should implement get_latest_bars()")

    @abstractmethod
    def get_latest_bar_datetime(self, symbol):
        """
        Returns a Python datetime object for the last bar.返回python datetime类的最后一个数据
        """
        raise NotImplementedError("Should implement get_latest_bar_datetime()")

    @abstractmethod
    def get_latest_bar_value(self, symbol, val_type):
        """
        Returns one of the Open, High, Low, Close, Volume or OI
        from the last bar.返回最后一个数据中的某个值
        """
        raise NotImplementedError("Should implement get_latest_bar_value()")

    @abstractmethod
    def get_latest_bars_values(self, symbol, val_type, N=1):
        """
        Returns the last N bar values from the 
        latest_symbol list, or N-k if less available.返回最后N个数据中value字段的值
        """
        raise NotImplementedError("Should implement get_latest_bars_values()")

    @abstractmethod
    def update_bars(self):
        """
        Pushes the latest bars to the bars_queue for each symbol
        in a tuple OHLCVI format: (datetime, open, high, low, 
        close, volume, open interest).更新数据以OHLCVI格式
        """
        raise NotImplementedError("Should implement update_bars()")


class RealTradeDataHandler(DataHandler):
    """
    RealTradeDataHandler is designed to recive data for
    each requested symbol from mdapi and provide an interface
    to obtain the "latest" bar in a live
    trading interface.
    """

    def __init__(self, events, symbol_list, latest_symbol_data=None):
        """
        Initialises the historic data handler by requesting
        the location of the CSV files and a list of symbols.

        It will be assumed that all files are of the form
        'symbol.csv', where symbol is a string in the list.

        Parameters:
        events - The Event Queue.
        symbol_list - A list of symbol strings.
        """
        self.symbol_list = symbol_list
        self.events = events
        self.symbol_data = {}
        self.symbol_data_dict = []  # 假设只有一个交易品种
        self.latest_symbol_data = {}
        self.continue_realtrade = True
        self.bar_index = 0
        self.initdata(latest_symbol_data)

    def initdata(self, latest_symbol_data):
        """
        默认如果有输入初始化数据的时候,只初始化1个交易品种
        :param latest_symbol_data:
        :return:
        """
        self.latest_symbol_data[self.symbol_list[0]] = latest_symbol_data  # 这里的数据类型是pandas类型,和backtest中稍有不同

    def get_latest_bar(self, symbol):
        """
        Returns the last bar from the latest_symbol list.
        """
        try:
            bars_list = self.latest_symbol_data[symbol]
        except KeyError:
            print("That symbol is not available in the historical data set.")
            raise
        else:
            return bars_list[-1]

    def get_latest_bars(self, symbol, N=1):
        """
        Returns the last N bars from the latest_symbol list,
        or N-k if less available.
        """
        try:
            bars_list = self.latest_symbol_data[symbol]
        except KeyError:
            print("That symbol is not available in the historical data set.")
            raise
        else:
            return bars_list[-N:]

    def get_latest_bar_datetime(self, symbol):
        """
        Returns a Python datetime object for the last bar.
        """
        try:
            bars_list = self.latest_symbol_data[symbol]
        except KeyError:
            print("That symbol is not available in the historical data set.")
            raise
        else:
            return bars_list.index[-1]

    def get_latest_bar_value(self, symbol, val_type):
        """
        Returns one of the Open, High, Low, Close, Volume or OI
        values from the pandas Bar series object.
        """
        try:
            bars_list = self.latest_symbol_data[symbol]
        except KeyError:
            print("That symbol is not available in the historical data set.")
            raise
        else:
            return getattr(bars_list[-1][1], val_type)

    def get_latest_bars_values(self, symbol, val_type, N=1):
        """
        Returns the last N bar values from the
        latest_symbol list, or N-k if less available.
        """
        try:
            bars_list = self.get_latest_bars(symbol, N)
        except KeyError:
            print("That symbol is not available in the historical data set.")
            raise
        else:
            if type(bars_list) == 'list':
                return np.array([getattr(b[1], val_type) for b in bars_list])
            else:
                return bars_list['close']

    def update_bars(self, event):
        """
        Pushes the latest bar to the latest_symbol_data structure
        for all symbols in the symbol list.
        """
        newbar = event.dict_
        # {'symbol': 'rb1905', 'Date': '20190425', 'Time': '17:01:15', 'open': 4146.0, 'high': 4147.0, 'low': 4146.0, 'close ': 4147.0, 'volume': 4, 'LowerLimitPrice': 3894.0, 'UpperLimitPrice': 4391.0}
        # data.loc[pd.Timestamp('20190425 17:01:15')] = {'symbol': 'rb1905', 'open': 4146.0, 'high': 4147.0,
        #                                                'low': 4146.0,
        #                                                'close ': 4147.0, 'volume': 4}
        Datetime = newbar['Date'] + ' ' + newbar['Time']
        newbar.pop('Date')
        newbar.pop("Time")
        newbar.pop('LowerLimitPrice')
        newbar.pop('UpperLimitPrice')

        print("datahandler.update_bars,newbar:", event.type_, ";;;")
        print("event.dict_:", event.dict_)

        for s in self.symbol_list:
            try:
                bar = newbar
            except StopIteration:
                self.continue_realtrade = False
            else:
                if bar is not None:
                    self.events.put(EventMarket())
                    # print("append newbar.")
                    self.latest_symbol_data[s].loc[pd.Timestamp(Datetime)] = newbar
                    # print('self.latest_symbol_data[s].loc[pd.Timestamp(Datetime)]:',
                    #       self.latest_symbol_data[s].loc[pd.Timestamp(Datetime)])
                    # self.latest_symbol_data[s].loc[pd.Timestamp]  # 因为数据不是list,不能append,得用pandas的数据插入方法,得先看bar的数据类型.

        # when update a list of bars of a new datetime, check the MarketEvent()
        print("datahandler.update_car: put EventMarket()")


class HistoricMysqlDataHandler(DataHandler):
    """TODO: to be revised
    HistoricMysqlDataHandler is designed to obtain data for
    each requested symbol from MySqlDB and provide an interface
    to obtain the "latest" bar in a manner identical to a live
    trading interface.
    """

    def __init__(self, events, csv_dir, symbol_list):
        """
        Initialises the historic data handler by requesting
        the location of the CSV files and a list of symbols.

        It will be assumed that all files are of the form
        'symbol.csv', where symbol is a string in the list.

        Parameters:
        events - The Event Queue.
        csv_dir - Absolute directory path to the CSV files.
        symbol_list - A list of symbol strings.
        """
        self.events = events
        self.csv_dir = csv_dir
        self.symbol_list = symbol_list

        self.symbol_data = {}
        self.symbol_data_dict = {}
        self.latest_symbol_data = {}  # # 这里的数据类型是dict{(tuple)}类型,和RealTrade中稍有不同,但处理数据的过程是一样的.
        self.continue_backtest = True
        self.bar_index = 0

        self._get_mysql_files()

    def _get_mysql_files(self):
        """

        them into pandas DataFrames within a symbol dictionary.

        For this handler it will be assumed that the data is
        taken from Yahoo. Thus its format will be respected.
        """
        comb_index = None
        for symbol in self.symbol_list:
            # Load the CSV file data of the symbol with no header information, indexed on datetime ascending
            try:
                self.symbol_data[symbol] = mysql_api.mysqlio.get_sth_from_mysql("xxx")  # 根据需求查找
                self.latest_symbol_data[symbol] = []
            except:
                print("Doesn't has %s's data" % symbol)

        # Reindex the dataframes
        for s in self.symbol_list:
            # '.iterrows()' ==  change data into a generator in a form of rows
            self.symbol_data[s] = self.symbol_data[s]. \
                reindex(index=comb_index, method='pad').iterrows()

    def _get_new_bar(self, symbol):
        """
        Returns the latest bar from the data feed.
        """
        for b in self.symbol_data[symbol]:
            yield b  # yield a bar in the order of rows

    def get_latest_bar(self, symbol):
        """
        Returns the last bar from the latest_symbol list.
        """
        try:
            bars_list = self.latest_symbol_data[symbol]
        except KeyError:
            print("That symbol is not available in the historical data set.")
            raise
        else:
            return bars_list[-1]

    def get_latest_bars(self, symbol, N=1):
        """
        Returns the last N bars from the latest_symbol list,
        or N-k if less available.
        """
        try:
            bars_list = self.latest_symbol_data[symbol]
        except KeyError:
            print("That symbol is not available in the historical data set.")
            raise
        else:
            return bars_list[-N:]

    def get_latest_bar_datetime(self, symbol):
        """
        Returns a Python datetime object for the last bar.
        """
        try:
            bars_list = self.latest_symbol_data[symbol]
        except KeyError:
            print("That symbol is not available in the historical data set.")
            raise
        else:
            return bars_list[-1][0]

    def get_latest_bar_value(self, symbol, val_type):
        """
        Returns one of the Open, High, Low, Close, Volume or OI
        values from the pandas Bar series object.
        """
        try:
            bars_list = self.latest_symbol_data[symbol]
        except KeyError:
            print("That symbol is not available in the historical data set.")
            raise
        else:
            return getattr(bars_list[-1][1], val_type)

    def get_latest_bars_values(self, symbol, val_type, N=1):
        """
        Returns the last N bar values from the
        latest_symbol list, or N-k if less available.
        """
        try:
            bars_list = self.get_latest_bars(symbol, N)
        except KeyError:
            print("That symbol is not available in the historical data set.")
            raise
        else:
            return np.array([getattr(b[1], val_type) for b in bars_list])

    def update_bars(self):
        """
        Pushes the latest bar to the latest_symbol_data structure
        for all symbols in the symbol list.
        """
        for s in self.symbol_list:
            try:
                bar = next(self._get_new_bar(s))
            except StopIteration:
                self.continue_backtest = False
            else:
                if bar is not None:
                    self.latest_symbol_data[s].append(bar)
        self.events.put(EventMarket())  # when update a list of bars of a new datetime, check the MarketEvent()


class HistoricCSVDataHandler(DataHandler):
    """
    HistoricCSVDataHandler is designed to read CSV files for
    each requested symbol from disk and provide an interface
    to obtain the "latest" bar in a manner identical to a live
    trading interface. 
    """

    def __init__(self, events, csv_dir, symbol_list):
        """
        Initialises the historic data handler by requesting
        the location of the CSV files and a list of symbols.

        It will be assumed that all files are of the form
        'symbol.csv', where symbol is a string in the list.

        Parameters:
        events - The Event Queue.
        csv_dir - Absolute directory path to the CSV files.
        symbol_list - A list of symbol strings.
        """
        self.events = events
        self.csv_dir = csv_dir
        self.symbol_list = symbol_list

        self.symbol_data = {}
        self.symbol_data_dict = []  # 假设只有一个
        self.latest_symbol_data = {}
        self.continue_backtest = True
        self.bar_index = 0

        self._open_convert_csv_files()

    def _open_convert_csv_files(self):
        """
        Opens the CSV files from the data directory, converting
        them into pandas DataFrames within a symbol dictionary.

        For this handler it will be assumed that the data is
        taken from Yahoo. Thus its format will be respected.
        """
        comb_index = None
        final_comb_index = None
        for symbol in self.symbol_list:
            # Load the CSV file data of the symbol with no header information, indexed on datetime ascending
            try:
                self.symbol_data[symbol] = pd.read_csv(
                    os.path.join(self.csv_dir, '%s.csv' % symbol),
                    header=0, index_col=0, parse_dates=True,
                    names=[
                        'datetime', 'open', 'high',
                        'low', 'close', 'volume'
                    ]
                ).sort_index()
                # Combine the index to pad forward value
                # Set the latest symbol_data to None
                if comb_index is None:
                    comb_index = self.symbol_data[symbol].index
                else:
                    # idx1.union(idx2)
                    # in order to keep them got the whole datetimes
                    final_comb_index = comb_index.union(self.symbol_data[symbol].index)

                self.latest_symbol_data[symbol] = []

            except:
                print("Doesn't has %s's data" % symbol)

        # Reindex the dataframes
        for s in self.symbol_list:
            # '.iterrows()' ==  change data into a generator in a form of rows
            self.symbol_data_dict = self.symbol_data[s].reindex(index=final_comb_index, method='pad')
            self.symbol_data[s] = self.symbol_data[s].reindex(index=final_comb_index, method='pad').iterrows()

    def _get_new_bar(self, symbol):
        """
        Returns the latest bar from the data feed.
        """
        for b in self.symbol_data[symbol]:
            yield b  # yield a bar in the order of rows

    def get_latest_bar(self, symbol):
        """
        Returns the last bar from the latest_symbol list.
        """
        try:
            bars_list = self.latest_symbol_data[symbol]
        except KeyError:
            print("That symbol is not available in the historical data set.")
            raise
        else:
            return bars_list[-1]

    def get_latest_bars(self, symbol, N=1):
        """
        Returns the last N bars from the latest_symbol list,
        or N-k if less available.
        """
        try:
            bars_list = self.latest_symbol_data[symbol]
        except KeyError:
            print("That symbol is not available in the historical data set.")
            raise
        else:
            return bars_list[-N:]

    def get_latest_bar_datetime(self, symbol):
        """
        Returns a Python datetime object for the last bar.
        """
        try:
            bars_list = self.latest_symbol_data[symbol]
        except KeyError:
            print("That symbol is not available in the historical data set.")
            raise
        else:
            return bars_list[-1][0]

    def get_latest_bar_value(self, symbol, val_type):
        """
        Returns one of the Open, High, Low, Close, Volume or OI
        values from the pandas Bar series object.
        """
        try:
            bars_list = self.latest_symbol_data[symbol]
        except KeyError:
            print("That symbol is not available in the historical data set.")
            raise
        else:
            return getattr(bars_list[-1][1], val_type)

    def get_latest_bars_values(self, symbol, val_type, N=1):
        """
        Returns the last N bar values from the
        latest_symbol list, or N-k if less available.
        """
        try:
            bars_list = self.get_latest_bars(symbol, N)
        except KeyError:
            print("That symbol is not available in the historical data set.")
            raise
        else:
            return np.array([getattr(b[1], val_type) for b in bars_list])

    def update_bars(self):
        """
        Pushes the latest bar to the latest_symbol_data structure
        for all symbols in the symbol list.
        """
        for s in self.symbol_list:
            try:
                bar = next(self._get_new_bar(s))
            except StopIteration:
                self.continue_backtest = False
            else:
                if bar is not None:
                    self.latest_symbol_data[s].append(bar)
                    print(type(self.latest_symbol_data[s]))
                    print(bar)
                    print(type(bar))
        self.events.put(EventMarket())  # when update a list of bars of a new datetime, check the MarketEvent()


if __name__ == '__main__':
    from MySqlio.mysql_api import mysqlio
    from myquant.event.myqueue import myqueue

    host = "localhost"
    port = 3306
    user = "root"
    passwd = "318318"
    db = "future_master"
    table = 'rb1905_1min'
    symbol_list = ['rb1905']
    symbol = symbol_list[0]
    SQLIO = mysqlio(host=host, port=port, user=user, passwd=passwd, db=db)
    data = SQLIO.get_sth_from_mysql(sql="""select ts_code,trade_date,open,high,low,close,vol from rb1905_1min;""")

    q = myqueue()
    TR = RealTradeDataHandler(events=myqueue, symbol_list=['rb1905'], latest_symbol_data=data)

    data = TR.latest_symbol_data[symbol]

    data.columns

    data.loc[pd.Timestamp('20190425 17:01:15')] = {'symbol': 'rb1905', 'open': 4146.0, 'high': 4147.0, 'low': 4146.0,
                                                   'close ': 4147.0, 'volume': 4}
