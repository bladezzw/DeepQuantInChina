from myquant.event.eventEngine import *
from queue import Queue
from myquant.pyqt_ui.constant import *

import datetime
from myquant.pyqt_ui.ctp_data_type import defineDict


# 系统相关
EVENT_TIMER = 'eTimer'  # 计时器事件，每隔1秒发送一次
EVENT_LOG = 'eLog'  # 日志事件，全局通用

# Gateway相关
EVENT_TICK = 'eTick'  # TICK行情事件，可后接具体的vtSymbol
EVENT_ORDER = 'eOrder'  # 发送报单
EVENT_POSITION = 'ePosition'  # 持仓回报事件
EVENT_ACCOUNT = 'eAccount'  # 账户回报事件
EVENT_ERROR = 'eError'  # 错误回报事件
EVENT_HISTORY = 'eHistory'  # K线数据查询回报事件
EVENT_SUBSCRIBE = 'eSubscribe'  # 订阅合约时间
EVENT_INSTRUMENT = 'eInstrument'  # 查询所有合约事件
EVENT_1minBAR = 'e1minbar'  # 新的1minbar
EVENT_ORDERRSP = 'eOrderrsp'  # 保单回报
EVENT_TRADERSP = 'eTradersp'  # 成交回报
EVENT_ORDERACTION = 'eOrderCancel'  # 撤单


# 以下为一些VT类型和CTP类型的映射字典
# 价格类型映射orderReq.priceType
priceTypeMap = {}
priceTypeMap[PRICETYPE_LIMITPRICE] = defineDict["THOST_FTDC_OPT_LimitPrice"]
priceTypeMap[PRICETYPE_MARKETPRICE] = defineDict["THOST_FTDC_OPT_AnyPrice"]
priceTypeMapReverse = {v: k for k, v in priceTypeMap.items()}

# 方向类型映射orderReq.direction
directionMap = {}
directionMap[DIRECTION_LONG] = defineDict['THOST_FTDC_D_Buy']
directionMap[DIRECTION_SHORT] = defineDict['THOST_FTDC_D_Sell']
directionMapReverse = {v: k for k, v in directionMap.items()}

# 开平类型映射orderReq.offset
offsetMap = {}
offsetMap[OFFSET_OPEN] = defineDict['THOST_FTDC_OF_Open']
offsetMap[OFFSET_CLOSE] = defineDict['THOST_FTDC_OF_Close']
offsetMap[OFFSET_CLOSETODAY] = defineDict['THOST_FTDC_OF_CloseToday']
offsetMap[OFFSET_CLOSEYESTERDAY] = defineDict['THOST_FTDC_OF_CloseYesterday']
offsetMapReverse = {v: k for k, v in offsetMap.items()}

# 交易所类型映射orderReq.exchange
exchangeMap = {}
exchangeMap[EXCHANGE_CFFEX] = 'CFFEX'
exchangeMap[EXCHANGE_SHFE] = 'SHFE'
exchangeMap[EXCHANGE_CZCE] = 'CZCE'
exchangeMap[EXCHANGE_DCE] = 'DCE'
exchangeMap[EXCHANGE_SSE] = 'SSE'
exchangeMap[EXCHANGE_SZSE] = 'SZSE'
exchangeMap[EXCHANGE_INE] = 'INE'
exchangeMap[EXCHANGE_UNKNOWN] = ''
exchangeMapReverse = {v: k for k, v in exchangeMap.items()}

# 持仓类型映射
posiDirectionMap = {}
posiDirectionMap[DIRECTION_NET] = defineDict["THOST_FTDC_PD_Net"]
posiDirectionMap[DIRECTION_LONG] = defineDict["THOST_FTDC_PD_Long"]
posiDirectionMap[DIRECTION_SHORT] = defineDict["THOST_FTDC_PD_Short"]
posiDirectionMapReverse = {v: k for k, v in posiDirectionMap.items()}

