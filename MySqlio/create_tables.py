# -*- coding:utf-8 -*-
import os,sys
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.append(BASE_DIR)
from MySqlio import * #获取包的全局参数
"""
#%% create database and tables
"""

def excute_sql(sql, db=db):
    conn = pymysql.connect(host=host,port=port,user=user,passwd=passwd,db=db)
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()
    cursor.close()
    conn.close()

def create_database_stock_master():
    """
    create stock_master, a database to manage data of stocks', in mysqldb.
    :return:
    """
    sql = """
    CREATE DATABASE stock_master;
    """
    excute_sql(sql,None)

def create_tables_daily():
    """
    create
    :return:
    """
    sql = """CREATE TABLE daily (
id int NOT NULL AUTO_INCREMENT,
ts_code varchar(255) NOT NULL,
trade_date datetime NULL,
open DOUBLE (19,4) NULL,
high DOUBLE(19,4)NULL,
low DOUBLE(19,4)NULL,
close DOUBLE(19,4)NULL,
`change` DOUBLE(19,4) NULL,
pre_close DOUBLE(9,4)NULL,
pct_chg DOUBLE(9,4)NULL,
vol DOUBLE(19,4)NULL,
amount DOUBLE(19,4)NULL,
create_date datetime NOT NULL,
PRIMARY KEY (`id`,`ts_code`),
INDEX index_ts_code_trade_date (ts_code,trade_date)

) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8; """
    excute_sql(sql)

def create_tables_Indexes():
    sql = """CREATE TABLE indexes (
    id int NOT NULL AUTO_INCREMENT,
    ts_code varchar(255) NOT NULL,
    name varchar(255) NULL,
    market varchar(255) NULL,
    publisher varchar(255) NULL,
    category varchar(255) NULL,
    base_date varchar(255) NULL,
    base_point decimal(16,2) NULL,
    list_date varchar(255) NULL,
    create_date datetime NOT NULL,
    PRIMARY KEY (id,ts_code)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8; """
    excute_sql(sql)

def create_tables_Index_daily():
    sql = """CREATE TABLE index_daily (
    id int NOT NULL AUTO_INCREMENT,
    ts_code varchar(255) NOT NULL,
    trade_date datetime NULL,
    open DOUBLE(19,4) NULL,
    high DOUBLE(19,4)NULL,
    low DOUBLE(19,4)NULL,
    close DOUBLE(19,4)NULL,
    pre_close DOUBLE(9,4)NULL,
    pct_chg DOUBLE(9,4)NULL,
    vol DOUBLE(19,4)NULL,
    amount DOUBLE(19,4)NULL,
    create_date datetime NOT NULL,
    PRIMARY KEY (`id`,`ts_code`)
    ) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8; """
    excute_sql(sql)

def create_tables_symbol():
    sql = """CREATE TABLE symbol (
  id int NOT NULL AUTO_INCREMENT ,
  ts_code varchar(255) NOT NULL unique,
  name varchar(255) NULL,
  symbol varchar(255) NULL,
  industry varchar(255) NULL,
  area varchar(255) NULL,
  fullname varchar(255) NULL,
  enname varchar(255) NULL,
  market varchar(255) NULL,
  exchange varchar(255) NULL,
  curr_type varchar(255) NULL,
  list_status varchar(255) NULL,
  list_date varchar(255) NULL,
  delist_date varchar(255) NULL,
  create_date datetime NOT NULL,  

  PRIMARY KEY (`id`,`ts_code`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8; """
    excute_sql(sql)

def create_database_future_master():
    """
    create stock_master, a database to manage data of stocks', in mysqldb.
    :return:
    """
    sql = """
    CREATE DATABASE future_master;
    """
    excute_sql(sql, None)

def create_tables_future_daily():
    sql = """CREATE TABLE futures_daily (
    id int NOT NULL AUTO_INCREMENT,
    ts_code varchar(255) NOT NULL,
    trade_date datetime NULL,
    open DOUBLE(19,4) NULL,
    high DOUBLE(19,4)NULL,
    low DOUBLE(19,4)NULL,
    close DOUBLE(19,4)NULL,
    pre_close DOUBLE(9,4)NULL,
    pct_chg DOUBLE(9,4)NULL,
    vol DOUBLE(19,4)NULL,
    amount DOUBLE(19,4)NULL,
    create_date datetime NOT NULL,
    PRIMARY KEY (`id`,`ts_code`)
    ) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8; """
    excute_sql(sql,"future_master")

def create_tables_future_daily_for_a_future(symbol=''):
    """
    为某个期货创建该名称的表
    :param symbol: e.g. rb1905_1min
    :return:
    """
    sql = """CREATE TABLE {} (
    id int NOT NULL AUTO_INCREMENT,
    ts_code varchar(255) NOT NULL,
    trade_date datetime NULL,
    open DOUBLE(19,4) NULL,
    high DOUBLE(19,4)NULL,
    low DOUBLE(19,4)NULL,
    close DOUBLE(19,4)NULL,
    pre_close DOUBLE(9,4)NULL,
    pct_chg DOUBLE(9,4)NULL,
    vol DOUBLE(19,4)NULL,
    amount DOUBLE(19,4)NULL,
    create_date datetime NOT NULL,
    PRIMARY KEY (`id`,`ts_code`)
    ) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8; """.format(symbol)
    excute_sql(sql,"future_master")

if __name__ == '__main__':
    print("create_tables_module".center(20,'-'))
    try:
        create_database_stock_master()#create stock_master in mysql
    except Exception as ee:
        print("stock_master already exist")
    try:
        create_tables_daily()#create table daily in mysql
    except Exception as ee:
        print('table daily Already exist')
    try:
        create_tables_Indexes()
    except Exception as ee:
        print('table indexes Already exist')
    try:
        create_tables_Index_daily()
    except Exception as ee:
        print('table index_daily Already exist')
    try:
        create_tables_symbol()
    except Exception as ee:
        print('table symbol Already exist')

    try:
        create_database_future_master()#create stock_master in mysql
    except Exception as ee:
        print("future_master already exist")

    try:
        create_tables_future_daily()
    except Exception as ee:
        print("future_daily already exist")