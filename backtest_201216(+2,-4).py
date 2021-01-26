import sqlite3
from pandas import Series, DataFrame

f = open("trading_day(20170102-).txt")
trading_day = f.read().split(',')
f.close()

f = open("ticker_list.txt", 'r')
ticker_list = f.read().split(',')
f.close()

#start: 20170109

con1 = sqlite3.connect("ohlcv.db")
cursor1 = con1.cursor()
record_df = DataFrame(columns=['예수금', '수익', '매매내역', '승률'], index=range(0))
record_df.loc['2017-01-06 00:00:00'] = [10000000, 1, [], []]
for i in range(5, len(trading_day)):
    print(trading_day[i])
    yesterday = record_df.loc[trading_day[i-1]]
    record_df.loc[trading_day[i]] = [yesterday['예수금'], yesterday['수익'], [], []]
    #매수 로직
    #전일 종가 천원 이상 만오천원 이하
    target = []
    for ju in ticker_list:
        # 1거래일 전 종가
        try:  # 만약 없는 날짜를 조회하는 거면 에러나서 다음 종목으로 넘어가도록
            query = 'SELECT "종가" FROM "' + ju + '" WHERE 날짜 == "' + str(trading_day[i - 1]) + '"'
            cursor1.execute(query)
            jong_before_1 = cursor1.fetchall()[0][0]
            query = 'SELECT "시가" FROM "' + ju + '" WHERE 날짜 == "' + str(trading_day[i]) + '"'
            cursor1.execute(query)
            siga = cursor1.fetchall()[0][0]
            if siga == 0:
                continue
        except:
            continue

        if 1000 <= jong_before_1 <= 15000:
            target.append(ju)

    #거래량 데이터프레임
    target_dict = {}
    for ju in target:
        #5거래일 동안의 거래량의 합
        volume = 0
        try:  # 만약 없는 날짜를 조회하는 거면 에러나서 다음 종목으로 넘어가도록
            for k in range(1,6):
                query = 'SELECT "거래량" FROM "' + ju + '" WHERE 날짜 == "' + str(trading_day[i - k]) + '"'
                cursor1.execute(query)
                volume += cursor1.fetchall()[0][0]

            if volume < 1000:
                continue
            target_dict[ju] = volume
        except:
            continue
    volume_df = DataFrame(list(target_dict.values()), index = list(target_dict.keys()), columns=['volume'])

    #하락률 데이터프레임
    target_dict = {}
    for ju in target:
        # 5거래일 전 시가, 1거래일 전 종가
        try:  # 만약 없는 날짜를 조회하는 거면 에러나서 다음 종목으로 넘어가도록
            query = 'SELECT "종가" FROM "' + ju + '" WHERE 날짜 == "' + str(trading_day[i - 1]) + '"'
            cursor1.execute(query)
            jong_before_1 = cursor1.fetchall()[0][0]
            query = 'SELECT "시가" FROM "' + ju + '" WHERE 날짜 == "' + str(trading_day[i - 5]) + '"'
            cursor1.execute(query)
            si_before_5 = cursor1.fetchall()[0][0]

            decline_rate = jong_before_1 / si_before_5
            target_dict[ju] = decline_rate
        except:
            continue
    decline_df = DataFrame(list(target_dict.values()), index = list(target_dict.keys()), columns=['decline_rate'])

    #데이터프레임 순위 매기기
    volume_df['거래량 순위'] = volume_df['volume'].rank(ascending=False, method='average')
    decline_df['하락률 순위'] = decline_df['decline_rate'].rank(method='average')

    #데이터프레임 합치기
    target_df = DataFrame.merge(volume_df, decline_df, left_index=True, right_index=True, how='left')
    target_df['순위합'] = target_df['거래량 순위'] + target_df['하락률 순위']
    target_df = target_df.sort_values(by='순위합')
    target = target_df.index.to_list()[:10]

    #매매
    if record_df.loc[trading_day[i]]['예수금'] >= 10000000:
        allot = 1000000
    else:
        allot = record_df.loc[trading_day[i]]['예수금'] // 10
    report = ""
    win = 0
    lose = 0
    for ju in target:
        #매수
        query = 'SELECT "시가" FROM "' + ju + '" WHERE 날짜 == "' + str(trading_day[i]) + '"'
        cursor1.execute(query)
        siga = int(cursor1.fetchall()[0][0])
        try:
            vol = allot // siga
        except:
            print(ju + "error")
            continue

        record_df.loc[trading_day[i]]['예수금'] -= siga * vol
        #매도
        query = 'SELECT "고가" FROM "' + ju + '" WHERE 날짜 == "' + str(trading_day[i]) + '"'
        cursor1.execute(query)
        high = cursor1.fetchall()[0][0]
        if siga*1.02 < high:
            record_df.loc[trading_day[i]]['예수금'] += siga * vol * 1.02 * 0.997
            report += (ju + ": +2%, ")
            win += 1
        else:
            query = 'SELECT "저가" FROM "' + ju + '" WHERE 날짜 == "' + str(trading_day[i]) + '"'
            cursor1.execute(query)
            low = cursor1.fetchall()[0][0]
            if siga*0.96 > low:
                record_df.loc[trading_day[i]]['예수금'] += siga * vol * 0.96 * 0.997
                report += (ju + ": -4%, ")
                lose += 1
            else:
                query = 'SELECT "종가" FROM "' + ju + '" WHERE 날짜 == "' + str(trading_day[i]) + '"'
                cursor1.execute(query)
                close = cursor1.fetchall()[0][0]
                record_df.loc[trading_day[i]]['예수금'] += close * vol * 0.997
                report += (ju + ": 종가, ")
                if siga < close:
                    win += 1
                else:
                    lose += 1

    record_df.loc[trading_day[i]]['매매내역'].append(report)

    #수익
    record_df.loc[trading_day[i]]['수익'] = (record_df.loc[trading_day[i]]['예수금'])/10000000
    # 승패
    record_df.loc[trading_day[i]]['승률'] = (win/10)

con1.close()

print(record_df)
record_df.to_excel("result_201216(+2,-4).xlsx")