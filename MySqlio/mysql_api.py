# -*- coding:utf-8 -*-
from MySqlio import *

from MySqlio import data_transfer
# %% get data from mysql



class mysqlio(object):

    def __init__(self, host=host, port=port, user=user, passwd=passwd, db=db):
        self.host = host
        self.port = port
        self.user = user
        self.passwd = passwd
        self.db = db

    def select_sql(self, key='*',table='',where=''):

        sql = """select {key} from {table} where {where} ; """.format(key = key, table = table, where = where)
        return sql

    def get_allSymbolInMysql(self):
        """
        return a dict of symbols.返回mysql中所有存在于symbol表中的股票代码
        """
        conn = pymysql.connect(host=self.host, port=self.port, user=self.user, passwd=self.passwd, db=self.db)
        # 更改获取数据结果的数据类型,默认是元组,可以改为字典等:conn.cursor(cursor=pymysql.cursors.DictCursor)
        cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
        row_ = cursor.execute("select ts_code from symbol")  # this can be a function
        all_ = cursor.fetchall()

        li = []
        [li.append(all_[i]['ts_code']) for i in range(len(all_))]
        cursor.close()
        conn.close()
        return li

    def get_allIndexesInMysql(self):
        """
        return a dict of Indexes.返回mysql中所有存在于symbol表中的指数代码
        """
        conn = pymysql.connect(host=self.host, port=self.port, user=self.user, passwd=self.passwd, db=self.db)
        # 更改获取数据结果的数据类型,默认是元组,可以改为字典等:conn.cursor(cursor=pymysql.cursors.DictCursor)
        cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
        row_ = cursor.execute("select ts_code from indexes")  # this can be a function
        all_ = cursor.fetchall()

        li = []
        [li.append(all_[i]['ts_code']) for i in range(len(all_))]
        cursor.close()
        conn.close()
        return li


    def get_1stockdailyInMysql(self,table='daily', symbol='', start_date='19900101', end_date=now_):
        """
        :param symbol: str,eg:'000001.SZ';
        :param start_date: str,eg:'19910101'or'1991-01-01' ;
        :param end_date: str ,eg:format same as start_date
        :return:从mysql中得到1个股票的日线数据
        """
        conn = pymysql.connect(host=self.host, port=self.port, user=self.user, passwd=self.passwd, db=self.db)
        cursor = conn.cursor()
        # select * from daily where ts_code='000001.SZ' and trade_date>'2018-1-27' and trade_date<'2018-02-06'
        sql = self.select_sql( table = table,
                         where="""ts_code='{symbol_}'
                             and trade_date>'{start_}'
                             and trade_date<'{end_}'""".format(symbol_=symbol, start_=start_date, end_=end_date))
        row_ = cursor.execute(sql)  # this can be a function

        if row_:
            all_ = cursor.fetchall()

            data = pd.DataFrame(all_)

            # get the column names of data
            sql_1 = """ desc {table_name} """.format(table_name=table)
            row_2 = cursor.execute(sql_1)  # this can be a function
            desc_ = cursor.fetchall()
            title = []
            [title.append(desc_[i][0]) for i in range(len(desc_))]
            data.rename(columns=pd.Series(title), inplace=True)  # add columns' name

        cursor.close()
        conn.close()
        return data

    def get_1indexdailyInMysql(self, table='index_daily', symbol='', start_date='19900101', end_date=now_):
        """
        从mysql中获得1个指数日线数据(前提是里面已经有数据)
        :param symbol:  str,eg:'000001.SZ';
        :param start_date: str,eg:'19910101'or'1991-01-01' ;
        :param end_date: str ,eg:format same as start_date
        :return:
        """
        conn = pymysql.connect(host=self.host, port=self.port, user=self.user, passwd=self.passwd, db=self.db)
        cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
        # select * from daily where ts_code='000001.SZ' and trade_date>'2018-1-27' and trade_date<'2018-02-06'
        sql = self.select_sql(table = table, where="""ts_code='{symbol_}' and trade_date>'{start_}' and trade_date<'{end_}'""".format(symbol_=symbol, start_=start_date, end_=end_date))
        row_ = cursor.execute(sql)  # this can be a function

        # # 一下这段是看是否加索引对速度的影响
        # t1 = time.time()
        # row_ = cursor.execute(sql)  # this can be a function
        # t2 = time.time()
        # t2 - t1


        if row_:
            all_ = cursor.fetchall()

            data = pd.DataFrame(all_)
            cursor.close()
            conn.close()
            return data

        else:
            cursor.close()
            conn.close()
            return

    def get_anystockdailyInMysql(self, symbols=[], start_date='19900101', end_date=now_):
        """
        得到一列股票从开始日期到结束日期的数据
        :param symbols:
        :param start_date:
        :param end_date:
        :return:
        """
        print('obtain data,please wait.')
        data_ = self.get_1stockdailyInMysql(symbol=symbols[0], start_date=start_date, end_date=end_date)

        for k in range(len(symbols)):
            if k > 0:
                data_temp = self.get_1stockdailyInMysql(symbol=symbols[k], start_date=start_date, end_date=end_date)
                if data_temp:
                    data_ = pd.concat([data_, data_temp], axis=0, join='outer')
            print(int(k * 100 / len(symbols)), "% finish!")
        return data_

    def get_last_date_of_ts_code(self, ts_code='',table=''):
        """
        :param ts_code:
        :param table:
        :return:
        """
        sql = self.select_sql(key='max(trade_date)', table=table, where = """ts_code = '{ts_code}'""".format(ts_code=ts_code))
        conn = pymysql.connect(host=self.host, port=self.port, user=self.user, passwd=self.passwd, db=self.db)
        # 更改获取数据结果的数据类型,默认是元组,可以改为字典等:conn.cursor(cursor=pymysql.cursors.DictCursor)
        cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
        row_ = cursor.execute(sql)  # this can be a function
        all_ = cursor.fetchall()
        cursor.close()
        conn.close()
        date = all_[0]['max(trade_date)'].strftime("%Y%m%d")

        return date

    def get_sth_from_mysql(self, sql=''):
        """
        推荐用这个,因为可以根据sql的变化而有针对性取.
        :param sql: 任何符合mysql的查询语句e.g. "select * from 某表;" ...
        :return:
        """
        conn = pymysql.connect(host=self.host, port=self.port, user=self.user, passwd=self.passwd, db=self.db)
        cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
        row_ = cursor.execute(sql)  # this can be a function
        all_ = cursor.fetchall()
        data = pd.DataFrame(all_)


        if 'ts_code' in data.columns:
            data = data.rename(columns={'ts_code': 'symbol'})
        if 'vol' in data.columns:
            data = data.rename(columns={'vol': 'volume'})
        if 'trade_date' in data.columns:
            data = data.rename(columns={'trade_date': 'datetime'})

        if 'datetime' in data.columns:  # 如果有日期时间,默认将trade_date作为索引
            data = data.set_index('datetime').sort_index()

        cursor.close()
        conn.close()
        return data


if __name__ == '__main__':

    print("mysql_api module".center(40, '-'))

    host = "localhost"
    port = 3306
    user = "root"
    passwd = "318318"
    db = "future_master"
    table = 'rb1905_1min'
    symbol_list = ['rb1905']
    SQLIO = mysqlio(host=host, port=port, user=user, passwd=passwd, db=db)
    data = SQLIO.get_sth_from_mysql(sql="""select ts_code,trade_date,open,high,low,close,vol from rb1905_1min;""")

    data.columns

    print(len(data))
