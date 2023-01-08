from datetime import datetime
import requests, bs4

def _main():
    print(getNewsContent('BAFCBD53-2781-494A-A9DB-686A91B8D992'))
    """
    d = datetime.strptime(input(), '%Y/%m/%d')
    j = getNewsList(d)
    for i in range(len(j)):
        print('------', i, '------\n', j[i]['V1'], j[i]['V2'], '\n', j[i]['content'])
    """

def getNewsList(d): #獲取某日新聞列表
    url = f"https://fund.megabank.com.tw/ETFData/djjson/ETNEWSjson.djjson?a=1&b={d}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"}
    r = requests.get(url, headers = headers)
    j = r.json()['ResultSet']['Result']
    count = 0
    while count < len(j):
        if j[count]['V1'] == d:
            count += 1
        else:
            break
    return j[:count]

def getNewsContent(A):  #獲取新聞內文
    url = f"https://fund.megabank.com.tw/ETFData/djhtm/ETNEWSContentMega.djhtm?&A={A}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"}
    r = requests.get(url, headers = headers)
    soup = bs4.BeautifulSoup(r.text, 'lxml')
    content = soup.find('td', class_ = 'NewsContent-Down')
    section = content.find('p')
    text = ''
    if section != None:
        text = section.text
        while section.next_sibling != None:
            section = section.next_sibling
            if isinstance(section, bs4.element.NavigableString):
                st = section.replace('\n', '')
                if st != '':
                    text += '\n\n' + st
            else:
                st = section.text.replace('\n', '')
                if st != '':
                    text += '\n\n' + st
    return text

if __name__ == '__main__':
    _main()
