#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Mar  6 10:49:31 2017

@author: bladez
"""
import pandas as pd
import MySQLdb as mdb



def export_foreign(code,startdate,enddate):
    #默认取出国外某一个股票的2000年到现在的所有数据
    con = mdb.connect(host = "localhost", user = "stock_user", passwd = "698955", db = "stock_master", charset='utf8')

    # Select all of the historic Google adjusted close data
    sql = """SELECT dp.price_date,dp.adj_close_price FROM symbol as sym  
            inner join daily_price as dp ON dp.symbol_id = sym.id 
            where sym.ticker='{0}' and '{1}' <= dp.price_date 
            and '{2}' >= dp.price_date 
            order by dp.price_date ASC;""".format(code,startdate,enddate)
    # Create a pandas dataframe from the SQL query
    data = pd.read_sql_query(sql, con=con)
    return data


def export_foreign_all(code,startdate,enddate):
    #默认取出国外某一个股票的2000年到现在的所有数据
    con = mdb.connect(host = "localhost", user = "stock_user", passwd = "698955", db = "stock_master", charset='utf8')
    # Select all of the historic Google adjusted close data
    sql = """SELECT dp.price_date,dp.open_price,dp.high_price,dp.low_price,dp.close_price,dp.adj_close_price FROM symbol as sym  
            inner join daily_price as dp ON dp.symbol_id = sym.id 
            where sym.ticker='{0}' and '{1}'<= dp.price_date 
            and '{2}'>= dp.price_date 
            order by dp.price_date ASC;""".format(code,startdate,enddate)
    # Create a pandas dataframe from the SQL query
    data = pd.read_sql_query(sql, con=con)
    return data

def list_foreigns():
    #默认取出国外所有股票的简称和名字
    con = mdb.connect(host = "localhost", user = "stock_user", passwd = "698955", db = "stock_master", charset='utf8')
    # Select all of the historic Google adjusted close data
    sql = """SELECT ticker,name FROM symbol ;"""
    # Create a pandas dataframe from the SQL query
    data = pd.read_sql_query(sql, con=con)
    return data


def export_domestic(code,startdate,enddate,db_table='daily_price'):
    #默认取出国外某一个股票的2000年到现在的所有close数据
    con = mdb.connect(host = "localhost", user = "stock_user", passwd = "698955", db = "stock_master", charset='utf8')
    # Select all of the historic Google adjusted close data
    sql = """SELECT date,close FROM {0} where code='{1}' and '{2}' <= date and '{3}' >= date order by date ASC;""".format(db_table,code,startdate,enddate)
    # Create a pandas dataframe from the SQL query
    data = pd.read_sql_query(sql, con=con)
    return data


def export_domestic_all(code,startdate,enddate,db_table='daily_price'):
    #默认取出国外某一个股票的2000年到现在的所有数据
    con = mdb.connect(host = "localhost", user = "stock_user", passwd = "698955", db = "stock_master", charset='utf8')
    # Select all of the historic Google adjusted close data
    sql = """SELECT date,open,high,low,close,volume FROM {0} where code='{1}' and '{2}' <= date and '{3}' >= date order by date ASC;""".format(db_table,code,startdate,enddate)
    # Create a pandas dataframe from the SQL query
    data = pd.read_sql_query(sql, con=con)
    return data

#
            


def list_domestics():
    #默认取出国外所有股票的简称和名字
    db_host = 'localhost'
    db_user = 'stock_user'
    db_pass = '698955'
    db_name = 'stock_master'
    con = mdb.connect(db_host, db_user, db_pass, db_name)
    # Select all of the historic Google adjusted close data
    sql = """SELECT code,name FROM symbol ;"""
    # Create a pandas dataframe from the SQL query
    data = pd.read_sql_query(sql, con=con)
    return data