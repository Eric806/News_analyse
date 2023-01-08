from datetime import datetime, timedelta
from wordcloud import WordCloud
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import tkinter as tk
import threading
from tkinter import messagebox
import crawler, db, ui, analyse

def _main():
    startup()

def startup():
    global app, show, newsList, showList, is_filter
    is_filter = False
    root = tk.Tk()
    app = ui.MainUI(root)
    show = tk.StringVar()
    init_ui()

    app.StartDate.insert(0,'2022/12/16')
    app.EndDate.insert(0,'2022/12/16')
    
    root.mainloop()

def init_ui():
    app.Search.configure(command = search_btn)
    app.ClearLog.configure(command = clearLog_btn)
    app.Crawler.configure(command = crawler_btn)
    app.Cloud.configure(command = cloud_btn)
    app.Filter.configure(command = filter_btn)
    app.LogText.tag_config('warn', backgroun="yellow", foreground = 'red')
    app.LogText.tag_config('sys', foreground = 'blue')
    app.NewsList.configure(listvariable = show)
    app.NewsList.bind('<<ListboxSelect>>', newsList_select)

#爬蟲獲取新聞並加入資料庫，然後查詢
def getRangeNews(start, end):
    now = start
    td = timedelta(1)
    while now <= end:
        date = datetime.strftime(now, '%Y/%m/%d')
        insertLog(f"正在下載{date}的新聞列表")
        news = crawler.getNewsList(date)
        #獲取新聞內文
        for n in news:
            exists = db.checkNews(n['V3'])
            if not exists:
                insertLog(f"正在下載網址{n['V3']}的新聞內文")
                content = crawler.getNewsContent(n['V3'])
                score = culEmotion(content)
                keywords = analyse.analyseNews(content)
                newsId = db.insertNews(n['V3'], n['V1'], n['V2'], content, score)
                db.insertKeywords(newsId, keywords)
        now += td
    insertLog(f'下載完成', 'sys')
    news = searchNews(start, end)
    return news

#查詢資料庫中的新聞
def searchNews(start, end):
    now = start
    td = timedelta(1)
    news = []
    while now <= end:
        date = datetime.strftime(now, '%Y/%m/%d')
        dayNews = db.getNews(date)
        newsAmount = len(dayNews)
        if newsAmount == 0:
            insertLog(f'資料庫中未搜索到{date}的新聞', 'warn')
        news += dayNews
        now += td
    insertLog(f'共搜索到{len(news)}條新聞', 'sys')
    return news

def culEmotion(text):
    text = analyse.cutNews(text)
    score = 0.0
    for t in text:
        score += db.getEmotionScore(t)
    return score

def cloud(dic):
    with open('dict/stop_words.txt', encoding = 'utf-8') as f:
        stop_words = f.read().splitlines()
    for s in stop_words:
        dic.pop(s, None)
    wc = WordCloud(background_color = 'white',
                   max_font_size = 120,
                   max_words = 75,
                   contour_width = 3,
                   font_path = "kaiu.ttf")
    return wc.fit_words(dic)

def showCloud(wc):
    plt.figure()
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    plt.show()

#計算正負情緒新聞數目
def culEmotionTotal(data):
    good = 0
    bad = 0
    for d in data:
        if d['emotion'] < 0:
            bad += 1
        elif d['emotion'] > 0:
            good += 1
    return [good, bad]

#將字詞出現次數整理為字典
def culWordsTotal(data):
    words = {}
    for d in data:
        for k in d['keywords']:
            words[k] = words.get(k, 0) + 1
    return words

def printNews(data):
    for i in range(len(data)):
        print(f'------{i}------')
        print(data[i]['title'], '\n')
        print(data[i]['content'], '\n')
        print('情緒分數：', data[i]['emotion'])
        print('關鍵字：', data[i]['keywords'], '\n')

def search_btn():
    try:
        startDate = app.StartDate.get()
        endDate = app.EndDate.get()
        start = datetime.strptime(startDate, "%Y/%m/%d")
        end = datetime.strptime(endDate, "%Y/%m/%d")
    except ValueError:
        messagebox.showwarning('格式錯誤', '請輸入正確的日期格式')
        return
    t = threading.Thread(target = search_btn_do, args = (startDate, endDate, start, end))
    t.start()
    btnWait(t)

