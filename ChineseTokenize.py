#encoding=utf-8

import re

import jieba
from nltk.corpus import stopwords

# import sys  

# reload(sys)  
# sys.setdefaultencoding('utf8')


sent_split_re = re.compile(u"[。！？：]+") # 分割句子的标点

# 排除的标点
punct_set = set(u'''~:!),.:;?]}¢'"、。〉》」』】〕〗〞︰︱︳﹐､﹒＋
﹔﹕﹖﹗﹚﹜﹞！），．：；？｜｝︴︶︸︺︼︾﹀﹂﹄﹏､～￠
々‖•·ˇˉ―--′’”([{£¥'"‵〈《「『【〔〖（［｛￡￥〝︵︷︹︻
︽︿﹁﹃﹙﹛﹝（｛“‘-—_…`!@#$%^&*()-_+=[{}];:\'\",./|\\<>? ''')

init_stops = None

def getStops(path="chinese_stopword.txt"):
    '''获得中文+英文stop_word，中文stop_word来自配置文件，英文来自nltk'''
    stops_set = set()
    with open(path) as fid:
        for line in fid:
            word = line.decode("utf8").rstrip()
            if word:
                stops_set.add(word)
    english_stops = set(stopwords.words("english"))

    return stops_set.union(english_stops)

def sentenceTokenize(paragraph):
    '''使用正则表达式sent_split_re分割句子'''
    sentences = sent_split_re.split(paragraph)

    return sentences

def wordTokenize(sentence, methods="jieba"):
    '''分词，并：1. 删除stopword 2. 去除标点'''

    global init_stops
    if not init_stops:
        init_stops = getStops()

    if methods == "jieba":
        words = jieba.cut(sentence)
    elif methods == "simple":
        words = [w for w in sentence] # 直接分词

    words = [w for w in words if not w in init_stops] #删除stopword
    filterpunt = lambda s: ''.join(filter(lambda x: x not in punct_set, s))
    words = [filterpunt(w) for w in words] #去除标点
    words = [w for w in words if w] #删除空词

    return words

def chineseTokenize(cs):
    '''入口'''
    sentences = sentenceTokenize(cs)
    words = [wordTokenize(sentence) for sentence in sentences if sentence]

    return words

if __name__ == '__main__':
    in_filename = "result_dezhou"
    out_filename = "cut_dezhou"

    infid = open(in_filename)
    outfid = open(out_filename, "w")

    for line in infid:
        try:
            url, cs = line.rstrip().decode('utf8').split('\t', 2)
        except ValueError:
            print "error at line:%s" %line.rstrip().decode('utf8').encode('gbk')
        words_list = chineseTokenize(cs.strip())
        words_str = u"】【".join(u"/".join(words) for words in words_list)
        outfid.write("%s\t%s\t%s\n"%(url.encode('utf8'), cs.encode('utf8'), words_str.encode('utf8')))

    infid.close()
    outfid.close()
