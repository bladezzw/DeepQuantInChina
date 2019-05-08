#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Jun  7 23:41:57 2017

@author: bladezzw
(前提将同花顺软件的目录下的股票数据文件先转化成csv文件),将获得的csv文件批量导入mysql
"""
from struct import *
import pandas as pd
import os
import sys
import datetime
import MySQLdb as mdb


import updatemysql as ud



def insert_csv_into_db(df,str_f,last_updated_date):
 # Create the insert strings
        conn = mdb.connect(host = "localhost", user = "root", passwd = "******", db = "stock_master", charset='utf8')

        df['last_updated_date'] = last_updated_date
        df['code'] = str_f
        sql0 = """code,date,open,high,low,close,volume,last_updated_date"""
        insert_str = (" %s, " * 8)[:-2]
        sql = "INSERT INTO daily_price (%s) VALUES (%s);" %(sql0, insert_str)
        args = [(str_f,str(df.iloc[i,0]),df.iloc[i,1],df.iloc[i,2],df.iloc[i,3],df.iloc[i,4],df.iloc[i,6],last_updated_date) for i in range(len(df))]    
        cursor = conn.cursor()
        try:
            cursor.executemany(sql, args)
        except:
            print('execute the file' +f+'. wrong!')  
        cursor.close()
        conn.commit()
        conn.close()

if __name__ == "__main__":
    #input
    #defaut_format: '/home/bladez/data/data_csv/shlday'
    pathdir = '/home/bladez/data/data_csv/szlday'#数据路径
    listfile= os.listdir(pathdir)

    tickers = ud.getcodes()
    tickers_all=ud.getcodes_from_ts()
    code =tickers_all.index

    last_updated_date = datetime.datetime.utcnow()
    #execution    
    n = 1
    for f in listfile:
        #csv files load to the mysql
        print (n+0.0)/len(listfile)*100,'%'        
        str_f = f[2:8]
        if(str_f in code):     
            print f
            df = pd.read_csv(pathdir+'/'+f)
            #attend of the '/'
            insert_csv_into_db(df,str_f,last_updated_date)
 

        n=n+1
   
    print 'The task is over'

