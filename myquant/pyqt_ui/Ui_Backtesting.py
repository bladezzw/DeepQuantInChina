# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'QWidget_plot.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!
import datetime
import pyqtgraph as pg
import os
import pandas as pd

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow

from multiprocessing import Process

from backtesting.backtest import Backtest
from backtesting.data import HistoricCSVDataHandler
from backtesting.execution import SimulatedExecutionHandler
from backtesting.portfolio import Portfolio, Portfolio_For_futures
from Strategy import strategy


class BacktestThread(Process):

    def __init__(self, csv_dir, symbol_list, initial_capital, start_date, strategy, commission, lever,
                 DATAhandler=HistoricCSVDataHandler,
                 EXECHandler=SimulatedExecutionHandler, portfolio=Portfolio, heartbeat=0.):
        super(BacktestThread, self).__init__()
        self.csv_dir = csv_dir
        self.symbol_list = symbol_list
        self.initial_capital = initial_capital
        self.start_date = start_date
        self.datahandler = DATAhandler
        self.exechandler = EXECHandler
        self.heartbeat = heartbeat
        self.strategy = strategy
        self.portfolio = portfolio
        self.commission = commission
        self.lever = lever

    def run(self):
        print(type(self.heartbeat), 'heartbeat')
        self.backtest = Backtest(csv_dir=self.csv_dir,
                                 symbol_list=self.symbol_list,
                                 initial_capital=self.initial_capital,
                                 heartbeat=self.heartbeat,
                                 start_date=self.start_date,
                                 data_handler=self.datahandler,
                                 execution_handler=self.exechandler,
                                 portfolio=self.portfolio,
                                 strategy=self.strategy,
                                 commission=self.commission,
                                 exchangeID=None,
                                 lever=self.lever
                                 )
        self.backtest.simulate_trading()


