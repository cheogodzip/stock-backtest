import sqlite3
from pandas import Series, DataFrame
import copy
from pykrx import stock
import time

f = open("ticker_list.txt", 'r')
ticker_list = f.read().split(',')
f.close()

con = sqlite3.connect("ohlcv.db")

again = []

for i in ticker_list:
    try:
        df = stock.get_market_ohlcv_by_date("20170101", "20201215", i)
        df.to_sql(i,con)
        time.sleep(0.5)
        print(i + ": 끝")
    except:
        print(i + ": 크롤링 안됨")
        again.append(i)

print("안된거: ", again)