import sqlite3

def _main():
    checkNews('')
    
#建立資料庫
def _create():
    conn = sqlite3.connect('news.db')
    try:
        sql = """create table news(
                news_id integer,
                url text,
                date text,
                title text,
                context text,
                emotion real,
                primary key(news_id autoincrement))"""
        conn.execute(sql)
        sql = """create table keywords(
                news_id integer,
                words text,
                foreign key(news_id) references news(news_id))"""
        conn.execute(sql)
        sql = """create table emotionWords(
                word text,
                score real,
                primary key(word))"""
        conn.execute(sql)
        print('資料庫建立完成')
    except sqlite3.OperationalError:
        print("資料表已存在")
    finally:
        conn.close()

#從字典建立情緒關鍵字資料庫
def _default_emotion_from_dict():
    conn = sqlite3.connect('news.db')
    with open("dict/ntusd-positive.txt", encoding = 'utf-8') as f:
        words = f.readlines()
        for s in words:
            sql = 'insert or ignore into emotionWords values (?,?)'
            conn.execute(sql, (s.replace('\n', ''), 1))
            print(s)
        conn.commit()
    with open("dict/ntusd-negative.txt", encoding = 'utf-8') as f:
        words = f.readlines()
        for s in words:
            sql = 'insert or ignore into emotionWords values (?,?)'
            conn.execute(sql, (s.replace('\n', ''), -1))
            print(s)
        conn.commit()
    conn.close()
    print('情緒字典加入完成')

def insertNews(url, date, title, context, emotion):
    conn = sqlite3.connect('news.db')
    sql = 'insert into news(url, date, title, context, emotion) values(?,?,?,?,?)'
    conn.execute(sql, (url, date, title, context, emotion))
    conn.commit()
    rowid = conn.execute("select last_insert_rowid()").fetchone()[0]
    conn.close()
    return rowid

def getNews(date):
    conn = sqlite3.connect('news.db')
    sql = f'select news_id, title, context, emotion from news where date = "{date}"'
    news = conn.execute(sql).fetchall()
    news_dict = []
    if news != None:
        for n in news:
            sql = f'select words from keywords where news_id = {n[0]}'
            keywords = conn.execute(sql)
            word_list = []
            for k in keywords:
                word_list.append(k[0])
            news_dict.append({
                'id' : n[0],
                'title' : n[1],
                'content' : n[2],
                'emotion' : n[3],
                'keywords' : word_list
                })
    conn.close()
    return news_dict

def checkNews(url):
    conn = sqlite3.connect('news.db')
    sql = f'select * from news where url = "{url}"'
    news = conn.execute(sql).fetchone()
    conn.close()
    return False if news == None else True
    
def insertKeywords(newsid, words):
    if newsid == 0:
        return
    conn = sqlite3.connect('news.db')
    for s in words:
        sql = 'insert into keywords(news_id, words) values (?,?)'
        conn.execute(sql, (newsid, s))
    conn.commit()
    conn.close()

def updateKeywords(newsid, newWords):
    conn = sqlite3.connect('news.db')
    sql = f'delete from keywords where news_id = {newsid}'
    conn.execute(sql)
    for s in newWords:
        sql = 'insert into keywords(news_id, words) values (?,?)'
        conn.execute(sql, (newsid, s))
    conn.commit()
    conn.close()

def insertEmotionWords(word, score):
    conn = sqlite3.connect('news.db')
    sql = 'insert or ignore into emotionWords values (?,?)'
    conn.execute(sql, (word, score))
    conn.commit()
    conn.close()

def updateEmotionWordsScore(word, score):
    conn = sqlite3.connect('news.db')
    sql = f'update emotionWords set score = {score} where word = "{word}"'
    conn.execute(sql)
    conn.commit()
    conn.close()

def delEmotionWords(word):
    conn = sqlite3.connect('news.db')
    sql = f'delete from emotionWords where word = "{word}"'
    conn.execute(sql)
    conn.commit()
    conn.close()

def getEmotionScore(word):
    conn = sqlite3.connect('news.db')
    sql = f'select score from emotionWords where word = "{word}"'
    score = conn.execute(sql).fetchone()
    conn.close()
    return 0 if score == None else score[0]

if __name__ == '__main__':
    _main()
