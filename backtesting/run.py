import os,sys
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.append(BASE_DIR)
import datetime
import time

from backtesting.backtest import Backtest
from backtesting.data import HistoricCSVDataHandler
from backtesting.execution import SimulatedExecutionHandler
from backtesting.portfolio import Portfolio,Portfolio_For_futures
from Strategy.strategy import MovingAverageCrossStrategy


def exc_time(func, *args, **kwargs):
    """
    计算运行时间
    :param func: a function
    :param args: arguements of the function
    :param kwargs: arguements of the function
    :return: time costed on running the function
    """

    def wrapper(func, *args, **kwargs):
        start_time = time.time()
        func(*args, **kwargs)
        stop_time = time.time()
        print("run time is %s" % (stop_time - start_time))

    return wrapper(func, *args, **kwargs)


if __name__ == "__main__":
    csv_dir = r"~/data"
    symbol_list = ['000001.SH']
    initial_capital = 5000.0
    start_date = datetime.datetime(2012,1,1,0,0,0)  # 这个没用上.
    heartbeat = 0.0
    
#default:    MACS = MovingAverageCrossStrategy(short_window=10,long_window=30)
    MACS = MovingAverageCrossStrategy

    commission = 5

    exchangeID = ''

    lever = 10  # 杠杆,(在期货中,一手跳动一个单位的价格,如:rb一手,跳动1个点表示10元)

    backtest_type = 'futures'



    if backtest_type == 'stock':
        backtest = Backtest(csv_dir=csv_dir,
                            symbol_list=symbol_list,
                            initial_capital=initial_capital,
                            heartbeat=heartbeat,
                            start_date=start_date,
                            data_handler=HistoricCSVDataHandler,
                            execution_handler=SimulatedExecutionHandler,
                            portfolio=Portfolio,
                            strategy=MACS,
                            commission=commission,
                            exchangeID=None,
                            lever=1
                            )

    elif backtest_type == 'futures':
        backtest = Backtest(csv_dir=csv_dir,
                            symbol_list=symbol_list,
                            initial_capital=initial_capital,
                            heartbeat=heartbeat,
                            start_date=start_date,
                            data_handler=HistoricCSVDataHandler,
                            execution_handler=SimulatedExecutionHandler,
                            portfolio=Portfolio_For_futures,
                            strategy=MACS,
                            commission=commission,
                            exchangeID=exchangeID,
                            lever=lever
                            )

    exc_time(backtest.simulate_trading)  # run time is 1.2880792617797852
