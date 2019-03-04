import time
import sys

import dbsetting
import re
import socket
timeout = 10
socket.setdefaulttimeout(timeout)
import threading
import urllib
from urllib import request
from bs4 import BeautifulSoup
import pymongo

class letterbreakThread (threading.Thread):
    myclient = dbsetting.myclient
    mydb = dbsetting.mydb
    situation = mydb["situation"].find_one()
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        mycol = self.mydb["letterbreak"]
        mycol2=self.mydb["letterresult"]
        mycol3=self.mydb["cataloglsit"]
        mycol4 = self.mydb["catalogqueue"]
        print(self.mydb["situation"].find_one())
        while (self.mydb["situation"].find_one()['stepone']=='running'):
            for x in mycol2.find():
                if(mycol.find_one(x)==None):
                    mycol.insert(x)
                    for i in range(1, int(x['page'])):
                        mycol3.insert({'catalogurl':x['letter']+'/page/'+str(i)})
                        mycol4.insert({'catalogurl': x['letter'] + '/page/' + str(i)})
                        print('更新了一次对字母的分析')
            time.sleep(3)

        for x in mycol2.find():
            if (mycol.find_one(x) == None):
                mycol.insert(x)
                for i in range(1, int(x['page'])):
                    mycol3.insert({'catalogurl': x['letter'] + '/page/' + str(i)})
                    mycol4.insert({'catalogurl': x['letter'] + '/page/' + str(i)})
        print('字母的分析分析已完成')


class moviequeueThread (threading.Thread):
    myclient = dbsetting.myclient
    mydb = dbsetting.mydb
    situation = mydb["situation"].find_one()
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        mycol = self.mydb["movielist"]
        mycol2=self.mydb["moviequeue"]
        mycol3=self.mydb["movieurl"]
        #mycol4 = self.mydb["catalogqueue"]
        print(self.mydb["situation"].find_one())
        while (self.mydb["situation"].find_one()['steptwo']=='running'):
            for x in mycol3.find():
                if(mycol.find_one({'url':x['url']})==None):
                    mycol.insert(x)
                    mycol2.insert(x)
                    print('更新了一次条movie的r任务')
            time.sleep(3)

        for x in mycol3.find():
            if (mycol.find_one({'url': x['url']}) == None):
                mycol.insert(x)
                mycol2.insert(x)
        print('movie的任务已全部获取')


class tvqueueThread (threading.Thread):
    myclient = dbsetting.myclient
    mydb = dbsetting.mydb
    situation = mydb["situation"].find_one()
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        mycol = self.mydb["tvlist"]
        mycol2=self.mydb["tvqueue"]
        mycol3=self.mydb["tvurl"]
        #mycol4 = self.mydb["catalogqueue"]
        print(self.mydb["situation"].find_one())
        while (self.mydb["situation"].find_one()['steptwo']=='running'):
            for x in mycol3.find():
                if(mycol.find_one({'url':x['url']})==None):
                    mycol.insert(x)
                    mycol2.insert(x)
                    print('更新了一次条tv的r任务')
            time.sleep(3)

        for x in mycol3.find():
            if (mycol.find_one({'url': x['url']}) == None):
                mycol.insert(x)
                mycol2.insert(x)
        print('tv的任务已全部获取')


class moviefinnalThread (threading.Thread):
    myclient = dbsetting.myclient
    mydb = dbsetting.mydb
    situation = mydb["situation"].find_one()
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        mycol = self.mydb["zonatorrent_movie_info"]

        mycol3=self.mydb["movieitem"]
        #mycol4 = self.mydb["catalogqueue"]
        print(self.mydb["situation"].find_one())
        while (self.mydb["situation"].find_one()['stepthree']=='running'):
            for x in mycol3.find():
                if(mycol.find_one({'page_url':x['page_url']})==None):
                    mycol.insert(x)

                    print('更新了一条movie的结果')
            time.sleep(3)

        for x in mycol3.find():
            if (mycol.find_one({'page_url': x['page_url']}) == None):
                mycol.insert(x)

        print('movie的所有结果已全部获取')


class tvdownloadurlThread (threading.Thread):
    myclient = dbsetting.myclient
    mydb = dbsetting.mydb
    situation = mydb["situation"].find_one()
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        mycol = self.mydb["tvitem"]
        mycol2 = self.mydb["tvdownloadlist"]
        mycol3=self.mydb["tvdownloadlqueue"]
        #mycol4 = self.mydb["catalogqueue"]
        print(self.mydb["situation"].find_one({}))
        while (self.mydb["situation"].find_one({})['stepfour']=='running'):
            for x in mycol.find():
                if(mycol2.find_one({'page_url':x['page_url']})==None):
                    for downloadurl in x['download_url']:
                        mycol2.insert({'page_url':x['page_url'],'name':downloadurl['name'],'url':downloadurl['url']})
                        mycol3.insert({'page_url':x['page_url'],'name':downloadurl['name'],'url':downloadurl['url']})


                    print('更新了一条下载链接的结果')
            time.sleep(3)

        for x in mycol3.find():
            if (mycol.find_one({'page_url': x['page_url']}) == None):
                for downloadurl in x['download_url']:
                    mycol2.insert({'page_url': x['page_url'], 'name': downloadurl['name'], 'url': downloadurl['url']})
                    mycol3.insert({'page_url': x['page_url'], 'name': downloadurl['name'], 'url': downloadurl['url']})

        print('movie的所有结果已全部获取')

class tvfinnalThread (threading.Thread):
    myclient = dbsetting.myclient
    mydb = dbsetting.mydb
    situation = mydb["situation"].find_one()
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        situation=self.situation
        while True:
            time.sleep(5)
            situation = self.mydb["situation"].find_one()
            if (bool(situation['stepone'] == 'done') and bool(situation['steptwo'] == 'done') and bool(  situation['stepthree'] == 'done') and bool(situation['stepfour'] == 'done') and bool(     situation['stepfive'] == 'done')):
                time.sleep(5)
                situation = self.mydb["situation"].find_one()
                if (bool(situation['stepone'] == 'done') and bool(situation['steptwo'] == 'done') and bool(
                    situation['stepthree'] == 'done') and bool(situation['stepfour'] == 'done') and bool(
                    situation['stepfive'] == 'done')):

                        print("所有数据爬取完毕")
                        break

        print("汇总")
        mycol = self.mydb["tvtemp"]

        mycol3=self.mydb["downloadresult"]
        for x in mycol3.find({}):

            item=mycol.find_one({'page_url':x['page_url']})

            print(x['url'])
            if(item):
                for epi in item['download_url']:
                    if(x['language']!=''):
                        item['language']=x['language']
                    if(epi['name']==x['name']):
                        epi['url']=x['url']
                        x = mycol.update({'page_url':x['page_url']}, {"$set":item})
                        break

        x = self.mydb['tvtemp'].find({})
        mycol = self.mydb['zonatorrent_movie_info']

        for result in x:
            mycol.insert(result)
        print('已获得所有tv的下载链接')