class Ui_Backtesting(QMainWindow):

    def __init__(self):
        super(Ui_Backtesting, self).__init__()
        # self.setupUi(self)

    def setupUi(self, MainWindow):
        print(os.getppid(), os.getpid())
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1200, 1000)

        self.createCentralwidget()

        self.createdock1()
        self.createdock2()

        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 31))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)

        self.retranslateUi(MainWindow)

    def createCentralwidget(self):
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.tab)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.tab_2)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.tabWidget.addTab(self.tab_2, "")
        self.tab_3 = QtWidgets.QWidget()
        self.tab_3.setObjectName("tab_3")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout(self.tab_3)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.tabWidget.addTab(self.tab_3, "")
        self.horizontalLayout.addWidget(self.tabWidget)
        self.setCentralWidget(self.centralwidget)

    def createPicture(self):
        """生成图片"""

        if not self.verticalLayout_2.itemAt(0):  # 没有就画
            self.drawChart1 = DrawChart(ktype='D')
            self.pic = self.drawChart1.pyqtgraphDrawChart()
            self.verticalLayout_2.addWidget(self.pic)
        else:  # 有就重画
            self.verticalLayout_2.removeWidget(self.pic)
            self.drawChart1 = DrawChart(ktype='D')
            self.pic = self.drawChart1.pyqtgraphDrawChart()
            self.verticalLayout_2.addWidget(self.pic)


    def createtotalcapital(self):
        """生成资金曲线图"""

        if not self.horizontalLayout_4.itemAt(0):  # 没有就画
            self.drawChart2 = DrawChart(ktype='D')
            self.capitalpic = self.drawChart2.pyqtgraphtotalcapital()
            self.horizontalLayout_4.addWidget(self.capitalpic)
        else:  # 有就重画
            self.horizontalLayout_4.removeWidget(self.capitalpic)
            self.drawChart2 = DrawChart(ktype='D')
            self.capitalpic = self.drawChart2.pyqtgraphtotalcapital()
            self.horizontalLayout_4.addWidget(self.capitalpic)


    def createdrawdown(self):

        if not self.horizontalLayout_6.itemAt(0):  # 没有就画
            self.drawChart3 = DrawChart(ktype='D')
            self.drawdownpic = self.drawChart3.pyqtgraphdrawdoen()
            self.horizontalLayout_6.addWidget(self.drawdownpic)
        else:  # 有就重画
            self.horizontalLayout_6.removeWidget(self.drawdownpic)
            self.drawChart3 = DrawChart(ktype='D')
            self.drawdownpic = self.drawChart3.pyqtgraphdrawdoen()
            self.horizontalLayout_6.addWidget(self.drawdownpic)



    def createdock1(self):
        self.dockWidget = QtWidgets.QDockWidget(self)
        self.dockWidget.setFeatures(QtWidgets.QDockWidget.DockWidgetFloatable | QtWidgets.QDockWidget.DockWidgetMovable)
        self.dockWidget.setObjectName("dockWidget")
        self.dockWidgetContents = QtWidgets.QWidget()
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.dockWidgetContents)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.label_6 = QtWidgets.QLabel(self.dockWidgetContents)
        self.label_6.setObjectName("label_6")
        self.gridLayout.addWidget(self.label_6, 1, 2, 1, 1)
        self.lineEdit_symbol = QtWidgets.QLineEdit(self.dockWidgetContents)
        self.lineEdit_symbol.setObjectName("lineEdit_symbol")
        self.gridLayout.addWidget(self.lineEdit_symbol, 1, 1, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.dockWidgetContents)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)
        self.lineEdit_begindate = QtWidgets.QLineEdit(self.dockWidgetContents)
        self.lineEdit_begindate.setObjectName("lineEdit_begindate")
        self.gridLayout.addWidget(self.lineEdit_begindate, 2, 1, 1, 1)
        self.label_8 = QtWidgets.QLabel(self.dockWidgetContents)
        self.label_8.setObjectName("label_8")
        self.gridLayout.addWidget(self.label_8, 3, 0, 1, 1)
        self.label_7 = QtWidgets.QLabel(self.dockWidgetContents)
        self.label_7.setObjectName("label_7")
        self.gridLayout.addWidget(self.label_7, 2, 2, 1, 1)
        self.line_Strategy = QtWidgets.QLineEdit(self.dockWidgetContents)
        self.line_Strategy.setObjectName("line_Strategy")
        self.gridLayout.addWidget(self.line_Strategy, 4, 1, 1, 1)
        self.label = QtWidgets.QLabel(self.dockWidgetContents)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.label_5 = QtWidgets.QLabel(self.dockWidgetContents)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 0, 2, 1, 1)
        self.Hist_path = QtWidgets.QLineEdit(self.dockWidgetContents)
        self.Hist_path.setObjectName("Hist_path")
        self.gridLayout.addWidget(self.Hist_path, 0, 1, 1, 1)
        self.label_4 = QtWidgets.QLabel(self.dockWidgetContents)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 4, 0, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.dockWidgetContents)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.label_9 = QtWidgets.QLabel(self.dockWidgetContents)
        self.label_9.setObjectName("label_9")
        self.gridLayout.addWidget(self.label_9, 0, 3, 1, 1)
        self.lineEdit_Capital = QtWidgets.QLineEdit(self.dockWidgetContents)
        self.lineEdit_Capital.setObjectName("lineEdit_Capital")
        self.gridLayout.addWidget(self.lineEdit_Capital, 3, 1, 1, 1)
        self.label_lever = QtWidgets.QLabel(self.dockWidgetContents)
        self.label_lever.setObjectName("label_lever")
        self.gridLayout.addWidget(self.label_lever, 1, 3, 1, 1)
        self.lineEdit_lever = QtWidgets.QLineEdit(self.dockWidgetContents)
        self.lineEdit_lever.setMaximumSize(QtCore.QSize(150, 150))
        self.lineEdit_lever.setObjectName("lineEdit_lever")
        self.gridLayout.addWidget(self.lineEdit_lever, 1, 4, 1, 1)
        self.label_10 = QtWidgets.QLabel(self.dockWidgetContents)
        self.label_10.setObjectName("label_10")
        self.gridLayout.addWidget(self.label_10, 2, 3, 1, 1)
        self.lineEdit_commission = QtWidgets.QLineEdit(self.dockWidgetContents)
        self.lineEdit_commission.setMaximumSize(QtCore.QSize(150, 150))
        self.lineEdit_commission.setObjectName("lineEdit_commission")
        self.gridLayout.addWidget(self.lineEdit_commission, 2, 4, 1, 1)
        self.comboBox_type = QtWidgets.QComboBox(self.dockWidgetContents)
        self.comboBox_type.setCurrentText("")
        self.comboBox_type.setObjectName("comboBox_type")
        self.gridLayout.addWidget(self.comboBox_type, 0, 4, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.dockWidget.setWidget(self.dockWidgetContents)
        self.addDockWidget(QtCore.Qt.DockWidgetArea(8), self.dockWidget)

        infomation = ['futures', 'stock']
        self.comboBox_type.addItems(infomation)

    def createdock2(self):
        self.dockWidget_2 = QtWidgets.QDockWidget(self)
        self.dockWidget_2.setFeatures(
            QtWidgets.QDockWidget.DockWidgetFloatable | QtWidgets.QDockWidget.DockWidgetMovable)
        self.dockWidget_2.setObjectName("dockWidget_2")
        self.dockWidgetContents_5 = QtWidgets.QWidget()
        self.dockWidgetContents_5.setObjectName("dockWidgetContents_5")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.dockWidgetContents_5)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.pushButton_createpicture = QtWidgets.QPushButton(self.dockWidgetContents_5)
        self.pushButton_createpicture.setObjectName("pushButton_createpicture")
        self.gridLayout_2.addWidget(self.pushButton_createpicture, 1, 0, 1, 1)
        self.pushButton_capital = QtWidgets.QPushButton(self.dockWidgetContents_5)
        self.pushButton_capital.setObjectName("pushButton_capital")
        self.gridLayout_2.addWidget(self.pushButton_capital, 2, 0, 1, 1)
        self.pushButton_Backteston = QtWidgets.QPushButton(self.dockWidgetContents_5)
        self.pushButton_Backteston.setObjectName("pushButton_Backteston")
        self.gridLayout_2.addWidget(self.pushButton_Backteston, 0, 0, 1, 1)
        self.pushButton_drawdown = QtWidgets.QPushButton(self.dockWidgetContents_5)
        self.pushButton_drawdown.setObjectName("pushButton_drawdown")
        self.gridLayout_2.addWidget(self.pushButton_drawdown, 3, 0, 1, 1)
        self.horizontalLayout_2.addLayout(self.gridLayout_2)
        self.dockWidget_2.setWidget(self.dockWidgetContents_5)
        self.addDockWidget(QtCore.Qt.DockWidgetArea(8), self.dockWidget_2)

        self.pushButton_createpicture.clicked.connect(self.createPicture)
        self.pushButton_Backteston.clicked.connect(self.runbacktest)
        self.pushButton_capital.clicked.connect(self.createtotalcapital)
        self.pushButton_drawdown.clicked.connect(self.createdrawdown)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "BackTest"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("MainWindow", "蜡烛图"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("MainWindow", "资金曲线图"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), _translate("MainWindow", "回撤图"))
        self.label_6.setText(_translate("MainWindow", "例: [\'00001.SH\']"))
        self.lineEdit_symbol.setText(_translate("MainWindow", "[\'000001.SH\']"))
        self.label_3.setText(_translate("MainWindow", "回测开始日期"))
        self.lineEdit_begindate.setText(_translate("MainWindow", "19900101"))
        self.label_8.setText(_translate("MainWindow", "初始资金"))
        self.label_7.setText(_translate("MainWindow", "例: 19900101"))
        self.line_Strategy.setText(_translate("MainWindow", "MovingAverageCrossStrategy"))
        self.label.setText(_translate("MainWindow", "csv历史数据文件目录:"))
        self.label_5.setText(_translate("MainWindow", "例: ~/data"))
        self.Hist_path.setText(_translate("MainWindow", "~/data"))
        self.label_4.setText(_translate("MainWindow", "策略名称"))
        self.label_2.setText(_translate("MainWindow", "symbol_lsit"))
        self.label_9.setText(_translate("MainWindow", "类型"))
        self.lineEdit_Capital.setText(_translate("MainWindow", "10000"))
        self.label_lever.setText(_translate("MainWindow", "杠杆(元/单位价差)"))
        self.lineEdit_lever.setText(_translate("MainWindow", "10"))
        self.label_10.setText(_translate("MainWindow", "交易费元/手"))
        self.lineEdit_commission.setText(_translate("MainWindow", "3.5"))
        self.pushButton_createpicture.setText(_translate("MainWindow", "回测完成后点击生成回测图"))
        self.pushButton_capital.setText(_translate("MainWindow", "生成资金曲线图"))
        self.pushButton_Backteston.setText(_translate("MainWindow", "开始回测"))
        self.pushButton_drawdown.setText(_translate("MainWindow", "生成回撤图"))

    def runbacktest(self):
        csv_dir = self.Hist_path.text()
        symbol_list = eval(self.lineEdit_symbol.text())
        initial_capital = int(self.lineEdit_Capital.text())
        start_date = self.lineEdit_begindate.text()
        stra_name = self.line_Strategy.text()

        stra = strategy.__dict__.__getitem__(stra_name)

        backtest_type = self.comboBox_type.currentText()

        lever = int(self.lineEdit_lever.text())
        commission = float(self.lineEdit_commission.text())

        if backtest_type == 'stock':
            Portfolio_type = Portfolio
            backtest = BacktestThread(csv_dir=csv_dir,
                                      symbol_list=symbol_list,
                                      initial_capital=initial_capital,
                                      heartbeat=0.0,
                                      start_date=start_date,
                                      lever=1,
                                      strategy=stra,
                                      commission=commission,
                                      portfolio=Portfolio_type,
                                      DATAhandler=HistoricCSVDataHandler,
                                      EXECHandler=SimulatedExecutionHandler
                                      )

        if backtest_type == 'futures':
            Portfolio_type = Portfolio_For_futures
            backtest = BacktestThread(csv_dir=csv_dir,
                                      symbol_list=symbol_list,
                                      initial_capital=initial_capital,
                                      heartbeat=0.0,
                                      start_date=start_date,
                                      DATAhandler=HistoricCSVDataHandler,
                                      EXECHandler=SimulatedExecutionHandler,
                                      portfolio=Portfolio_type,
                                      strategy=stra,
                                      commission=commission,
                                      lever=lever
                                      )
        backtest.start()


