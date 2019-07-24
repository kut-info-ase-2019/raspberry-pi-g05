import pymysql.cursors
import datetime

def main():
    conn = pymysql.connect(
        user='add',	 # addの場合はユーザ名addを用いる必要あり
        passwd='raspberry',
        host='localhost',
        db='kaitekikun'
    )

    now = datetime.datetime.now()	# 現在時刻の読み込み
    timekey = '{0:%Y-%m-%d %H:%M:%S}'.format(now)	# 現在時刻を文字列に変換

    c = conn.cursor()
    sql = 'insert into environmenttable (placeID, time, temprature, humidity, human, noise) values (%s,%s,%s,%s,%s,%s);'
    c.execute(sql, (1, timekey, 120, 28, 8, 19)) # 追加を行うSQL文の実行
    conn.commit()		# add結果をcommit

    # 現状ではユーザ名addに閲覧権限がないため下記をコメントアウトしている
    #print('* enviromenttableの一覧を表示\n')
    #sql2 = 'select * from environmenttable;'
    #c.execute(sql2)
    #for row in c.fetchall():#rowという配列に取ってきたデータ代入
    #    print(row[0], row[1], row[2], row[3], row[4], row[5])
main()