# 产品类型映射
productClassMap = {}
productClassMap[PRODUCT_FUTURES] = defineDict["THOST_FTDC_PC_Futures"]
productClassMap[PRODUCT_OPTION] = defineDict["THOST_FTDC_PC_Options"]
productClassMap[PRODUCT_COMBINATION] = defineDict["THOST_FTDC_PC_Combination"]
productClassMapReverse = {v: k for k, v in productClassMap.items()}
productClassMapReverse[defineDict["THOST_FTDC_PC_ETFOption"]] = PRODUCT_OPTION
productClassMapReverse[defineDict["THOST_FTDC_PC_Stock"]] = PRODUCT_EQUITY

# 委托状态映射
statusMap = {}
statusMap[STATUS_ALLTRADED] = defineDict["THOST_FTDC_OST_AllTraded"]
statusMap[STATUS_PARTTRADED] = defineDict["THOST_FTDC_OST_PartTradedQueueing"]
statusMap[STATUS_NOTTRADED] = defineDict["THOST_FTDC_OST_NoTradeQueueing"]
statusMap[STATUS_CANCELLED] = defineDict["THOST_FTDC_OST_Canceled"]
statusMapReverse = {v: k for k, v in statusMap.items()}


class OrderReq(object):
    """发单时传入的对象类"""

    # ----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        self.symbol = EMPTY_STRING  # 代码
        self.exchange = EMPTY_STRING  # 交易所
        self.price = EMPTY_FLOAT  # 价格
        self.volume = EMPTY_INT  # 数量

        self.priceType = EMPTY_STRING  # 价格类型
        self.direction = EMPTY_STRING  # 买卖
        self.offset = EMPTY_STRING  # 开平


class CancelOrderReq(object):
    """撤单时传入的对象类"""

    # ----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        self.symbol = EMPTY_STRING  # 代码
        self.exchange = EMPTY_STRING  # 交易所

        # 以下字段主要和CTP、LTS类接口相关
        self.volumechange = 0
        self.orderID = EMPTY_STRING  # 报单号
        self.frontID = EMPTY_STRING  # 前置机号
        self.sessionID = EMPTY_STRING  # 会话号


class Position(object):
    """持仓类"""

    def __init__(self, position_):
        self.TradingDay = position_.TradingDay.decode("utf-8").__str__()
        self.InstrumentID = position_.InstrumentID.decode("utf-8").__str__()
        self.PosiDirection = position_.PosiDirection.__str__()
        self.YdPosition = position_.YdPosition
        # 净
        defineDict["THOST_FTDC_PD_Net"] = '1'
        # 多头
        defineDict["THOST_FTDC_PD_Long"] = '2'
        # 空头
        defineDict["THOST_FTDC_PD_Short"] = '3'
        if position_.PosiDirection == b'2':
            self.PosiDirection = '多'
        elif position_.PosiDirection == b'3':
            self.PosiDirection = '空'

        self.Position = position_.Position
        self.OpenAmount = position_.OpenAmount.__str__()
        self.ShortFrozenAmount = position_.ShortFrozenAmount.__str__()
        self.LongFrozenAmount = position_.LongFrozenAmount.__str__()
        self.PositionProfit = position_.PositionProfit.__str__()
        self.CloseProfit = position_.CloseProfit
        self.Commission = position_.Commission.__str__()
        self.PositionCost = position_.PositionCost
        self.UseMargin = position_.UseMargin
        self.OpenCost = position_.OpenCost
        self.PositionProfit = position_.PositionProfit
        self.SymbolDir = self.InstrumentID + self.PosiDirection