class DrawChart:
    def __init__(self, code='sz50', start=str(datetime.date.today() - datetime.timedelta(days=200)),
                 end=str(datetime.date.today() + datetime.timedelta(days=1)), ktype='D'):
        self.code = code
        self.start = start
        self.end = end
        self.ktype = ktype
        self.data_list, self.t = self.getData()

    def pyqtgraphDrawChart(self):
        try:
            self.item = CandlestickItem(self.data_list)
            self.xdict = {0: str(self.hist_data.index[0]).replace('-', '/'),
                          int((self.t + 1) / 2) - 1: str(self.hist_data.index[int((self.t + 1) / 2)]).replace('-', '/'),
                          self.t - 1: str(self.hist_data.index[-1]).replace('-', '/')}
            self.stringaxis = pg.AxisItem(orientation='bottom')
            self.stringaxis.setTicks([self.xdict.items()])
            self.plt = pg.PlotWidget(axisItems={'bottom': self.stringaxis}, enableMenu=False)

            self.plt.addItem(self.item)
            self.plt.showGrid(x=True, y=True)

            return self.plt
        except:
            return pg.PlotWidget()

    def pyqtgraphtotalcapital(self):
        try:
            self.item = totalcapitalItem(self.data_list)
            self.xdict = {0: str(self.hist_data.index[0]).replace('-', '/'),
                          int((self.t + 1) / 2) - 1: str(self.hist_data.index[int((self.t + 1) / 2)]).replace('-', '/'),
                          self.t - 1: str(self.hist_data.index[-1]).replace('-', '/')}
            self.stringaxis = pg.AxisItem(orientation='bottom')
            self.stringaxis.setTicks([self.xdict.items()])
            self.plt = pg.PlotWidget(axisItems={'bottom': self.stringaxis}, enableMenu=False)

            self.plt.addItem(self.item)
            self.plt.showGrid(x=True, y=True)

            return self.plt
        except:
            return pg.PlotWidget()

    def pyqtgraphdrawdoen(self):
        try:
            self.item = drawdownItem(self.data_list)
            self.xdict = {0: str(self.hist_data.index[0]).replace('-', '/'),
                          int((self.t + 1) / 2) - 1: str(self.hist_data.index[int((self.t + 1) / 2)]).replace('-', '/'),
                          self.t - 1: str(self.hist_data.index[-1]).replace('-', '/')}
            self.stringaxis = pg.AxisItem(orientation='bottom')
            self.stringaxis.setTicks([self.xdict.items()])
            self.plt = pg.PlotWidget(axisItems={'bottom': self.stringaxis}, enableMenu=False)

            self.plt.addItem(self.item)
            self.plt.showGrid(x=True, y=True)

            return self.plt
        except:
            return pg.PlotWidget()

    def getData(self):
        """

        :return: data_list,
        """

        self.hist_data = pd.read_csv('equity.csv')
        # print(self.hist_data)
        # print(self.hist_data.columns, 'self.hist_data.shape')
        try:
            self.hist_data.pop('direction')
        except:
            pass
        self.data_columns = self.hist_data.columns
        data_list = []
        t = 0
        for dates, row in self.hist_data.iterrows():
            # if :
            datetime, open, high, low, close, volume, Position, cash, commission, signal, total, returns, equity_curve, drawdown = row
            datas = (
                t, datetime, open, high, low, close, volume, Position, cash, commission, signal, total,
                returns, equity_curve, drawdown)

            data_list.append(datas)
            t += 1

        return data_list, t


