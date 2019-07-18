import pymysql.cursors

def main():
    conn = pymysql.connect(
        user='user', #selectの場合
        passwd='raspberry',#適宜自分で設定したパスワードに書き換えてください。
        host='localhost',#接続先DBのホスト名或いはIPに書き換えてください。
        db='kaitekikun'
    )
    c = conn.cursor()

    # テーブルの作成
    sql = 'select * from environmenttable;' #
    c.execute(sql)
    print('* envanテーブルの一覧を表示\n')
    for row in c.fetchall():#rowという配列に取ってきたデータ代入
        print('No:', row[0], 'Time:', row[1])# 1 2019-06-11 17:21:18
main()
