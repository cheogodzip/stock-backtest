from pykrx import stock
from pandas import DataFrame

df = stock.get_market_cap_by_ticker("20201208")
df = df.sort_values(by=['시가총액'], ascending=[True])
df2 = df[df['시가총액']<70000000000]
df2 = df2.sort_values(by=['시가총액'], ascending=[True])
df2.to_excel("sichong.xlsx")
print(df2.head)