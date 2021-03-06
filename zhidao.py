#!/usr/bin/python
# -*- coding: utf-8 -*-
import time
import traceback
import requests
from tieba import Tieba, TiebaError, get_random_sentense, print_message, rerun
from mydb import Tiedb, zhidao_whole
from IPdb import IPdb
import json
import re
import random
from random import choice
from reg_test import Reg_test
from IP_test import Getmyip
import sys
from question import NLP_process


reload(sys)
sys.setdefaultencoding("utf-8")
senten1 = [
    '好像在哪听过',
    '好像确实听过',
    '有点印象耶',
    '前几天还听过呢记不太清',
    '哎确实想知道是什么歌',
    '好像在哪个酒吧听过',
    '好像在丽江听哪个歌手唱过',
    '好像在电视里听过',
    '好像真的有印象耶',
    ]
senten2 = [
    '可以用音乐雷达的哼唱识别功能试试如果记得旋律的话',
    '有声音的话可以下载音乐雷达的音乐识别',
    '用音乐雷达的哼唱识别功能看能不能找到这首歌',
    '这首歌用音乐雷达的声音识别看能不能找到',
    '用音乐雷达的声音识别看能找到吗',
    '好像音乐雷达有一个哼唱功能哼出旋律就能识别歌曲',
    '好像音乐雷达有听歌识曲的功能放出来就能识别歌曲',
    ]

senten3 = [
    '。',
    '。。',
    '。。。',
    '。。。。',
    '~_~',
    '~_~。',
    '~_~。。',
    ]

q_re = re.compile('<a href="(http://zhidao.baidu.com/question/\d+\.html)".*?<em>(.*?)</em></a>')

def yield_q():
    for i in range(0, 460, 10):
        msg = requests.get('http://zhidao.baidu.com/search?word=%D5%E2%CA%D7%B8%E8%BD%D0%CA%B2%C3%B4%C3%FB%D7%D6&ie=gbk&site=-1&sites=0&date=3&pn='+str(i)).content.decode('gbk')
        for row in re.findall(r'<a href="(http://zhidao.baidu.com/question/\d+\.html)".*?<em>(.*?)</em>.*?<dd class="dd summary">.*?</i>(.*?)</dd>', msg, re.DOTALL):
            yield [i.encode('utf8') for i in row]
            # yield row[0].encode('utf8'), row[1].encode('utf8')

def get_random_senten(insert=''):
    return '%s %s%s%s' % (choice(senten1), choice(senten2), insert, choice(senten3))

def get_cur_ts():
    return str(time.time()).replace('.', '0')

myIPdb=IPdb()
proxy_dict=['http://113.11.198.163:2223/','http://113.11.198.167:2223/','http://113.11.198.168:2223/','http://113.11.198.169:2223/',]        
current_IP=''
tiebadb = Tiedb()
reg=Reg_test()        
zhidaodb = zhidao_whole()
myNLP=NLP_process()
#temp_word='确实挺熟悉的'
@rerun
def answer_search():
    #tieba = Tieba('eternalcxx0302', 'yanhuai0202')
    username, passwd = tiebadb.get_random_bd_user()
    print username, passwd
    current_IP=random.choice(proxy_dict)
    print 'current_IP:',current_IP
    tieba = Tieba(username, passwd,{'http':current_IP})
    tieba.login()
    switch_user=0
    p = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    questions=list(zhidaodb.get_questions())
    random.shuffle(questions)
    temp_word=questions[0][1]
    random.shuffle(questions)
    
    for row in questions:
        try:    
            qid = row[0]
            title = row[1]#.decode('utf8')
            print '获得qid：',qid
            print '获得title：',title
            senten=''
            senten_left=''
            if not tiebadb.is_q_in(qid) or tiebadb.is_q_in(qid) and tiebadb.is_q_shown(qid)[0]<=1:
                switch_user=switch_user+1
                if switch_user%5==0:
                    print 'switch to another user....'
                    username, passwd = tiebadb.get_random_bd_user()
                    print_message('%s\t%s' % (username, passwd))
                    current_IP=random.choice(proxy_dict)
                    tieba = Tieba(username, passwd,{'http':current_IP})
                    tieba.login()

                NLP_reply=myNLP.reply(title)
                if NLP_reply!='':
                    print '获得NLP回答：',NLP_reply
                    temp_word=NLP_reply+'我去找找,'
                first_sen=senten1[random.randint(0,len(senten1)-1)]
                print first_sen,len(first_sen)
                second_sen=senten2[random.randint(0,len(senten2)-1)]
                print second_sen,len(second_sen)
                senten=temp_word+','+first_sen[0:random.randrange(3,(len(first_sen)-1),3)]+','+second_sen[0:random.randrange(12,(len(second_sen)-1),3)]
                #senten=temp_word+first_sen[0:3]+','+second_sen[0:3]
                try:            
                    print '回答前：',senten
                    tieba.answer_q(qid, senten)
                    print '回答成功，入库前：',qid, senten,'et',current_IP
                    tiebadb.save_question(qid, senten,username,current_IP)
                except TiebaError, e:
                    print '回答内错误',e
                #time.sleep(choice([1, 2])*10)
                temp_word=title
            else:
                print tiebadb.is_q_shown(qid),'answered_before',qid
        except TiebaError, e:
            print '回答外错误',e
            raise