def search_btn_do(startDate, endDate, start, end):
    global newsList, showList
    insertLog(f'開始搜尋資料庫中{startDate}至{endDate}的新聞', 'sys')
    newsList = searchNews(start, end)
    showList = newsList
    showNewsList(showList)
    app.Filter.configure(text='''篩選''')
    is_filter = False

def crawler_btn():
    try:
        startDate = app.StartDate.get()
        endDate = app.EndDate.get()
        start = datetime.strptime(startDate, "%Y/%m/%d")
        end = datetime.strptime(endDate, "%Y/%m/%d")
    except ValueError:
        messagebox.showwarning('格式錯誤', '請輸入正確的日期格式')
        return
    t = threading.Thread(target = crawler_btn_do, args = (startDate, endDate, start, end))
    t.start()
    btnWait(t)

def crawler_btn_do(startDate, endDate, start, end):
    global newsList, showList
    insertLog(f'開始爬蟲{startDate}至{endDate}的新聞', 'sys')
    newsList = getRangeNews(start, end)
    showList = newsList
    showNewsList(showList)
    app.Filter.configure(text='''篩選''')
    is_filter = False

def clearLog_btn():
    app.LogText.configure(state='normal')
    app.LogText.delete('1.0', 'end')
    app.LogText.configure(state='disabled')

def cloud_btn():
    if newsList != []:
        t = threading.Thread(target = cloud_btn_do)
        t.start()
        btnWait(t)
    else:
        messagebox.showwarning('錯誤', '新聞列表為空，請先進行搜尋')

def cloud_btn_do():
    insertLog(f'正在生成文字雲...', 'sys')
    words = culWordsTotal(newsList)
    c = cloud(words)
    insertLog(f'文字雲生成完成', 'sys')
    showCloud(c)

def filter_btn():
    text = app.FilterText.get().replace(" ", "")
    if text == "":
        messagebox.showwarning('錯誤', '請先輸入欲篩選的文字')
        return
    t = threading.Thread(target = filter_btn_do, args = (text,))
    t.start()

def filter_btn_do(text):
    global showList, is_filter
    if is_filter:
        app.Filter.configure(text='''篩選''')
        is_filter = False
        showList = newsList
        showNewsList(showList)
    else:
        app.Filter.configure(text='''返回''')
        is_filter = True
        showList = []
        for n in newsList:
            """
            if text in n["title"] or text in n["content"]:
                showList.append(n)
                """
            for k in n["keywords"]:
                if text == k:
                    showList.append(n)
        showNewsList(showList)

def btnWait(t):
    tb = threading.Thread(target = btnWait_, args = (t,))
    tb.start()

def btnWait_(t):
    app.Search.configure(state = 'disable')
    app.Crawler.configure(state = 'disable')
    app.Cloud.configure(state = 'disable')
    t.join()
    app.Search.configure(state = 'normal')
    app.Crawler.configure(state = 'normal')
    app.Cloud.configure(state = 'normal')
    
def newsList_select(event):
    w = event.widget
    if len(w.curselection()) == 1:
        index = int(w.curselection()[0])
        app.NewsTitle.configure(state = 'normal')
        app.NewsTitle.delete('1.0', 'end')
        app.NewsTitle.insert('1.0', showList[index]['title'])
        app.NewsTitle.configure(state='disable')
        app.NewsContent.configure(state='normal')
        app.NewsContent.delete('1.0', 'end')
        app.NewsContent.insert('1.0', showList[index]['content'])
        app.NewsContent.insert('end', f"\n\n關鍵字：{showList[index]['keywords']}")
        app.NewsContent.configure(state = 'disable')
        app.NewsEmotionScore.configure(text = f"情緒分數：{showList[index]['emotion']}")

def insertLog(text, tag = None):
    app.LogText.configure(state='normal')
    app.LogText.insert('end', text + '\n', tag)
    app.LogText.see('end')
    app.LogText.configure(state='disabled')

def showNewsList(showList):
    newsTitle = []
    for i in range(len(showList)):
        newsTitle.append(f"{i+1}. {showList[i]['title']}")
    show.set(newsTitle)
    for i in range(1, len(showList), 2):
        app.NewsList.itemconfig(i, background = "#c4c4c4")
    emotion = culEmotionTotal(showList)
    app.GoodNewsCount.configure(text=f"正面新聞數：{emotion[0]}則")
    app.BadNewsCount.configure(text=f"負面新聞數：{emotion[1]}則")

if __name__ == '__main__':
    _main()