class CandlestickItem(pg.GraphicsObject):
    """TODO:往x轴加入日期"""

    def __init__(self, data):
        pg.GraphicsObject.__init__(self)
        self.data = data
        self.generatePicture()

    def generatePicture(self):
        self.picture = QtGui.QPicture()
        p = QtGui.QPainter(self.picture)
        p.setPen(pg.mkPen('w'))

        w = 0.2  # 线条宽度

        for (t, datetime, open, high, low, close, volume, Position, cash, commission, signal, total, returns,
             equity_curve, drawdown) in self.data:
            if open > close:
                p.setPen(pg.mkPen('g'))
                p.setBrush(pg.mkBrush('g'))
                p.drawLine(QtCore.QPointF(t, low), QtCore.QPointF(t, high))
                p.drawRect(QtCore.QRectF(t - w, open, w * 2, close - open))
            else:
                p.setPen(pg.mkPen('r'))
                p.setBrush(pg.mkBrush('r'))
                p.drawLine(QtCore.QPointF(t, low), QtCore.QPointF(t, high))
                p.drawRect(QtCore.QRectF(t - w, open, w * 2, close - open))
            if signal == 1:
                p.setPen(pg.mkPen('r'))
                p.setBrush(pg.mkBrush('r'))
                p.drawEllipse(QtCore.QRectF(t - 1, high+2, 2, 4))
            if signal == -1:
                p.setPen(pg.mkPen('g'))
                p.setBrush(pg.mkBrush('g'))
                p.drawEllipse(QtCore.QRectF(t - 1, low-2, 2, 4))

        p.end()

    def paint(self, p, *args):
        p.drawPicture(0, 0, self.picture)

    def boundingRect(self):
        return QtCore.QRectF(self.picture.boundingRect())


