from myquant.pyqt_ui.Ui_MainWindow import *
from PyQt5.QtWidgets import QApplication, QMessageBox
import traceback
import json
import multiprocessing

from myquant.pyqt_ui.tdapi import *
from myquant.pyqt_ui.mdapi import *
from myquant.pyqt_ui.Variables_ import *
from myquant.pyqt_ui.Ui_Info import Ui_info

from myquant.pyqt_ui.__Functions import (FilePath, Json_loading)
from myquant.pyqt_ui.constant import *
from myquant.event import *
from myquant.pyqt_ui.Ui_Backtesting import Ui_Backtesting
from myquant.pyqt_ui.Ui_RealTrade import Ui_Real_Trade
from backtesting import data, portfolio, execution
from Strategy import strategy
from MySqlio.mysql_api import mysqlio
from myquant.event.myqueue import myqueue

ctploginsettingpath = FilePath("CTPLogin.json")
ctploginsetting = Json_loading(ctploginsettingpath)

q_bar = multiprocessing.Queue()  # 连接主进程和实盘策略进程的bar与order数据传递
q_order = multiprocessing.Queue()


class MainWindow(Ui_MainWindow):
    """
    Class documentation goes here.
    """

    def __init__(self):
        super(Ui_MainWindow, self).__init__()
        self.setupUi(self)
        self.TDEdit.setText(ctploginsetting["tdAddress"])
        self.MDEdit.setText(ctploginsetting["mdAddress"])
        self.BIDEdit.setText(ctploginsetting["brokerID"])
        self.PWEdit.setText(ctploginsetting["password"])
        self.USEREdit.setText(ctploginsetting["userID"])

        self.ismdConnected = False  # 判断是否登录ctp
        self.istdConnected = False

        self.orderdirection = 0  # 开单方向属性 :0,1,2 1开多,2开空,0
        self.orderoffsettype = 0  # 平单: 0开仓,1平今,2平昨
        self.orderpricetype = 1  # 开平单 限价与市价属性: 1市价, 2限价.

        self.Instrumentrow = 0  # 填充合约列表的时候从0,即第一行,开始填充

        self.is_datacollect_on = False  # 默认关闭数据收集服务
        self.is_real_trade_on = False  # 默认关闭实盘交易的数据传递

        self.tableWidget_DepthMarket.itemClicked.connect(self._tableDepthMarketItem_OnClicked)  # 行情板信号连接
        self.tableWidget_Instrument.itemDoubleClicked.connect(self._tableDepthMarketItem_DoubleClicked)  # 行情板信号连接
        self.tableWidget_onrtnorder.itemDoubleClicked.connect(self._tableOnRtnOrderAction_DoubelClicked)  # 双击撤单

        self.actionInfo.triggered.connect(self.InfoUI)
        self.actionHelp.triggered.connect(self.HelpUI)
        self.actionContact.triggered.connect(self.ContactUI)

        # self.MainBoardtickonBid = ""  # eg:"rb1905"控制下单板显示该单个合约tick行情

        self.ee = EventEngine()

        [self.tableWidget_Account.setItem(i, 0, QtWidgets.QTableWidgetItem()) for i in range(7)]  # 创建资金账户的表格items

        self.Ui_Backtesting = Ui_Backtesting()
        self.Ui_Backtesting.setupUi(self.Ui_Backtesting)


    # ---------------------------------------------------------------------------------------------------------
    def InfoUI(self):
        """显示菜单栏INFO的信息"""
        self.a = Ui_info()
        self.a.setupUi(self.a)
        self.a.show()
        print(1)

    def HelpUI(self):
        """显示菜单栏Help的信息"""
        QMessageBox.aboutQt(self)

    def ContactUI(self):
        """显示菜单栏Contact的信息"""
        QMessageBox.information(self, u'提示信息框', u'提示信息', )

    def closeEvent(self, event):
        reply = QtWidgets.QMessageBox.question(self, '警告', '退出后交易将停止,\n你确认要退出吗？',
                                               QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    # ---------------------------------------------------------------------------------------------------------
    def _tableDepthMarketItem_OnClicked(self, item):
        """"""
        tmp = item  # type QTableWidgetItem
        col = self.tableWidget_DepthMarket.indexFromItem(tmp).column()  # 获取所在列
        text = self.tableWidget_DepthMarket.item(0, col).text()
        self.label_order_code.setText(text)
        self.label_lastprice.setText(self.tableWidget_DepthMarket.item(1, col).text())

    def _tableOnRtnOrderAction_DoubelClicked(self, item):
        """双击委托板撤单"""
        tmp = item
        col = self.tableWidget_onrtnorder.indexFromItem(tmp).column()
        symbol = self.tableWidget_onrtnorder.item(0, col).text()
        exchange = self.tableWidget_onrtnorder.item(7, col).text()
        frontID = self.tableWidget_onrtnorder.item(8, col).text()
        sessionID = self.tableWidget_onrtnorder.item(9, col).text()

        # 撤单模板:
        cancelOrderReq = CancelOrderReq()
        cancelOrderReq.symbol = symbol
        cancelOrderReq.exchange = exchange
        cancelOrderReq.frontID = frontID
        cancelOrderReq.sessionID = sessionID

        event = Event()
        event.type_ = EVENT_ORDERACTION
        event.dict_ = cancelOrderReq
        self.ee.put(event)


    def _tableDepthMarketItem_DoubleClicked(self, item):
        tmp = item
        row = self.tableWidget_Instrument.indexFromItem(tmp).row()
        instrumentID = self.tableWidget_Instrument.item(row, 1)
        try:
            self.mdApi.subscribeReq.setdefault(instrumentID)
            # li = self.mdApi.subscribeReq
            # self.mdApi.tosubscribe()  # 查询li中的行情
            self.ee.registerGeneralHandler(self.mdApi.tosubscribe)  # 向每秒都申请一次连接行情,以防行情断开

        except:
            traceback.print_exc()

    # ---------------------------------------------- 界面信号与槽区块 ------------------------------------------#
    @QtCore.pyqtSlot()
    def on_pushButton_onrtndel_clicked(self):
        """清空列表"""
        print("""清空列表""")
        if self.tableWidget_onrtnorder.item(0, 0):
            self.tableWidget_onrtnorder.setColumnCount(0)

    @QtCore.pyqtSlot()
    def on_pushButton_OrderReq_clicked(self):
        """查询委托"""
        print("main,查询委托")
        if self.istdConnected:
            self.tdApi.reqQryOrder()

    @QtCore.pyqtSlot()
    def on_pushButton_TradeReq_clicked(self):
        """查询成交"""
        print("main,查询成交")
        if self.istdConnected:
            self.tdApi.reqQryTrade()

    @QtCore.pyqtSlot()
    def on_action_Backtesting_triggered(self):
        """打开回测界面"""
        self.Ui_Backtesting.show()

    @QtCore.pyqtSlot()
    def on_action_RealTrading_triggered(self):
        """打开回测界面"""
        self.Ui_Real_Trade = RealTradeWindow()
        self.Ui_Real_Trade.show()
        self.is_real_trade_on = True  # TODO:和实盘子进程启动按钮绑定?

    @QtCore.pyqtSlot()
    def on_Direction_BUY_clicked(self):
        """下单板:开多"""
        print("下单板:方向买")
        self.orderdirection = 1

    @QtCore.pyqtSlot()
    def on_Direction_SELL_clicked(self):
        """下单板:开空"""
        print("下单板:方向卖")
        self.orderdirection = 2

    @QtCore.pyqtSlot()
    def on_OFFSET_OPEN_clicked(self):
        """下单板开仓"""
        print("下单板:开仓")
        self.orderoffsettype = 0

    @QtCore.pyqtSlot()
    def on_OFFSET_CLOSETODAY_clicked(self):
        """下单板平今"""
        print("下单板:平今")
        self.orderoffsettype = 1

    @QtCore.pyqtSlot()
    def on_OFFSET_CLOSEY_clicked(self):
        """下单板平昨"""
        print("下单板:平昨")
        self.orderoffsettype = 2

    @QtCore.pyqtSlot()
    def on_radioButton_limitprice_clicked(self):
        """下单板限价"""
        print("下单板:限价")
        self.orderpricetype = 2

    @QtCore.pyqtSlot()
    def on_radioButton_SJ_clicked(self):
        """下单板市价价"""
        print("下单板:市价")
        self.orderpricetype = 1

    @QtCore.pyqtSlot()
    def on_pushButton_searchInstruemt_clicked(self):
        """搜索表格中的字符,并定位到对应行,可以先排序再定位"""
        if self.ismdConnected:
            text = self.lineEdit_searchInstrument.text()
            item = self.tableWidget_Instrument.findItems(text, QtCore.Qt.MatchContains)  # 遍历表查找对应的item
            row = item[0].row()  # 获取其行号
            self.tableWidget_Instrument.verticalScrollBar().setSliderPosition(row)

    @QtCore.pyqtSlot()
    def on_pushButton_loadInstrument_clicked(self):
        """载入合约列表信息"""
        try:
            self.Instrumentrow = 0
            self.tdApi.reqQryInstrument()
            print("载入合约信息中")
        except:
            print("未登录")

    @QtCore.pyqtSlot()
    def on_pushButton_login_clicked(self):

        if not self.istdConnected:
            self.tdserver = self.TDEdit.text()
            self.mdserver = self.MDEdit.text()

            self.broker_id = self.BIDEdit.text()
            self.password = self.PWEdit.text()
            self.investor_id = self.USEREdit.text()

            if check_address_port(self.tdserver):
                print("正在登录ctp")
                self.connect()

                self.register()  # 事件监听的要在ctp启动之后

            else:
                print("交易所端口已关闭或未连接")

    @QtCore.pyqtSlot()
    def on_checkBox_saveLogin_clicked(self):
        print("保存登录信息")
        setting_dict = {
            "brokerID": self.BIDEdit.text(),
            "mdAddress": self.MDEdit.text(),
            "tdAddress": self.TDEdit.text(),
            "userID": self.USEREdit.text(),
            "password": self.PWEdit.text()
        }
        setting_dict = json.dumps(setting_dict)

        with open(ctploginsettingpath, 'w') as f:
            f.write(setting_dict)

    @QtCore.pyqtSlot()
    def on_pushButton_qry_clicked(self):
        """点击订阅行情"""
        print("点击订阅行情")
        if self.ismdConnected:
            self.mdApi.subscribeReq.setdefault(self.lineEdit_code.text())
            print(self.mdApi.subscribeReq)

    @QtCore.pyqtSlot()
    def on_pushButton_Orderin_clicked(self):
        """点击发送开平单"""

        if self.istdConnected:
            self.sendOrder()
            print("发送委托单")
        # self.tdApi.orderInsert(orderReq)

    # ---------------------------------------------------------------------------------------------------------
    def register(self):  # 往self.ee中注册函数
        self.ee.register(type_=EVENT_TICK, handler=self.inserttick)  # 注册gettick

        self.ee.register(type_=EVENT_POSITION, handler=self.insertposition)

        self.ee.register(type_=EVENT_ACCOUNT, handler=self.insertAccountinfo)

        self.ee.register(type_=EVENT_INSTRUMENT, handler=self.insertInstrument)

        self.ee.register(type_=EVENT_ORDER, handler=self.tdApi.orderInsert)
        self.ee.register(type_=EVENT_ORDERRSP, handler=self.insertOrderRsp)
        self.ee.register(type_=EVENT_TRADERSP, handler=self.insertTradeRsp)
        self.ee.register(type_=EVENT_ORDERACTION, handler=self.tdApi.ordercancel)

        self.ee.register(type_=EVENT_TIMER, handler=self.tdApi.reqQryInvestorPosition)
        self.ee.register(type_=EVENT_TIMER, handler=self.tdApi.reqQryTadingAccount)
        self.ee.register(type_=EVENT_TIMER, handler=self.listenRealTradeOrder)

        self.ee.register(type_=EVENT_1minBAR, handler=self.sendbar)

        self.ee.registerGeneralHandler(self.mdApi.tosubscribe)  # 增加冗余的查询语句,防止行情断开

        self.ee.start()

    # ---------------------------------------------------------------------------------------------------------

    def connect(self):
        """连接"""
        # 行情连接
        if not self.ismdConnected:
            try:
                self.mdApi = Md(broker_id=self.broker_id, investor_id=self.investor_id, password=self.password,
                                engine=self.ee)
                self.mdApi.Create()
                self.mdApi.RegisterFront(self.mdserver)
                self.mdApi.Init()
                self.ismdConnected = True  # 行情API连接状态，登录完成后为True
            except:
                traceback.print_exc()
                print("行情连接未成功")
        if not self.istdConnected:
            try:
                self.tdApi = Trader(broker_id=self.broker_id, investor_id=self.investor_id, password=self.password,
                                    engine=self.ee)
                self.tdApi.Create()
                self.tdApi.RegisterFront(self.tdserver)
                self.tdApi.SubscribePrivateTopic(2)  # 只传送登录后的流内容
                self.tdApi.SubscribePublicTopic(2)  # 只传送登录后的流内容
                self.tdApi.Init()
                self.istdConnected = True  # 交易API连接状态
            except:
                traceback.print_exc()

    # ---------------------------------------------------------------------------------------------------------
    def sendbar(self, event):
        """
        处理1min数据的分发
        :return:
        """
        if self.is_datacollect_on:
            # TODO:数据收集,入数据库(当能稳定实盘交易的时候制作该模块)或csv
            pass
        if self.is_real_trade_on:
            q_bar.put(event)
            # print("主进程sendbar发送给Real_Trade:   ", 'event:', event.type_, ";", 'event.dict_:', event.dict_)

    def listenRealTradeOrder(self, event):
        """
        监听实盘子进程的报单
        :param event:
        :return:
        """
        if self.is_real_trade_on:

            if not q_order.empty():
                temp = q_order.get_nowait()
                self.ee.put(temp)

    def sendOrder(self):
        """
        发单,tdapi.orderInsert()中默认为1手,日后需求可改进为自定义买入手数
        """
        orderReq = self.orderbook()
        event = Event()
        event.type_ = EVENT_ORDER
        event.dict_ = orderReq
        self.ee.put(event)

    # ---------------------------------------------- 界面数据更新块 -------------------------------------------------

    def insertAccountinfo(self, event):
        """接收tdApi.OnRspQryTradingAccount传过来的资金数据"""
        account = event.dict_
        if account:
            self.tableWidget_Account.item(0, 0).setText(account.AccountID.decode("utf-8").__str__())
            self.tableWidget_Account.item(1, 0).setText(account.PreBalance.__str__())
            self.tableWidget_Account.item(2, 0).setText(account.Available.__str__())
            self.tableWidget_Account.item(3, 0).setText(account.Commission.__str__())
            self.tableWidget_Account.item(4, 0).setText(account.CurrMargin.__str__())
            # self.tableWidget_Account.item(5, 0).setText(account.CloseProfit.__str__())
            # self.tableWidget_Account.item(6, 0).setText(account.PositionProfit.__str__())

    def inserttick(self, event):
        """
        接受ctpclien.mdApi.OnRtnDepthMarketData()传过来的订阅数据流
        :param tickbar:
        :return:
        """

        length = len(self.mdApi.subscribeReq)
        tickdata = event.dict_
        for col in range(length):
            symbol = self.tableWidget_DepthMarket.item(0, col).text()
            if symbol == tickdata.InstrumentID or symbol == "_":
                # col列,0行更新数据为tickdata.InstrumentID...
                self.tableWidget_DepthMarket.item(0, col).setText(tickdata.InstrumentID)
                self.tableWidget_DepthMarket.item(1, col).setText(tickdata.LastPrice.__str__())
                self.tableWidget_DepthMarket.item(2, col).setText(tickdata.PreClosePrice.__str__())
                self.tableWidget_DepthMarket.item(3, col).setText(tickdata.PreOpenInterest.__str__())
                self.tableWidget_DepthMarket.item(4, col).setText(tickdata.OpenPrice.__str__())
                self.tableWidget_DepthMarket.item(5, col).setText(tickdata.HighestPrice.__str__())
                self.tableWidget_DepthMarket.item(6, col).setText(tickdata.LowestPrice.__str__())
                self.tableWidget_DepthMarket.item(7, col).setText(tickdata.Volume.__str__())
                self.tableWidget_DepthMarket.item(8, col).setText(tickdata.Turnover.__str__())
                self.tableWidget_DepthMarket.item(9, col).setText(tickdata.OpenInterest.__str__())
                self.tableWidget_DepthMarket.item(10, col).setText(tickdata.AskVolume1.__str__())
                self.tableWidget_DepthMarket.item(11, col).setText(tickdata.AskPrice1.__str__())
                self.tableWidget_DepthMarket.item(12, col).setText(tickdata.BidPrice1.__str__())
                self.tableWidget_DepthMarket.item(13, col).setText(tickdata.BidVolume1.__str__())
                self.tableWidget_DepthMarket.item(14, col).setText(tickdata.UpperLimitPrice.__str__())
                self.tableWidget_DepthMarket.item(15, col).setText(tickdata.LowerLimitPrice.__str__())
                self.tableWidget_DepthMarket.item(16, col).setText(tickdata.Date.__str__())
                self.tableWidget_DepthMarket.item(17, col).setText(tickdata.UpdateTime.__str__())
                return

    def insertposition(self, event):
        """
        接受self.tdApi.OnRspQryInvestorPosition
        :param position_:
        :return:
        """
        if self.is_real_trade_on:
            q_bar.put(event)
        positions = event.dict_
        cols = positions.__len__()
        self.tableWidget_position.setColumnCount(cols)  # 以列的数目cols建表
        col = 0
        for SymbolDirPos in positions:
            if self.tableWidget_position.item(0, col) is None:
                [self.tableWidget_position.setItem(j, col, QtWidgets.QTableWidgetItem()) for j in range(10)]
            position_ = positions[SymbolDirPos]

            # print("self.tableWidget_position.item(0, col):", self.tableWidget_position.item(0, col))

            self.tableWidget_position.item(0, col).setText(position_.TradingDay)
            self.tableWidget_position.item(1, col).setText(position_.InstrumentID)
            self.tableWidget_position.item(2, col).setText(position_.PosiDirection)
            self.tableWidget_position.item(3, col).setText(position_.YdPosition.__str__())
            self.tableWidget_position.item(4, col).setText(position_.Position.__str__())
            self.tableWidget_position.item(5, col).setText(position_.PositionCost.__str__())
            self.tableWidget_position.item(6, col).setText(position_.UseMargin.__str__())
            self.tableWidget_position.item(7, col).setText(position_.OpenCost.__str__())
            self.tableWidget_position.item(8, col).setText(position_.PositionProfit.__str__())
            self.tableWidget_position.item(9, col).setText(position_.CloseProfit.__str__())
            col += 1

    def insertOrderRsp(self, event):
        """接受tdApi.OnRspQryOrder传过来的数据"""
        orderrsps = event.dict_
        cols = orderrsps.__len__()
        # self.tableWidget_onrtnorder.clearContents()

        self.tableWidget_onrtnorder.setColumnCount(cols)  # 以列的数目cols建表
        col = 0
        for orderrsp in orderrsps:
            if not self.tableWidget_onrtnorder.item(0, col):
                # 若为空,则建立表
                [self.tableWidget_onrtnorder.setItem(j, col, QtWidgets.QTableWidgetItem()) for j in range(10)]
            data = orderrsps[orderrsp]
            print("data.__dict__:", data.__dict__)
            self.tableWidget_onrtnorder.item(0, col).setText(data.InstrumentID)
            self.tableWidget_onrtnorder.item(1, col).setText(data.DirOffset)
            self.tableWidget_onrtnorder.item(2, col).setText(data.LimitPrice)
            self.tableWidget_onrtnorder.item(3, col).setText(data.VolumeTotalOriginal)
            self.tableWidget_onrtnorder.item(4, col).setText(data.VolumeTraded)
            self.tableWidget_onrtnorder.item(5, col).setText(data.Datetime)
            self.tableWidget_onrtnorder.item(6, col).setText(data.OrderStatus)
            self.tableWidget_onrtnorder.item(7, col).setText(data.ExchangeID)
            self.tableWidget_onrtnorder.item(8, col).setText(data.FrontID)
            self.tableWidget_onrtnorder.item(9, col).setText(data.SessionID)
            col += 1

    def insertTradeRsp(self, event):
        """接收tdApi关于成交单的数据"""
        tradersps = event.dict_
        cols = tradersps.__len__()
        # print("cols:", cols)
        self.tableWidget_onrtntrade.setColumnCount(cols)  # 以列的数目cols建表
        col = 0
        for orderrsp in tradersps:
            if not self.tableWidget_onrtntrade.item(0, col):
                # 若为空,则建立表
                [self.tableWidget_onrtntrade.setItem(j, col, QtWidgets.QTableWidgetItem()) for j in range(8)]
            data = tradersps[orderrsp]
            print(data.__dict__)
            self.tableWidget_onrtntrade.item(0, col).setText(data.InstrumentID)
            self.tableWidget_onrtntrade.item(1, col).setText(data.OffsetFlag)
            self.tableWidget_onrtntrade.item(2, col).setText(data.Direction)
            self.tableWidget_onrtntrade.item(3, col).setText(data.Price)
            self.tableWidget_onrtntrade.item(4, col).setText(data.Volume)
            self.tableWidget_onrtntrade.item(5, col).setText(data.Datetime)
            self.tableWidget_onrtntrade.item(6, col).setText(data.TradeID)
            self.tableWidget_onrtntrade.item(7, col).setText(data.OrderSysID)
            col += 1

    def insertInstrument(self, event):
        """
        接受self.tdApoi.OnRspQryInstrument传来的信息流
        :param Instrument:
        :return:
        """
        Instruments = event.dict_
        rows = Instruments.__len__()
        self.tableWidget_Instrument.setRowCount(rows)  # 以列的数目cols建表
        row = 0
        for InstrumentID in Instruments:

            if not self.tableWidget_Instrument.item(row, 0):
                # 若为空则建立合约表的栏目
                [self.tableWidget_Instrument.setItem(row, j, QtWidgets.QTableWidgetItem()) for j in range(11)]
            Instrument = Instruments[InstrumentID]
            self.tableWidget_Instrument.item(row, 0).setText(Instrument.InstrumentID)
            self.tableWidget_Instrument.item(row, 2).setText(Instrument.ExchangeID)
            self.tableWidget_Instrument.item(row, 3).setText(Instrument.MinLimitOrderVolume)
            self.tableWidget_Instrument.item(row, 4).setText(Instrument.MinMarketOrderVolume)
            self.tableWidget_Instrument.item(row, 5).setText(Instrument.PriceTick)
            self.tableWidget_Instrument.item(row, 6).setText(Instrument.ExpireDate)
            self.tableWidget_Instrument.item(row, 7).setText(Instrument.ShortMarginRatio)
            self.tableWidget_Instrument.item(row, 8).setText(Instrument.LongMarginRatio)
            self.tableWidget_Instrument.item(row, 9).setText(Instrument.VolumeMultiple)
            self.tableWidget_Instrument.item(row, 10).setText(Instrument.StartDelivDate)
            row += 1

    def orderbook(self):
        # 报单模板:
        orderReq = OrderReq()

        orderReq.symbol = self.label_order_code.text()  # 如:'rb1905'  # 代码

        if orderReq.symbol is not None:
            if self.orderdirection == 1:  # 开单方向属性 :0,1,2 1开多,2开空,0
                orderReq.direction = directionMap[DIRECTION_LONG]  # 买卖
            elif self.orderdirection == 2:
                orderReq.direction = directionMap[DIRECTION_SHORT]  # 买卖

            if self.orderoffsettype == 0:  # 平单: 0开仓,1平今,2平昨
                orderReq.offset = offsetMap[OFFSET_OPEN]  # 开平
            elif self.orderoffsettype == 1:
                orderReq.offset = offsetMap[OFFSET_CLOSETODAY]
            elif self.orderoffsettype == 2:
                orderReq.offset = offsetMap[OFFSET_CLOSEYESTERDAY]

            if self.orderpricetype == 2:  # 开平单 限价与市价属性: 1市价, 2限价.
                try:
                    orderReq.price = float(self.lineEdit_limitprice.text())  # 限价
                except ValueError:
                    print("请输入整数.")
                orderReq.priceType = priceTypeMap[PRICETYPE_LIMITPRICE]  # 价格类型
            elif self.orderpricetype == 1:
                # orderReq.price = int(self.label_lastprice.text())# 市价
                orderReq.priceType = priceTypeMap[PRICETYPE_MARKETPRICE]  # 价格类型
            orderReq.volume = int(self.lineEdit_volume.text())  # 数量
            # print(orderReq)
            return orderReq


class Realtrade(multiprocessing.Process):
    """
    实盘子进程
    """

    def __init__(self, symbol_list, Portfolio_, strategy, quantity, start_date=None, capital=None, initial_data=None):
        super(Realtrade, self).__init__()
        self.symbol_list = symbol_list
        self.initial_capital = capital  # 通过conn_listen接收该值
        self.quantity = quantity
        self.UpperLimitPrice = 0  # 初始化最高价为0
        self.LowerLimitPrice = 0  # 初始化最低价为0
        # self.heartbeat = heartbeat  # 心跳,暂时没啥用
        self.start_date = start_date  # 在第一次while循环的时候再更新
        self.initial_data = initial_data
        self.positionLong = None  # 存放当前多的持仓信息
        self.positionShort = None  # 存放当前空的持仓信息

        self.signals = 0
        self.orders = 0
        self.fills = 0
        self.num_strats = 1

        self.events = myqueue()

        self.data_handler_cls = data.RealTradeDataHandler
        self.portfolio_cls = Portfolio_
        self.strategy_cls = strategy
        self.execution_handler_cls = execution.realExecutionHandler

        self._generate_trading_instances()

        print('运行实盘交易子进程__init__ ok')

    def _generate_trading_instances(self):
        """
        Generates the trading instance objects from their class types.
        """
        print("Creating DataHandler, Strategy")
        self.data_handler = self.data_handler_cls(self.events, self.symbol_list, latest_symbol_data=self.initial_data)

        self.strategy = self.strategy_cls(self.data_handler, self.events, self.quantity)

        # TODO:未来加入资产收益记录模块
        # self.portfolio = self.portfolio_cls(self.data_handler, self.ee, self.start_date, self.initial_capital)
        # self.execution_handler = self.execution_handler_cls(eventEngine=self.ee, commission=self.commission, exchange=self.exchange)

    def getposition(self, event):
        """TODO:修改这个self.position,要对应多空仓位.
        接受从主进程行情端传过来的持仓信息
        :param event:
        :return:
        """
        positions = event.dict_
        print('getposition positions.')
        for SymbolDirPos in positions:
            position_ = positions[SymbolDirPos]

            if position_.InstrumentID == self.symbol_list[0] and position_.PosiDirection == '多':  # 过滤仓位信息,只保留实盘策略标的持仓信息
                print("position_.InstrumentID == self.symbol_list[0] and position_.PosiDirection == '多':",
                      position_.InstrumentID == self.symbol_list[0] and position_.PosiDirection == '多')
                self.positionLong = position_
            else:
                self.positionLong = None

            if position_.InstrumentID == self.symbol_list[0] and position_.PosiDirection == '空':  # 过滤仓位信息,只保留实盘策略标的持仓信息
                print("position_.InstrumentID == self.symbol_list[0] and position_.PosiDirection == '空':",
                      position_.InstrumentID == self.symbol_list[0] and position_.PosiDirection == '空')
                self.positionShort = position_
            else:
                self.positionShort = None


        if self.positionLong:
            print("self.positionLong.__dict__", self.positionLong.__dict__)
        elif self.positionShort:
            print("self.positionShort.__dict__", self.positionShort.__dict__)


    def run(self):
        """
        Executes the RealTrade son Process.
        """
        i = 0

        while True:
            # Update the market bars

            try:
                event = q_bar.get(block=True, timeout=1)

                # print('Real_Trade进程得到:', event.type_, ';', event.dict_)

                if event.type_ == EVENT_POSITION:
                    self.getposition(event)

                if event.type_ == EVENT_1minBAR and self.UpperLimitPrice == 0 and event.dict_['symbol'] == \
                        self.symbol_list[0]:
                    self.UpperLimitPrice = event.dict_["UpperLimitPrice"]
                    self.LowerLimitPrice = event.dict_["LowerLimitPrice"]

                if event.type_ == EVENT_1minBAR and event.dict_['symbol'] == self.symbol_list[0]:
                    # print('准备put event:', event.type_, ';', event.dict_)
                    self.data_handler.update_bars(event)
                    # print("将bar数据提交给 data_handler")

                while True:
                    # print("while while")
                    if self.events.empty():
                        print("break")
                        break
                    if not self.events.empty():
                        print("while while else")
                        RTevents = self.events.get()

                        if RTevents.type_ == 'MARKET':
                            self.strategy.calculate_signals(RTevents)

                        if RTevents.type_ == 'SIGNAL':
                            self.generate_order(RTevents)

                i += 1
                if i % 10 == 0:
                    print(i)
            except Exception as ee:
                pass
                print(ee)

    def generate_order(self, event):
        """TODO:有错误从简单的开始
        机制:
        1.如果原来未持有该symbol,则进行买入空单或多单,
        2.如果原来持有该symbol,则先卖出所有该symbol的持有的空单再买入多单,或先卖入所有的多单再买入空单
        event: signal信息
        :return:
        """

        # try:
        #     position = self.position  # 所有仓位信息
        # except:
        #     position = None
        # print('generate_order positon:', position)

        if event.signal_type == 'LONG':  # TODO:实盘检查 看看order是否正确

            if self.positionLong is None and self.positionShort.Position == 0:  # 没有仓位的时候开多.
                print("self.positionLong is None and self.positionShort == 0:",
                      self.positionLong is None and self.positionShort == 0)

                orderReq = OrderReq()
                orderReq.symbol = self.symbol_list[0]  # 代码
                orderReq.direction = directionMap[DIRECTION_LONG]  # 方向为多
                orderReq.price = self.UpperLimitPrice  # 最高价格
                orderReq.volume = self.quantity  # 面板自定义的数量
                orderReq.priceType = priceTypeMap[PRICETYPE_LIMITPRICE]  # 价格类型限价
                orderReq.offset = offsetMap[OFFSET_OPEN]  # 开仓

                RTOERDERevent = Event()
                RTOERDERevent.type_ = EVENT_ORDER
                RTOERDERevent.dict_ = orderReq
                q_order.put(RTOERDERevent)

            if self.positionShort is not None:  # 有空方仓位的时候先平空,再买多
                print("self.positionShort is not None:", self.positionShort is not None)
                orderReq = OrderReq()
                orderReq.symbol = self.symbol_list[0]  # 代码
                orderReq.direction = directionMap[DIRECTION_LONG]  # 买
                orderReq.price = self.UpperLimitPrice  # 涨停价格
                orderReq.volume = self.positionShort.Position  # 平仓数量按照持仓数来平
                orderReq.priceType = priceTypeMap[PRICETYPE_LIMITPRICE]  # 价格类型
                orderReq.offset = offsetMap[OFFSET_CLOSETODAY]  # 平

                RTOERDERevent = Event()
                RTOERDERevent.type_ = EVENT_ORDER
                RTOERDERevent.dict_ = orderReq
                q_order.put(RTOERDERevent)

                orderReq = OrderReq()
                orderReq.symbol = self.symbol_list[0]  # 代码
                orderReq.direction = directionMap[DIRECTION_LONG]  # 买
                orderReq.price = self.UpperLimitPrice  # 涨停价格
                orderReq.volume = self.quantity  # 面板自定义的数量
                orderReq.priceType = priceTypeMap[PRICETYPE_LIMITPRICE]  # 价格类型限价
                orderReq.offset = offsetMap[OFFSET_OPEN]  # 开平

                RTOERDERevent = Event()
                RTOERDERevent.type_ = EVENT_ORDER
                RTOERDERevent.dict_ = orderReq
                q_order.put(RTOERDERevent)

        if event.signal_type == 'EXIT':  # TODO: 以后把EXIT改成SHORT(看空),与LONG(看多)对应

            if self.positionShort is None and self.positionLong is None:  # 没有空仓没有多仓的时候开多.
                print("self.positionShort is None and self.positionLong is None:",
                      self.positionShort is None and self.positionLong is None)

                orderReq = OrderReq()
                orderReq.symbol = self.symbol_list[0]  # 代码
                orderReq.direction = directionMap[DIRECTION_SHORT]  # 卖
                orderReq.price = self.LowerLimitPrice  # 跌停价格
                orderReq.volume = self.quantity  # 面板自定义的数量
                orderReq.priceType = priceTypeMap[PRICETYPE_LIMITPRICE]  # 价格类型限价
                orderReq.offset = offsetMap[OFFSET_OPEN]  # 开

                RTOERDERevent = Event()
                RTOERDERevent.type_ = EVENT_ORDER
                RTOERDERevent.dict_ = orderReq
                q_order.put(RTOERDERevent)

            if self.positionLong is not None:  # 有多仓的时候先平多,再买空
                print("self.positionLong is not None:", self.positionLong is not None)
                orderReq = OrderReq()
                orderReq.symbol = self.symbol_list[0]  # 代码
                orderReq.direction = directionMap[DIRECTION_SHORT]  # 卖
                orderReq.price = self.LowerLimitPrice  # 跌停价格
                orderReq.volume = self.quantity  # 面板自定义的数量
                orderReq.priceType = priceTypeMap[PRICETYPE_LIMITPRICE]  # 价格类型限价
                orderReq.offset = offsetMap[OFFSET_CLOSETODAY]  # 平

                RTOERDERevent = Event()
                RTOERDERevent.type_ = EVENT_ORDER
                RTOERDERevent.dict_ = orderReq
                q_order.put(RTOERDERevent)

                orderReq = OrderReq()
                orderReq.symbol = self.symbol_list[0]  # 代码
                orderReq.direction = directionMap[DIRECTION_SHORT]  # 卖
                orderReq.price = self.LowerLimitPrice  # 价格
                orderReq.volume = self.quantity  # 数量
                orderReq.priceType = priceTypeMap[PRICETYPE_LIMITPRICE]  # 价格类型
                orderReq.offset = offsetMap[OFFSET_OPEN]  # 开平

                RTOERDERevent = Event()
                RTOERDERevent.type_ = EVENT_ORDER
                RTOERDERevent.dict_ = orderReq
                q_order.put(RTOERDERevent)


class RealTradeWindow(Ui_Real_Trade):

    def __init__(self):
        super(RealTradeWindow, self).__init__()
        self.setupUi(self)

        self.is_p_active = False  # 判断实盘进程是否启动
        self.init_data = None  # 初始数据

        self.pushButton_ONREALTRADE.clicked.connect(self.onReal_trade)  # 启动实盘策略子进程
        self.pushButton_Initialparameter.clicked.connect(self._initparameter)  # 初始化面板参数
        self.pushButton_frommysql.clicked.connect(self._loaddatafrommysql)  # 载入初始数据

        infomation = ['futures', 'stock']
        self.comboBox_style.addItems(infomation)

    def _initparameter(self):
        """
        载入面板参数
        :return:
        """

        # start_date = self.
        # capital = self.capital
        self.portfolio_cls = self.comboBox_style.currentText()
        if self.portfolio_cls == 'futures':
            self.portfolio_cls = 'Portfolio_For_futures_real'
        else:
            self.portfolio_cls = 'Portfolio_For_stock_real'
        self.Portfolio_ = portfolio.__dict__.__getitem__(self.portfolio_cls)
        self.strategy_cls = self.lineEdit_strategy.text()
        self.stra = strategy.__dict__.__getitem__(self.strategy_cls)
        self.symbol_list = [self.lineEdit_symbol.text()]
        self.quantity = int(self.lineEdit_volume.text())
        print("载入面板参数ok!")

    def _loaddatafrommysql(self):
        """
        TODO:载入的时候界面会阻塞,以后可以放到子线程中.
        (前提:mysql中的future_master下的xxx_1min中)
        载入self.symbol_list中的元素的某表
        :return:
        """
        self._initparameter()  # 以防没有初始化面板参数

        self.host = "localhost"
        self.port = 3306
        self.user = "root"
        self.passwd = "318318"
        self.db = "future_master"

        self.mysqlio = mysqlio(host=self.host, port=self.port, user=self.user, passwd=self.passwd, db=self.db)
        self.init_data = self.mysqlio.get_sth_from_mysql(
            sql="""select ts_code,trade_date,open,high,low,close,vol from %s_1min;""" % self.symbol_list[
                0])  # 数据类型pd.DataFrame
        print("数据载入成功,共%s条记录." % self.init_data.__len__())

    def onReal_trade(self):
        """
        启动实盘策略
        :return:
        """
        if self.init_data is not None:
            if self.is_p_active == False:
                self.p = Realtrade(symbol_list=self.symbol_list,
                                   Portfolio_=self.Portfolio_,
                                   strategy=self.stra,
                                   quantity=self.quantity,
                                   initial_data=self.init_data)
                self.p.daemon = True
                self.p.start()
                self.is_p_active = True
        else:
            print("为载入初始数据!实盘进程未启动")

    def closeEvent(self, event):
        """
        关闭窗口,同时关闭策略
        :param event:
        :return:
        """
        reply = QtWidgets.QMessageBox.question(self, '警告', '若有运行的实盘策略,退出后实盘策略将停止,\n确认要退出吗？',
                                               QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            if self.is_p_active == True:
                # 如果有实盘进程运行,则关闭
                self.p.terminate()
                self.is_p_active = False

            event.accept()
        else:
            event.ignore()


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    ui = MainWindow()
    ui.show()
    sys.exit(app.exec_())