class TickData:
    """Tick行情数据类"""

    def __init__(self, DepthData):
        self.InstrumentID = DepthData.InstrumentID.decode("utf-8").__str__()
        self.PreOpenInterest = DepthData.PreOpenInterest
        self.PreClosePrice = DepthData.PreClosePrice
        self.Turnover = DepthData.Turnover
        self.ClosePrice = DepthData.ClosePrice
        self.UpdateTime = DepthData.UpdateTime.decode("utf-8")
        self.ExchangeID = DepthData.ExchangeID
        self.LastPrice = DepthData.LastPrice
        self.Volume = DepthData.Volume
        self.OpenInterest = DepthData.OpenInterest
        # 上期所和郑商所可以直接使用，大商所需要转换
        self.Date = DepthData.ActionDay.decode("utf-8")
        self.OpenPrice = DepthData.OpenPrice
        self.HighestPrice = DepthData.HighestPrice
        self.LowestPrice = DepthData.LowestPrice
        self.PreClosePrice = DepthData.PreClosePrice
        self.UpperLimitPrice = DepthData.UpperLimitPrice
        self.LowerLimitPrice = DepthData.LowerLimitPrice
        # CTP只有一档行情
        self.BidPrice1 = DepthData.BidPrice1
        self.BidVolume1 = DepthData.BidVolume1
        self.AskPrice1 = DepthData.AskPrice1
        self.AskVolume1 = DepthData.AskVolume1
        # 大商所日期转换
        if self.ExchangeID == EXCHANGE_DCE:
            self.Date = datetime.datetime.now().strftime('%Y%m%d')
        # 上交所，SSE，股票期权相关
        if self.ExchangeID == EXCHANGE_SSE:
            self.BidPrice2 = DepthData.BidPrice2
            self.BidVolume2 = DepthData.BidVolume2
            self.AskPrice2 = DepthData.AskPrice2
            self.AskVolume2 = DepthData.AskVolume2
            self.BidPrice3 = DepthData.BidPrice3
            self.BidVolume3 = DepthData.BidVolume3
            self.AskPrice3 = DepthData.AskPrice3
            self.AskVolume3 = DepthData.AskVolume3
            self.BidPrice4 = DepthData.BidPrice4
            self.BidVolume4 = DepthData.BidVolume4
            self.AskPrice4 = DepthData.AskPrice4
            self.AskVolume4 = DepthData.AskVolume4
            self.BidPrice5 = DepthData.BidPrice5
            self.BidVolume5 = DepthData.BidVolume5
            self.AskPrice5 = DepthData.AskPrice5
            self.AskVolume5 = DepthData.AskVolume5


class Instument:
    """合约类"""

    def __init__(self, pInstrument):
        self.InstrumentID = pInstrument.InstrumentID.decode("utf-8").__str__()
        self.ExchangeID = pInstrument.ExchangeID.decode("utf-8").__str__()
        self.MinLimitOrderVolume = pInstrument.MinLimitOrderVolume.__str__()
        self.MinMarketOrderVolume = pInstrument.MinMarketOrderVolume.__str__()
        self.PriceTick = pInstrument.PriceTick.__str__()
        self.ExpireDate = pInstrument.ExpireDate.decode("utf-8").__str__()
        self.ShortMarginRatio = pInstrument.ShortMarginRatio.__str__()
        self.LongMarginRatio = pInstrument.LongMarginRatio.__str__()
        self.VolumeMultiple = pInstrument.VolumeMultiple.__str__()
        self.StartDelivDate = pInstrument.StartDelivDate.decode("utf-8").__str__()


