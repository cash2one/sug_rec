#!/bin/env python
#coding=utf-8
import json                                                     #导入Json模块
import string
import matplotlib.pyplot as plt
import numpy as np
  
def processJson(inputJsonFile):

    fin = open(inputJsonFile, 'r')

    final_score = []
    display_rec_weight = []
    for eachLine in fin:
        line = eachLine.strip().decode('utf-8')                #去除每行首位可能的空格，并且转为Unicode进行处理
        line = line.strip(',')    #去除Json文件每行大括号后的逗号
        if 'final_score'in line:
            score = line.split(':')
            final_score.append(int(score[1]))
        if 'display' in line:
            score = line.split(':')
            display_rec_weight.append(int(score[1]))

    print len(final_score)
    desc_sort_score = final_score.sort(reverse = True)
   # print display_rec_weight
    x = [i+100 for i in range(len(final_score))]
    print final_score
    plt.plot(x[:436],final_score[:436],'.b',x[436:],final_score[436:],'.r')
    plt.ylabel('xrank score now')
def parseJson(inputJsonFile):
    items_file = open('items_file.txt','w')
    s = json.load(open(inputJsonFile,'r'))

    items =  s['items']
    list = []
    for item in items :
        if item['item_type']== 1:
            line = item['text']
            list.append(line.encode('utf-8'))
    return list
def parseJsonbyid(inputJsonFile):
    s = json.load(open(inputJsonFile,'r'))

    items =  s['items']
    list = []

    for item in items:
        if item['item_type'] == 1:
            line = item['id']
            list.append(line)
    return list

def parseJson2dict(inputJsonFile):

    s = json.load(open(inputJsonFile,'r'))

    items =  s['items']
    news = {}
    for item in items:
        if item['item_type'] == 1:
            id = item['id']
            text = item['text']
            news[id] =text.encode('utf-8')
    return news







    #     js = None
    #     try:
    #         js = json.loads(line)
    #         print '1'                                            #加载Json文件
    #     except Exception,e:
    #         print 'bad line'
    #         continue
    #                                                           #对您需要修改的项进行修改，xxx表示你要修改的内容
    #     # outStr = json.dumps(js, ensure_ascii = False) + ','    #处理完之后重新转为Json格式，并在行尾加上一个逗号
    #     # fout.write(outStr.strip().encode('utf-8') + '\n')      #写回到一个新的Json文件中去
    # fin.close()                                                #关闭文件
    # # fout.close()
if __name__ == "__main__":
    # processJson('xrank.json')
    parseJson('xrank.json')