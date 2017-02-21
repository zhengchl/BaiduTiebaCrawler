#encoding=utf-8

'''
百度贴吧主题列表的url示例
http://tieba.baidu.com/f?kw=%E5%A4%A9%E5%A4%A9%E5%BE%B7%E5%B7%9E
http://tieba.baidu.com/f?kw=%E5%A4%A9%E5%A4%A9%E5%BE%B7%E5%B7%9E&pn=0
http://tieba.baidu.com/f?kw=%E5%A4%A9%E5%A4%A9%E5%BE%B7%E5%B7%9E&ie=utf-8&pn=50
http://tieba.baidu.com/f?kw=%E5%A4%A9%E5%A4%A9%E5%BE%B7%E5%B7%9E&ie=utf-8&pn=100

贴吧帖子的url示例
http://tieba.baidu.com/p/4965638364
http://tieba.baidu.com/p/4966830781

帖子html示例：
<div id="post_content_103484160275" class="d_post_content j_d_post_content ">            天天德州里面的十日签活动，拿福字换了奖励，却没用奖励，用十天的换来的福却用完了，我就呵呵了，TM<a href="http://jump.bdimg.com/safecheck/index?url=rN3wPs8te/pL4AOY0zAwhz3wi8AXlR5gsMEbyYdIw620q6P4KNTgxO2jJ4m3Rd0yt6XyibVFgk4fbLMgytUg5Z4Q4OO30Ri8SAtVjSx1NjJY8K44RtEayPWmgLpz8y36hTdCT9IUs4T05hvgchh9CzxCZVKzLsIy7/LrcfWaVD0dJnZ4aIMtppuQye2MG4bWMDxm7iZ2BjQ="  class="ps_cb" target="_blank" onclick="$.stats.track(0, 'nlp_ps_word',{obj_name:'腾讯'});$.stats.track('Pb_content_wordner','ps_callback_statics')">腾讯</a>就是这么玩人的吗？？</div>
<div id="post_content_103484761972" class="d_post_content j_d_post_content ">            我也没到账</div>

帖子分页html示例
	<li class="l_pager pager_theme_5 pb_list_pager"><span class="tP">1</span>
<a href="/p/4889568200?pn=2">2</a>
<a href="/p/4889568200?pn=3">3</a>
<a href="/p/4889568200?pn=4">4</a>
<a href="/p/4889568200?pn=2">下一页</a>
<a href="/p/4889568200?pn=4">尾页</a>
</li>

'''

import urllib2
import urllib
from bs4 import BeautifulSoup
from urlparse import urljoin
import itertools
import socket
import re

timeout = 10
content_re = re.compile(r"post_content_\d+")
tiezi_url_re = re.compile(r"/p/\d+")
tiezi_pn_re = re.compile(r"/p/\d+\?pn=(?P<pn>\d+)")

class Tiezi(object):
    base_url = "http://tieba.baidu.com"
    def __init__(self, tiezi_url):
        self.tiezi_url_ = tiezi_url

        self.url_ = self.join_url()
        print self.url_

        self.pn_ = 1    # 帖子页码，默认一页
        self.fid_ = []  # 每页的内容
        self.soup_ = [] # 每页的soup
        self.fid_.append(urllib2.urlopen(self.url_))
        self.soup_.append(BeautifulSoup(self.fid_[0], "lxml"))

        # 检查帖子是否多页
        pf = self.soup_[0].find_all("li", {"class":"l_pager pager_theme_5 pb_list_pager"})
        if len(pf) == 0:
            return
        pf_urls = pf[0].find_all("a")
        for pf_url in pf_urls:
            mo = tiezi_pn_re.search(str(pf_url))
            cur_pn = int(mo.groupdict()["pn"])
            self.pn_ = cur_pn if cur_pn > self.pn_ else self.pn_

        # 拼接每页的url，并打开
        for pn in xrange(2, self.pn_+1):
            cur_url = "%s?pn=%d"%(self.url_, pn)
            print cur_url
            self.fid_.append(urllib2.urlopen(cur_url))
            self.soup_.append(BeautifulSoup(self.fid_[pn-1], "lxml"))


    def join_url(self):
        '''生成帖子的url'''
        return urljoin(Tiezi.base_url, self.tiezi_url_)

    def get_content(self):
        all_text = []
        for soup in self.soup_:
            contents = soup.find_all("div")
            for content in contents:
                if "id" in content.attrs and content_re.match(content["id"]):
                    all_text.append((self.url_, content.text.strip()))
        return all_text

class Zhuye(object):
    def __init__(self, keyword):
        self.url_ = "http://tieba.baidu.com/f?kw=%s"%(urllib.quote(keyword))

    def get_page_url(self, pn=1):
        '''生成指定页的url'''
        return "%s&pn=%d"%(self.url_, 50*(pn-1))

    def get_tiezi_list(self, pn):
        url = self.get_page_url(pn)
        print url
        fid = urllib2.urlopen(url)
        soup = BeautifulSoup(fid, "lxml")

        tiezi_list = []

        links = soup.find_all("a")
        for link in links:
            if "href" in link.attrs and tiezi_url_re.match(link["href"]):
                tiezi_list.append(link["href"])

        return tiezi_list


if __name__ == '__main__':
    socket.setdefaulttimeout(timeout)

    keyword = '天天德州'
    filename = 'result'

    tiezi_list = []
    zhuye = Zhuye(keyword)
    for i in xrange(1, 2):
        tiezi_list.extend(zhuye.get_tiezi_list(i))

    tiezi = [Tiezi(url) for url in tiezi_list]
    texts = [var.get_content() for var in tiezi]
    with open(filename, "w") as fid:
        for text in itertools.chain(*texts):
            fid.write("%s\t%s\n"%(text[0].encode('utf8'), text[1].encode('utf8')))