class OrderOnRsp:
    """返回的报单类"""

    def __init__(self, RspOrder):
        self.BrokerID = RspOrder.BrokerID.decode("utf-8").__str__()
        self.InvestorID = RspOrder.InvestorID.decode("utf-8").__str__()
        self.InstrumentID = RspOrder.InstrumentID.decode("utf-8").__str__()
        self.LimitPrice = RspOrder.LimitPrice.__str__()
        self.VolumeTotalOriginal = RspOrder.VolumeTotalOriginal.__str__()
        self.ExchangeID = RspOrder.ExchangeID.__str__()

        self.offsetflag = RspOrder.CombOffsetFlag.decode("utf-8").__str__()
        if self.offsetflag == defineDict["THOST_FTDC_OFEN_Open"]:
            self.offsetflag = '开仓'
        else:
            self.offsetflag = '平仓'

        self.Direction = RspOrder.Direction.decode("utf-8").__str__()
        if self.Direction == '0':
            self.Direction = '买'
        else:
            self.Direction = '卖'

        self.OrderLocalID = RspOrder.OrderLocalID.decode("utf-8").__str__()  # 唯一,可以以此区分报单

        self.OrderSubmitStatus = RspOrder.OrderSubmitStatus.decode("utf-8").__str__()
        if self.OrderSubmitStatus == '0':
            self.OrderSubmitStatus = '已经提交'
        elif self.OrderSubmitStatus == '1':
            self.OrderSubmitStatus = '撤单已经提交'
        elif self.OrderSubmitStatus == '2':
            self.OrderSubmitStatus = '修改已经提交'
        elif self.OrderSubmitStatus == '3':
            self.OrderSubmitStatus = '已经接受'
        elif self.OrderSubmitStatus == '4':
            self.OrderSubmitStatus = '报单已经被拒绝'
        elif self.OrderSubmitStatus == '5':
            self.OrderSubmitStatus = '撤单已经被拒绝'
        elif self.OrderSubmitStatus == '6':
            self.OrderSubmitStatus = '改单已经被拒绝'

        self.OrderSysID = RspOrder.OrderSysID.decode("utf-8").__str__()

        self.OrderStatus = RspOrder.OrderStatus.decode("utf-8").__str__()
        if self.OrderStatus == defineDict["THOST_FTDC_OST_AllTraded"]:
            self.OrderStatus = '全部成交'
        elif self.OrderStatus == defineDict["THOST_FTDC_OST_PartTradedQueueing"]:
            self.OrderStatus = '部分成交还在队列中'
        elif self.OrderStatus == defineDict["THOST_FTDC_OST_PartTradedNotQueueing"]:
            self.OrderStatus = '部分成交不在队列中'
        elif self.OrderStatus == defineDict["THOST_FTDC_OST_NoTradeQueueing"]:
            self.OrderStatus = '未成交还在队列中'
        elif self.OrderStatus == defineDict["THOST_FTDC_OST_NoTradeNotQueueing"]:
            self.OrderStatus = '未成交不在队列中'
        elif self.OrderStatus == defineDict["THOST_FTDC_OST_Canceled"]:
            self.OrderStatus = '撤单'
        elif self.OrderStatus == defineDict["THOST_FTDC_OST_Unknown"]:
            self.OrderStatus = '未知'
        elif self.OrderStatus == defineDict["THOST_FTDC_OST_NotTouched"]:
            self.OrderStatus = '尚未触发'
        elif self.OrderStatus == defineDict["THOST_FTDC_OST_Touched"]:
            self.OrderStatus = '已触发'

        self.VolumeTraded = RspOrder.VolumeTraded.__str__()
        self.Datetime = (RspOrder.InsertDate + b' ' + RspOrder.InsertTime).decode('utf-8').__str__()
        self.SequenceNo = RspOrder.SequenceNo.__str__()
        self.SessionID = RspOrder.SessionID.__str__()
        self.FrontID = RspOrder.FrontID.__str__()

        self.StatusMsg = RspOrder.StatusMsg.decode("gbk").__str__()
        self.DirOffset = self.Direction + self.offsetflag


class TradeRsp:
    """成交单回报类"""
    def __init__(self, RspTrade):
        self.InstrumentID = RspTrade.InstrumentID.decode("utf-8").__str__()
        self.TradeID = RspTrade.TradeID.decode("utf-8")

        self.Direction = RspTrade.Direction.decode("utf-8")
        if self.Direction == '0':
            self.Direction = '买'
        else:
            self.Direction = '卖'

        self.Price = RspTrade.Price.__str__()

        self.OffsetFlag = RspTrade.OffsetFlag.decode("utf-8")
        if self.OffsetFlag == defineDict["THOST_FTDC_OFEN_Open"]:
            self.OffsetFlag = '开仓'
        else:
            self.OffsetFlag = '平仓'

        self.Volume = RspTrade.Volume.__str__()
        self.TradeDate = RspTrade.TradeDate.decode("utf-8")
        self.TradeTime = RspTrade.TradeTime.decode("utf-8")
        self.Datetime = (RspTrade.TradeDate + b' ' + RspTrade.TradeTime).decode('utf-8').__str__()
        self.OrderSysID = RspTrade.OrderSysID.decode("utf-8")