#!/usr/bin/python
# -*- coding: utf-8 -*-

# event.py

from __future__ import print_function

EVENT_TICK = 'eTick.'  # TICK行情事件，可后接具体的vtSymbol
EVENT_ORDER = 'eOrder.'  # 发送报单
EVENT_POSITION = 'ePosition.'  # 持仓回报事件
EVENT_ACCOUNT = 'eAccount.'  # 账户回报事件
EVENT_ERROR = 'eError.'  # 错误回报事件
EVENT_HISTORY = 'eHistory.'  # K线数据查询回报事件
EVENT_SUBSCRIBE = 'eSubscribe'  # 订阅合约时间
EVENT_INSTRUMENT = 'eInstrument'  # 查询所有合约事件
EVENT_1minBAR = 'e1minbar'  # 新的1minbar
EVENT_ORDERRSP = 'eOrderrsp'  # 保单回报
EVENT_TRADERSP = 'eTradersp'  # 成交回报


class Event:
    """事件对象"""

    # ----------------------------------------------------------------------
    def __init__(self, type_=None):
        """Constructor"""
        self.type_ = type_  # 事件类型
        self.dict_ = {}  # 字典用于保存具体的事件数据


class EventMarket(Event):
    """
    Handles the event of receiving a new market update with
    corresponding bars.
    """

    def __init__(self):
        """
        Initialises the MarketEvent.
        """
        self.type_ = 'MARKET'


class EventSignal(Event):
    """
    Handles the event of sending a Signal from a Strategy object.
    This is received by a Portfolio object and acted upon.
    """

    def __init__(self, strategy_id, symbol, datetime, signal_type, strength, mkt_quantity):
        """
        Initialises the SignalEvent.

        Parameters:
        strategy_id - The unique ID of the strategy sending the signal.
        symbol - The ticker symbol, e.g. 'GOOG'.
        datetime - The timestamp at which the signal was generated.
        signal_type - 'LONG' or 'SHORT'.
        strength - An adjustment factor "suggestion" used to scale
            quantity at the portfolio level. Useful for pairs strategies.
        """

        self.type_ = 'SIGNAL'
        self.symbol = symbol
        self.datetime = datetime
        self.signal_type = signal_type
        self.strength = strength
        self.mkt_quantity = mkt_quantity
        self.strategy_id = strategy_id

        self.dict_ = {str(strategy_id): strategy_id,
                      str(symbol): symbol,
                      str(datetime): datetime,
                      str(signal_type): signal_type,
                      str(strength): strength,
                      str(mkt_quantity): mkt_quantity
                      }


class EventOrder(Event):
    """
    Handles the event of sending an Order to an execution system.
    The order contains a symbol (e.g. GOOG), a type (market or limit),
    quantity and a direction.
    """

    def __init__(self, symbol, order_type, quantity, direction):
        """
        Initialises the order type, setting whether it is
        a Market order ('MKT') or Limit order ('LMT'), has
        a quantity (integral) and its direction ('BUY' or
        'SELL').

        TODO: Must handle error checking here to obtain
        rational orders (i.e. no negative quantities etc).

        Parameters:
        symbol - The instrument to trade.
        order_type - 'MKT' or 'LMT' for Market or Limit.
        quantity - Non-negative integer for quantity.
        direction - 'BUY' or 'SELL' for long or short.
        """
        self.type_ = EVENT_ORDER
        self.dict_ = {str(symbol): symbol,
                      str(order_type): order_type,
                      str(quantity): quantity,
                      str(direction): direction
                      }
        self.symbol = symbol
        self.order_type = order_type
        self.quantity = quantity
        self.direction = direction

    def print_order(self):
        """
        Outputs the values within the Order.
        """
        print(
            "Order: Symbol=%s, Type=%s, Quantity=%s, Direction=%s" %
            (self.symbol, self.order_type, self.quantity, self.direction)
        )


class EventFill(Event):
    """
    Encapsulates the notion of a Filled Order, as returned
    from a brokerage. Stores the quantity of an instrument
    actually filled and at what price. In addition, stores
    the commission of the trade from the brokerage.

    TODO: Currently does not support filling positions at
    different prices. This will be simulated by averaging
    the cost.
    """

    def __init__(self, timeindex, symbol, exchange, quantity,
                 direction, commission, fill_cost):
        """
        Initialises the FillEvent object. Sets the symbol, exchange,
        quantity, direction, cost of fill and an optional
        commission.

        If commission is not provided, the Fill object will
        calculate it based on the trade size and Interactive
        Brokers fees.

        Parameters:
        timeindex - The bar-resolution when the order was filled.
        symbol - The instrument which was filled.
        exchange - The exchange where the order was filled.
        quantity - The filled quantity.
        direction - The direction of fill ('BUY' or 'SELL')
        fill_cost - The holdings value in dollars.
        commission - An optional commission sent from IB.
        """
        self.type_ = 'FILL'
        self.timeindex = timeindex
        self.symbol = symbol
        self.exchange = exchange
        self.quantity = quantity
        self.direction = direction
        self.fill_cost = fill_cost

        # Calculate commission
        if commission is None:  # TODO改交易费用
            self.commission = self.calculate_ib_commission()
        else:
            self.commission = commission

        self.dict_ = {str(timeindex): timeindex,
                      str(symbol): symbol,
                      str(exchange): exchange,
                      str(quantity): quantity,
                      str(direction): direction,
                      str(fill_cost): fill_cost}

    def calculate_ib_commission(self):
        """
        Calculates the fees of trading based on an Interactive
        Brokers fee structure for API, in USD.

        This does not include exchange or ECN fees.

        Based on "US API Directed Orders":
        https://www.interactivebrokers.com/en/index.php?f=commission&p=stocks2
        """
        full_cost = 1.3
        if self.quantity <= 500:
            full_cost = max(1.3, 0.013 * self.quantity)
        else:  # Greater than 500
            full_cost = max(1.3, 0.008 * self.quantity)
        return full_cost