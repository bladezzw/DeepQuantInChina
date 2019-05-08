import socket
import urllib.parse
from contextlib import closing

from ctpwrapper import ApiStructure
from ctpwrapper import TraderApiPy

from myquant.pyqt_ui.Variables_ import *



def check_address_port(tcp):
    """
    :param tcp:
    :return:
    """
    host_schema = urllib.parse.urlparse(tcp)

    ip = host_schema.hostname
    port = host_schema.port

    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        if sock.connect_ex((ip, port)) == 0:
            return True  # OPEN
        else:
            return False  # closed


class Trader(TraderApiPy):

    def __init__(self, broker_id, investor_id, password, engine=EventEngine, request_id=1):
        self.request_id = request_id
        self.broker_id = broker_id.encode()
        self.investor_id = investor_id.encode()
        self.password = password.encode()
        self.orderRef = 0
        self.Instrumentrow = 0
        self.engine = engine  # 事件处理引擎
        self.Instruments = {}  # 接受所有合约的字典
        self.positions = {}  # 接收仓位的字典
        self.orderrsp = {}  # 接受报单的字典
        self.tradersp = {}  # 接收成交单的字典

    def inc_request_id(self):
        """查询顺序编号,每调用一次就+1"""
        self.request_id += 1
        return self.request_id

    def OnRspError(self, pRspInfo, nRequestID, bIsLast):

        self.ErrorRspInfo(pRspInfo, nRequestID)

    def ErrorRspInfo(self, info, request_id):
        """错误响应ErrorRspInfo:"""
        if info.ErrorID != 0:
            print('request_id=%s ErrorID=%d, ErrorMsg=%s',
                  request_id, info.ErrorID, info.ErrorMsg.decode('gbk'))
        return info.ErrorID != 0

    def OnHeartBeatWarning(self, nTimeLapse):
        """心跳超时警告。当长时间未收到报文时，该方法被调用。
        @param nTimeLapse 距离上次接收报文的时间
        """
        print("on OnHeartBeatWarning time: ", nTimeLapse)

    def OnFrontDisconnected(self, nReason):
        """交易前端接入响应"""
        print("交易前端接入on FrontDisConnected disconnected", nReason)

    def OnFrontConnected(self):
        """前端登录响应"""
        req = ApiStructure.ReqUserLoginField(BrokerID=self.broker_id,
                                             UserID=self.investor_id,
                                             Password=self.password)
        self.ReqUserLogin(req, self.request_id)
        print("trader on front connection交易前端连接.")

    def OnRspUserLogin(self, pRspUserLogin, pRspInfo, nRequestID, bIsLast):
        """用户登录响应"""
        if pRspInfo.ErrorID != 0:
            print("交易端 OnRspUserLogin failed error_id=%s msg:%s",
                  pRspInfo.ErrorID, pRspInfo.ErrorMsg.decode('gbk'))
        else:
            print("交易端 user login successfully", nRequestID)

            inv = ApiStructure.QryInvestorField(BrokerID=self.broker_id, InvestorID=self.investor_id)

            self.ReqQryInvestor(inv, self.inc_request_id())
            print("查询投资者信息.", "请求编号:", self.request_id)
            req = ApiStructure.SettlementInfoConfirmField.from_dict({"BrokerID": self.broker_id,
                                                                     "InvestorID": self.investor_id})

            self.ReqSettlementInfoConfirm(req, self.inc_request_id())

    def OnRspSettlementInfoConfirm(self, pSettlementInfoConfirm, pRspInfo, nRequestID, bIsLast):
        """结算信息确认"""
        print("结算信息响应:", pSettlementInfoConfirm, pRspInfo, pRspInfo.ErrorMsg.decode("GBK"))

    def OnRspQryInstrument(self, pInstrument, pRspInfo, nRequestID, bIsLast):
        """查询合约响应"""
        # print("查询合约响应")
        data = Instument(pInstrument)
        self.Instruments.setdefault(data.InstrumentID, data)
        if bIsLast:
            event = Event()
            event.type_ = EVENT_INSTRUMENT
            event.dict_ = self.Instruments
            self.engine.put(event)
            # print("合约s,已经put")

    def OnRspQryInvestor(self, pInvestor, pRspInfo, nRequestID, bIsLast):
        """交易端投资者信息响应"""
        print("查询交易端投资者信息响应 OnRspQryInvestor:", pInvestor, pRspInfo)

    def OnRspQryInvestorPosition(self, pInvestorPosition, pRspInfo, nRequestID, bIsLast):
        """查询持仓回报"""
        # print("查询持仓请求回报", pInvestorPosition)
        Positiondata = Position(pInvestorPosition)
        # print('Positiondata.Position != 0', Positiondata.Position != 0)
        if Positiondata.Position != 0:
            if Positiondata.SymbolDir in self.positions:
                # print('Positiondata.SymbolDir in self.positions', Positiondata.SymbolDir in self.positions)
                self.positions[Positiondata.SymbolDir].YdPosition += Positiondata.YdPosition
                self.positions[Positiondata.SymbolDir].Position += Positiondata.Position
                self.positions[Positiondata.SymbolDir].PositionCost += Positiondata.PositionCost
                self.positions[Positiondata.SymbolDir].UseMargin += Positiondata.UseMargin
                self.positions[Positiondata.SymbolDir].OpenCost += Positiondata.OpenCost
                self.positions[Positiondata.SymbolDir].PositionProfit += Positiondata.PositionProfit
                self.positions[Positiondata.SymbolDir].CloseProfit += Positiondata.CloseProfit
            else:
                # 如果self.positions中没有该仓位的信息,
                # 则创建该字典的key为Positiondata.SymbolDir,value为Positiondata(Position类)
                self.positions.setdefault(Positiondata.SymbolDir, Positiondata)

        if bIsLast:
            event = Event()
            event.type_ = EVENT_POSITION
            event.dict_ = self.positions
            self.engine.put(event)
            self.positions = {}

    def OnRspQryTradingAccount(self, data, error, n, last):
        """资金账户查询回报"""
        event = Event()
        event.type_ = EVENT_ACCOUNT
        event.dict_ = data
        self.engine.put(event)

    def OnRspQryOrder(self, pOrder, pRspInfo, nRequestID, bIsLast):
        """报单查询回报"""
        print("OnRspQryOrder报单查询回报:", pOrder, "pRspInfo:", pRspInfo, "nRequestID", nRequestID,
              "是否结束", bIsLast)
        if pOrder:
            Orderrsp = OrderOnRsp(pOrder)
            self.orderrsp.setdefault(Orderrsp.OrderLocalID, Orderrsp)
            if bIsLast:
                event = Event()
                event.type_ = EVENT_ORDERRSP
                event.dict_ = self.orderrsp
                self.engine.put(event)

    def OnRspQryTrade(self, pTrade, pRspInfo, nRequestID, bIsLast):
        """成交查询回报"""
        print("OnRspQryTrade成交查询回报:", pTrade, "pRspInfo:", pRspInfo, "nRequestID", nRequestID,
              "是否结束", bIsLast)
        if pTrade:
            Tradersp = TradeRsp(pTrade)
            self.tradersp.setdefault(Tradersp.TradeID, Tradersp)
            if bIsLast:
                event = Event()
                event.type_ = EVENT_TRADERSP
                event.dict_ = self.tradersp
                self.engine.put(event)

    def OnRspOrderInsert(self, pInputOrder, pRspInfo, nRequestID, bIsLast):
        """报单回报"""
        print("OnRspOrderInsert报单录入回报:", pInputOrder, ".是否结束", bIsLast)

    def OnRtnOrder(self, pOrder):
        print("报单录入或保单状态变化时回报:", pOrder)
        if pOrder:
            Orderrsp = OrderOnRsp(pOrder)
            self.orderrsp.setdefault(Orderrsp.OrderLocalID, Orderrsp)
            event = Event()
            event.type_ = EVENT_ORDERRSP
            event.dict_ = self.orderrsp
            self.engine.put(event)

    def OnRspOrderAction(self, pInputOrderAction, pRspInfo, nRequestID, bIsLast):
        """撤单响应"""
        print("撤单响应:", pInputOrderAction, "--------", pRspInfo)

    def OnRtnTrade(self, pTrade):
        print("所报单成交回报:", pTrade)
        if pTrade:
            Tradersp = TradeRsp(pTrade)
            self.tradersp.setdefault(Tradersp.TradeID, Tradersp)
            event = Event()
            event.type_ = EVENT_TRADERSP
            event.dict_ = self.tradersp
            self.engine.put(event)

    def OnErrRtnOrderInsert(self, pInputOrder, pRspInfo):
        """发单错误回报（交易所）"""
        print("发单错误回报:", pInputOrder, pRspInfo)

    def OnErrRtnOrderAction(self, pOrderAction, pRspInfo):
        """撤单错误回报（交易所）"""
        print("撤单错误回报（交易所）:", pOrderAction, pRspInfo)

    def reqQryOrder(self):
        """查询报单请求"""
        pQryOrder = ApiStructure.QryOrderField.from_dict({
            "InvestorID": self.investor_id,
            "BrokerID": self.broker_id
        })
        self.ReqQryOrder(pQryOrder, self.inc_request_id())

    def reqQryTrade(self):
        """查询成交请求"""
        pQryTrade = ApiStructure.QryTradeField.from_dict({
            "BrokerID": self.broker_id,
            "InvestorID": self.investor_id
        })

        self.ReqQryTrade(pQryTrade, self.inc_request_id())

    def reqQryInstrument(self):
        """查询合约"""
        req = ApiStructure.QryInstrumentField()
        self.ReqQryInstrument(req, self.inc_request_id())

    # --------------------------------------------------------------#
    def reqQryInvestorPosition(self, event):  # 可用
        """查询持仓请求"""
        pQryInvestorPosition = ApiStructure.QryInvestorPositionDetailField(
            BrokerID=self.broker_id,
            InvestorID=self.investor_id
        )
        reqID = self.inc_request_id()
        if reqID % 2 == 0:  # 每秒只支持一次查询,故和资金查询错开.
            self.ReqQryInvestorPosition(pQryInvestorPosition, reqID)
        # print("查询持仓请求已发出编号:",self.request_id)

    # --------------------------------------------------------------#
    def reqQryTadingAccount(self, event):  # 可用
        """查询资金账户"""
        req = ApiStructure.QryInvestorField.from_dict({'BrokerID': self.broker_id,  # 经纪公司代码
                                                       'InvestorID': self.investor_id  # 投资者代码})
                                                       })
        reqID = self.request_id
        if reqID % 2 != 0:  # 每秒只支持一次查询,故和资金查询错开.
            self.ReqQryTradingAccount(req, reqID)
        # print("查询资金账户:", self.request_id)

    # --------------------------------------------------------------#
    def orderInsert(self, event):  # 可用
        """发单"""
        orderReq = event.dict_
        reqID = self.inc_request_id()
        self.orderRef += 1
        # self.orderRef += self.inc_request_id()#发单次数+1
        req = {}
        req['CombOffsetFlag'] = orderReq.offset  # 默认开仓
        req["TimeCondition"] = defineDict['THOST_FTDC_TC_GFD']  # 默认当日有效
        req['OrderPriceType'] = orderReq.priceType  # 默认限价
        req['VolumeCondition'] = defineDict['THOST_FTDC_VC_AV']  # 默认1手

        # 判断FAK和FOK.
        # FOK立即全部成交否则自动撤销指令,指在限定价位下达指令,如果该指令下所有申报手数未能全部成交,
        # 该指令下所有申报手数自动被系统撤销.
        # FAK立即成交申报价位的指令,剩余的自动撤销.
        # # 任何数量
        # defineDict["THOST_FTDC_VC_AV"] = '1'
        # # 最小数量
        # defineDict["THOST_FTDC_VC_MV"] = '2'
        # # 全部数量
        # defineDict["THOST_FTDC_VC_CV"] = '3'
        if orderReq.priceType == '1':
            req['OrderPriceType'] = defineDict["THOST_FTDC_OPT_LimitPrice"]  # 限价
            req['TimeCondition'] = defineDict['THOST_FTDC_TC_IOC']  # 立即完成否则撤销
            req['VolumeCondition'] = defineDict['THOST_FTDC_VC_AV']  # 任何数量
        if orderReq.priceType == '3':
            req['OrderPriceType'] = defineDict["THOST_FTDC_OPT_LimitPrice"]  # 限价
            req['TimeCondition'] = defineDict['THOST_FTDC_TC_IOC']  # 立即完成否则撤销
            req['VolumeCondition'] = int(defineDict['THOST_FTDC_VC_CV'])  # 全部数量

        pInputOrder = ApiStructure.InputOrderField.from_dict({
            'BrokerID': self.broker_id,
            'InvestorID': self.investor_id,
            'InstrumentID': orderReq.symbol,
            'OrderRef': self.orderRef,
            'UserID': self.investor_id,

            'OrderPriceType': req['OrderPriceType'],
            'Direction': orderReq.direction,
            'CombOffsetFlag': req['CombOffsetFlag'],
            'CombHedgeFlag': defineDict['THOST_FTDC_HF_Speculation'],
            'LimitPrice': orderReq.price,
            'VolumeTotalOriginal': int(orderReq.volume),
            'TimeCondition': req['TimeCondition'],

            'VolumeCondition': req['VolumeCondition'],
            'MinVolume': 1,
            'ContingentCondition': defineDict['THOST_FTDC_CC_Immediately'],
            'ForceCloseReason': defineDict['THOST_FTDC_FCC_NotForceClose'],
            'IsAutoSuspend': 0,
            'VolumeCondition': req['VolumeCondition']
        })

        self.ReqOrderInsert(pInputOrder=pInputOrder, nRequestID=reqID)
        return self.orderRef

    def ordercancel(self, event):
        """
        撤单 TODO:to be revised
        """
        cancelOrderReq = event.dict_
        self.request_id += self.inc_request_id()

        pQryOder = ApiStructure.InputOrderActionField.from_dict({
            "InstrumentID": cancelOrderReq.symbol,
            "ExchangeID": cancelOrderReq.exchange,
            "OrderRef": 1,
            "FrontID": cancelOrderReq.frontID,
            "SessionID": cancelOrderReq.sessionID,
            "ActionFlag": defineDict['THOST_FTDC_AF_Delete'],
            "BrokerID": self.broker_id,
            "InvestorID": self.investor_id
        })
        self.ReqOrderAction(pQryOder, self.request_id)

        # pQryOrder = ApiStructure.QryOrderField.from_dict({
        #     "InvestorID": self.investor_id,
        #     "BrokerID": self.broker_id
        # })
        # self.ReqQryOrder(pQryOrder, self.inc_request_id())

        # "VolumeChange": cancelOrderReq.volumechange,
        # "OrderSysID": cancelOrderReq.OrderSysID

