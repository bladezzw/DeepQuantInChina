import sys
import copy
import time
from ctpwrapper import ApiStructure
from ctpwrapper import MdApiPy

from myquant.pyqt_ui.Variables_ import *


class Md(MdApiPy):
    """
    """

    def __init__(self, broker_id, investor_id, password, engine, request_id=1):

        self.broker_id = broker_id
        self.investor_id = investor_id
        self.password = password
        self.request_id = request_id
        self.subscribeReq = {}
        self.id = 1
        self.engine = engine
        self.cachetick = {}  # 缓存tick数据
        self.bar = {}  # 缓存bar数据
        self.firsttick = {}  # 缓存bar的第一个tick数据
        self.t1 = {}  # 用于判断newtick的时间
        self.t2 = {}  # 用于判断newtick的时间

    def OnRspError(self, pRspInfo, nRequestID, bIsLast):

        self.ErrorRspInfo(pRspInfo, nRequestID)

    def ErrorRspInfo(self, info, request_id):
        """
        :param info:
        :return:
        """
        if info.ErrorID != 0:
            print('request_id=%s ErrorID=%d, ErrorMsg=%s',
                  request_id, info.ErrorID, info.ErrorMsg.decode('gbk'))
        return info.ErrorID != 0

    def OnFrontConnected(self):
        """
        :return:
        """

        user_login = ApiStructure.ReqUserLoginField(BrokerID=self.broker_id,
                                                    UserID=self.investor_id,
                                                    Password=self.password)
        self.ReqUserLogin(user_login, self.request_id)

    def OnFrontDisconnected(self, nReason):

        print("行情端 OnFrontDisconnected %s", nReason)
        sys.exit()

    def OnHeartBeatWarning(self, nTimeLapse):
        """心跳超时警告。当长时间未收到报文时，该方法被调用。
        @param nTimeLapse 距离上次接收报文的时间
        """
        print('行情端 OnHeartBeatWarning, time = %s', nTimeLapse)

    def OnRspUserLogin(self, pRspUserLogin, pRspInfo, nRequestID, bIsLast):
        """
        用户登录应答
        :param pRspUserLogin:
        :param pRspInfo:
        :param nRequestID:
        :param bIsLast:
        :return:
        """
        if pRspInfo.ErrorID != 0:
            print("Md OnRspUserLogin failed error_id=%s msg:%s",
                  pRspInfo.ErrorID, pRspInfo.ErrorMsg.decode('gbk'))
        else:
            print("Md user login successfully")
            print(pRspUserLogin)
            print(pRspInfo)

    # ---------------------------------------------------------------------------#
    def tosubscribe(self, event):
        """tosubscribe"""
        ppInstrumentID = list(self.subscribeReq)
        self.SubscribeMarketData(ppInstrumentID)

    def OnRtnDepthMarketData(self, DepthData):
        """深度行情通知"""
        newtick = TickData(DepthData)
        qEvent = Event()
        qEvent.type_ = EVENT_TICK
        qEvent.dict_ = newtick
        self.engine.put(qEvent)
        self.ticktobar(newtick)

    def ticktobar(self, newtick):
        """处理tick数据,导出1min线"""

        symbol = newtick.InstrumentID
        if symbol not in self.cachetick:
            # print("没有", symbol, "的数据,现在创建")
            self.firsttick[symbol] = {}
            self.firsttick[symbol]['Date'] = newtick.Date
            self.firsttick[symbol]["symbol"] = newtick.InstrumentID
            self.firsttick[symbol]["symbol"] = newtick.InstrumentID
            self.firsttick[symbol]["Time"] = newtick.UpdateTime
            self.firsttick[symbol]["price"] = [newtick.LastPrice]
            self.firsttick[symbol]["volume"] = newtick.Volume
            self.cachetick[symbol] = copy.deepcopy(self.firsttick[symbol])
        self.cachetick[symbol]["price"].append(newtick.LastPrice)
        # print('cachetick:', self.cachetick[symbol])

        self.t1[symbol] = time.mktime(time.strptime(self.firsttick[symbol]["Time"], "%H:%M:%S"))
        self.t2[symbol] = time.mktime(time.strptime(newtick.UpdateTime, "%H:%M:%S"))

        # print('时差', self.t2[symbol] - self.t1[symbol])
        if self.t2[symbol] - self.t1[symbol] >= 5:  # TODO:为了测试是实盘进程改成5s, 记得改回59.5
            self.bar[symbol] = {}
            self.bar[symbol]["symbol"] = symbol
            self.bar[symbol]["Date"] = self.firsttick[symbol]["Date"]
            self.bar[symbol]["Time"] = newtick.UpdateTime
            self.bar[symbol]["open"] = self.firsttick[symbol]["price"][0]
            self.bar[symbol]["high"] = max(self.cachetick[symbol]["price"])
            self.bar[symbol]["low"] = min(self.cachetick[symbol]["price"])
            self.bar[symbol]["close"] = newtick.LastPrice
            self.bar[symbol]["volume"] = newtick.Volume - self.firsttick[symbol]["volume"]
            self.bar[symbol]["LowerLimitPrice"] = newtick.LowerLimitPrice
            self.bar[symbol]["UpperLimitPrice"] = newtick.UpperLimitPrice

            # print("1min bar:", self.bar[symbol])
            event = Event()
            event.type_ = EVENT_1minBAR
            event.dict_ = self.bar[symbol]
            # print("%s的数据:" % symbol, self.bar[symbol])
            self.engine.put(event)
            self.cachetick.pop(symbol)
            self.firsttick.pop(symbol)
            self.bar.pop(symbol)



if __name__ == "__main__":
    BORDKER_ID = "9999"
    INVESTOR_ID = ""
    PASSWORD = ""
    SERVER = "tcp://180.168.146.187:10031"
    ppInstrumentID = ["rb1905"]  # 上海和大连的小写, 郑州的大写,行情订阅列表
    iInstrumentID = 1  # 行情订阅数量

    md = Md(BORDKER_ID, INVESTOR_ID, PASSWORD)
    md.Create()
    md.RegisterFront(SERVER)

    md.Init()
    day = md.GetTradingDay()

    print(day)
    print("api worker!")

    InstrumentField = ["rb1905"]
    # InstrumentField.appen(
    md.tosubscribe(InstrumentField)  # 订阅行情,等个10秒左右吧?好像是tcp连接的原因,如果获取过多会出现NULL的情况,

    md.Join()