class totalcapitalItem(pg.GraphicsObject):
    def __init__(self, data):
        pg.GraphicsObject.__init__(self)
        self.data = data
        self.pic_total()

    def pic_total(self):
        self.picture = QtGui.QPicture()
        p = QtGui.QPainter(self.picture)
        p.setPen(pg.mkPen('w'))

        w = 0.2

        pretotal = 0
        for (t, datetime, open, high, low, close, volume, Position, cash, commission, signal, total, returns,
             equity_curve, drawdown) in self.data:
            if pretotal != 0:
                p.setPen(pg.mkPen('w'))
                p.setBrush(pg.mkBrush('w'))
                p.drawLine(QtCore.QPointF(t - 1, pretotal), QtCore.QPointF(t, total))
            pretotal = total

        p.end()

    def paint(self, p, *args):
        p.drawPicture(0, 0, self.picture)
    def boundingRect(self):
        return QtCore.QRectF(self.picture.boundingRect())


class drawdownItem(pg.GraphicsObject):
    def __init__(self, data):
        pg.GraphicsObject.__init__(self)
        self.data = data
        self.drawdown()

    def drawdown(self):
        self.picture = QtGui.QPicture()
        p = QtGui.QPainter(self.picture)
        p.setPen(pg.mkPen('w'))

        w = 0.2

        predrawdown = 0
        for (t, datetime, open, high, low, close, volume, Position, cash, commission, signal, total, returns,
             equity_curve, drawdown) in self.data:
            print("t:",t)
            if t >= 2:
                p.setPen(pg.mkPen('w'))
                p.setBrush(pg.mkBrush('w'))
                p.drawLine(QtCore.QPointF(t - 1, predrawdown), QtCore.QPointF(t, drawdown))
            predrawdown = drawdown

        p.end()

    def paint(self, p, *args):
        p.drawPicture(0, 0, self.picture)
    def boundingRect(self):
        return QtCore.QRectF(self.picture.boundingRect())


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    ui = Ui_Backtesting()
    ui.setupUi(ui)
    ui.show()
    sys.exit(app.exec_())