if __name__ == "__main__":
    from myquant.event.myqueue import myqueue
    ee = myqueue()
    investor_id = "092122"
    broker_id = "9999"
    password = "698955"
    server = "tcp://218.202.237.33 :10002"

    if check_address_port(server):

        user_trader = Trader(broker_id=broker_id, investor_id=investor_id, password=password, engine=ee)

        user_trader.Create()
        user_trader.RegisterFront(server)
        user_trader.SubscribePrivateTopic(2)  # 只传送登录后的流内容
        user_trader.SubscribePrivateTopic(2)  # 只传送登录后的流内容

        user_trader.Init()

        print("trader started")
        print(user_trader.GetTradingDay())

        user_trader.reqQryTadingAccount(None)  # 包装函数

        user_trader.reqQryInvestorPosition(None)

        user_trader.reqQryInvestorPosition(None)

        # 报单模板:
        orderReq = OrderReq()

        orderReq.symbol = 'rb1905'  # 代码
        orderReq.direction = directionMap[DIRECTION_SHORT]  # 买卖
        orderReq.exchange = exchangeMap[EXCHANGE_SHFE]  # 交易所
        orderReq.price = float(3990)  # 价格
        orderReq.volume = 1  # 数量
        orderReq.priceType = priceTypeMap[PRICETYPE_LIMITPRICE]  # 价格类型
        orderReq.offset = offsetMap[OFFSET_OPEN]  # 开平

        user_trader.orderInsert(orderReq)


        # 撤单模板:
        cancelOrderReq = CancelOrderReq()
        cancelOrderReq.symbol = 'rb1910'
        cancelOrderReq.exchange = exchangeMap[EXCHANGE_SHFE]
        cancelOrderReq.frontID = '5'
        cancelOrderReq.sessionID = '-152110344'
        # cancelOrderReq.OrderSysID = '90287'
        # cancelOrderReq.volumechange = 1


        event = Event()
        event.dict_ = cancelOrderReq
        user_trader.ordercancel(event)

    else:
        print("trader server down")
