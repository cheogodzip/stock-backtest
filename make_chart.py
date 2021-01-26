import openpyxl
import pandas as pd
from matplotlib import pyplot

wb = openpyxl.load_workbook('result_201216-edit(+4,-2).xlsx')
sheet = wb.active

df = pd.DataFrame(sheet.values)
target = []
print(len(df))
for i in range(len(df)):
    target.append(df.loc[i][0])
df.index = target
df.columns = df.iloc[0, :]
df = df.iloc[1:, :]
del df['날짜']

pyplot.rcParams["font.family"] = 'Malgun Gothic'
pyplot.rcParams["font.size"] = 10
pyplot.rcParams["figure.figsize"] = (20, 10)

df['수익'].plot(color='#ff0000')
pyplot.grid()
pyplot.legend()
pyplot.title("백테스트 결과")
pyplot.xlabel("날짜")
pyplot.ylabel("수익")
pyplot.show()