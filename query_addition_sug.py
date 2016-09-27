#!--encoding=utf-8
'''
Created on 2015年11月4日

@author: tiantian06
'''

from bs4 import BeautifulSoup
import urllib2
import sys
from sys import *
import argparse
import threading
from _ast import Add
import chardet

reload(sys)
sys.setdefaultencoding('utf-8')

class SubThread():
    def __init__(self):
        self.data = ''



def get_html_content(url):
    '''
    proxy = "61.233.25.166:80"
    proxies = {"http":"http://%s" % proxy}
    proxy_support = urllib2.ProxyHandler(proxies)
    proxy_support = urllib2.ProxyHandler(proxies)
    opener = urllib2.build_opener(proxy_support, urllib2.HTTPHandler(debuglevel=1))
    urllib2.install_opener(opener)
    '''
    headers = { #伪装为浏览器抓取
    'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'
    }
    html = ''
    req = urllib2.Request(url,headers=headers)
    try:
        html = urllib2.urlopen(req,timeout=10).read()
    except:
        pass
    return html


def get_query_addition_base(query):
    """"demo how to use beautifulsoup to process complex html"""
    url_list = get_url_list(query)
    addition = ''

    for url in url_list[:3]:
        html = get_html_content(url)
        try:
            soup = BeautifulSoup(html,"lxml",from_encoding='gbk')
        except:
            continue
        head = soup.find(name="meta", attrs={"name":"description"})
        if head !=None:
            addition = addition + head['content']
            break
        else:
            continue
    return addition


def get_url_list(query,pn=0):
    url = "https://www.baidu.com/s?ie=utf-8&f=8&rsv_bp=0&rsv_idx=1&tn=baidu&wd={query}&pn=%s"%pn
    query=query.replace(' ','%20')
    url = url.format(query=query)
    html = get_html_content(url)
    soup = BeautifulSoup(html,'lxml')
    url_list = []
    souplist = soup.findAll(name="h3", attrs={"class":"t c-gap-bottom-small"})
    if len(souplist) > 0:
        for soup in souplist:
            tag_a = soup.find(name = 'a')
            url_list.append(tag_a['href'])
    else:
        souplist = soup.findAll(name="div", attrs={"class":"result c-container "})
        if len(souplist) > 0:
            for soup in souplist:
                tag_a = soup.find(name="h3", attrs={"class":"t"}).find(name="a")
                url_list.append(tag_a['href'])
    return url_list


def get_query_addition(query):
    addition = get_query_addition_base(query)
    return addition





if __name__ == "__main__":

    add = get_query_addition('泄洪万吨鲟鱼逃逸')
    print len(add),type(add),add

