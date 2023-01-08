import jieba, jieba.analyse, re

jieba.set_dictionary('dict/dict.txt.big')
jieba.load_userdict('dict/userDict.txt')
jieba.analyse.set_stop_words('dict/stop_words.txt')
    
def _main():
    text = "'我是誰123"
    text = re.sub(r'[0-9a-zA-Z\"\']+', ' ', text)
    print(text)

def analyseNews(text):
    text = re.sub(r'[0-9a-zA-Z\"\']+', ' ', text)
    tags = jieba.analyse.extract_tags(text, topK = 10)
    return tags

def cutNews(text):
    text = re.sub(r'[0-9a-zA-Z\"\']+', ' ', text)
    cut = jieba.lcut(text)
    return cut

if __name__ == '__main__':
    _main()