# @rerun
def main():
    username, passwd = tiebadb.get_random_bd_user()
    print_message('%s\t%s' % (username, passwd))
    tieba = Tieba(username, passwd)
    try:

        
        q = tieba.get_questions()
        for row in q['data']['detail']:
            #username, passwd = tiebadb.get_random_bd_user()
            #print_message('%s\t%s' % (username, passwd))
            #tieba = Tieba(username, passwd)
            #tieba.login()
            # print row['title'].encode('utf8'), row['tagName'][0].encode('utf8')
            # continue
            if u'小时' in row['createTime']:
                return
            qid = row['qid'].encode('utf8')
            title = row['title'].encode('utf8')
            similar_answer = tieba.get_zhidao_similar(title)
            if similar_answer:
                answer = similar_answer.encode('utf8').replace('<font color="#C60A00">', '').replace('</font>', '')
                senten = answer# +',  也可以用音乐识别软件识别'
            else:
                senten = get_random_senten(choice(list(title.decode('utf8'))).encode('utf8'))
            # continue
            if not tiebadb.is_q_in(qid) and not '用户名' in title:
                answer_once(qid, senten)
    except TiebaError, e:
        print 'Answer Failed'
        raise

def get_tag():
    username, passwd = tiebadb.get_random_bd_user()
    print_message('%s\t%s' % (username, passwd))
    tieba = Tieba(username, passwd)
    try:
        tieba.login()
        tagdic = {}
        for i in xrange(0, 750, 25):
            q = tieba.get_questions(str(i))
            for row in q['data']['detail']:
                if row['tagName']:
                    tag = row['tagName'][0].encode('utf8')
                    tagdic[tag] = tagdic.get(tag, 0)+1
    except TiebaError, e:
        print e
    for row in sorted(tagdic.items(), key=lambda x: x[1], reverse=True):
        # print row
        print row[0], row[1]

def test():
    username, passwd = tiebadb.get_random_bd_user()
    print_message('%s\t%s' % (username, passwd))
    tieba = Tieba(username, passwd)
    try:
        tieba.login()
        q = tieba.get_zhidao_similar('这首歌叫什么名字', '在网上搜到的一个铃声，很好听，但是完全没有歌曲信息，我很想知道这首')
        print q.encode('utf8')
    except TiebaError, e:
        print e

if __name__ == "__main__":
    # main()
    # get_tag()
    # test()
    # yield_q()
    #temp_word='确实挺熟悉的'
    while True:

        for IP in myIPdb.get_fast_IP():
            fast_IP=str('http://'+IP[0])+':'+str(IP[1])+'/'
            proxy_dict.append(fast_IP)
            print fast_IP

            #print myIPdb.get_fast_IP()


        answer_search()
