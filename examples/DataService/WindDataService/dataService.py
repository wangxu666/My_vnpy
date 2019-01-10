# encoding: UTF-8

from __future__ import print_function
import sys
import json
from datetime import datetime
from time import time, sleep

from pymongo import MongoClient, ASCENDING

from vnpy.trader.vtObject import VtBarData
from vnpy.trader.app.ctaStrategy.ctaBase import MINUTE_DB_NAME
import pandas as pd
from WindPy import *

# 加载配置
config = open('config.json')
setting = json.load(config)

MONGO_HOST = setting['MONGO_HOST']
MONGO_PORT = setting['MONGO_PORT']
SYMBOLS = setting['SYMBOLS']

mc = MongoClient(MONGO_HOST, MONGO_PORT)        # Mongo连接
db = mc[MINUTE_DB_NAME]                         # 数据库


#----------------------------------------------------------------------
def generateExchange(symbol):
    """生成VT合约代码"""
    w.start()
    if symbol[0:2] in ['60', '51','00', '15', '30']:
        data = w.htocode(symbol, "stocka").Data
        exchange = data[-1][0]
        symbol_m = data[0][0]

    else:
        data = w.htocode(symbol, "future").Data
        exchange = data[-1][0]
        symbol_m = data[0][0]
    w.stop()
    return exchange,symbol_m

#----------------------------------------------------------------------
def generateVtBar(ix,row):
    """生成K线"""
    bar = VtBarData()
    
    bar.symbol = row['code']
    bar.exchange = row['exchange']
    bar.vtSymbol = '.'.join([bar.symbol, bar.exchange])
    bar.open = row['open']
    bar.high = row['high']
    bar.low = row['low']
    bar.close = row['close']
    bar.volume = row['volume']
    bar.datetime = ix
    bar.date = bar.datetime.strftime("%Y%m%d")
    bar.time = bar.datetime.strftime("%H:%M:%S")
    
    return bar

#----------------------------------------------------------------------
def downMinuteBarBySymbol(symbol,date):
    """下载某一合约的分钟线数据"""

    cl = db[symbol]
    cl.ensure_index([('datetime', ASCENDING)], unique=True)         # 添加索引

    exchange,symbol_m = generateExchange(symbol)

    w.start()
    pre_td = w.tdaysoffset(-1, date, "").Data[0][0]
    date_start = pre_td.replace(hour=21).strftime('%Y-%m-%d %H:%M:%S')
    date_end = datetime.strptime(date,'%Y-%m-%d').replace(hour=15).strftime('%Y-%m-%d %H:%M:%S')

    data = w.wsi(symbol_m, "open,high,low,close,volume", date_start, date_end, "")
    df = pd.DataFrame(data.Data, columns=data.Times, index=data.Fields).T
    df['code']=symbol
    df['exchange']=exchange
    w.stop()
    
    for ix, row in df.iterrows():
        bar = generateVtBar(ix,row)
        d = bar.__dict__
        flt = {'datetime': bar.datetime}
        cl.replace_one(flt, d, True)            



    print(u'合约%s数据下载完成%s' %(symbol, df.index[0]))

    
#----------------------------------------------------------------------
def downloadAllMinuteBar(date):
    """下载所有配置中的合约的分钟线数据"""
    print('-' * 50)
    print(u'开始下载合约分钟线数据')
    print('-' * 50)
    
    # 添加下载任务
    for symbol in SYMBOLS:
        downMinuteBarBySymbol(str(symbol),date)
    
    print('-' * 50)
    print(u'合约分钟线数据下载完成')
    print('-' * 50)
    


    