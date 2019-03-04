# -*- coding:utf-8 -*-
import re
import socket
timeout = 100
socket.setdefaulttimeout(timeout)
import threading
import urllib
from urllib import request
from bs4 import BeautifulSoup
import dbsetting
import datetime as dt
import sys

flag=0
dict={}
myclient = dbsetting.myclient
mydb = dbsetting.mydb
# -*- coding: utf-8 -*-

class movieThread (threading.Thread):
    Rurl = 'https://zonatorrent.tv/letters/'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}
    def __init__(self, murl):
        threading.Thread.__init__(self)
        self.murl = murl

    def run(self):
        try:
            print(self.murl)
            req = urllib.request.Request(url=self.murl, headers=self.headers)


            response = urllib.request.urlopen(req).read()
            soup = BeautifulSoup(response, "html.parser")
            ablume_type='0'
            backdrop_path = soup.find("img", attrs={'class': 'TPostBg'})['src']
            bludv_name = soup.find("h1", attrs={'class': 'Title'}).string

            original_title = ''
            director = []
            main_actor = []
            service_type = []
            temps = soup.find_all("strong")
            for temp in temps:
                if temp.text == 'Director:':
                    director = temp.parent.text.split(":", 1)[1].lstrip().split(",")

                if temp.text == 'Título original:':
                    original_title = temp.parent.text.split(":", 1)[1].lstrip()
                if temp.text == 'Género:':
                    service_type = temp.parent.text.split(":", 1)[1].lstrip().split(",")

            for actor in soup.find_all('figcaption'):
                main_actor.append(actor.text)

            language = ''
            download_url=''
            if  soup.find("tbody"):
                language = soup.find("tbody").tr.td.next_sibling.next_sibling.next_sibling.text.lstrip()

                download_url = [{'name':bludv_name,'url':soup.find("a", attrs={'class': 'Button STPb torrent-movie'})['href']}]

            if soup.find("div", attrs={'class': 'Description'}).p:
                overview = soup.find("div", attrs={'class': 'Description'}).p.text
            else:
                overview = soup.find("div", attrs={'class': 'Description'}).text
            page_url =self.murl
            poster_path = soup.find("div", attrs={'class': 'Image'}).figure.img['src']
            if soup.find("span", attrs={'class': 'Date AAIco-date_range'}):
                release_date = soup.find("span", attrs={'class': 'Date AAIco-date_range'}).string
                time = dt.datetime.strptime(release_date, '%d-%m-%Y')
                release_date = time.strftime('%Y-%m-%d')
                year = time.strftime('%Y')
            else:
                release_date=''
                year=''

            vote_average = soup.find("div", attrs={'id': 'TPVotes'})['data-percent']
            vote_average = str(float(vote_average) / 10)


            mydict = {"ablume_type":ablume_type,'backdrop_path':backdrop_path,'bludv_name':bludv_name,'original_title':original_title,'director':director,'service_type':service_type,
                      'main_actor':main_actor,'language':language,'download_url':download_url,'overview':overview,'page_url':page_url,'poster_path':poster_path,'release_date':release_date,'year':year,'vote_average':vote_average}
            print(mydict)
            global dict
            dict = mydict

        except Exception as ex:
            print(self.murl + '页数获取失败（可能由于超时等原因）')

            print(ex)


    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()


if(len(sys.argv)<1):
    sys.exit('请传入需要爬取的url')
print("开始爬取"+sys.argv[1])
print(sys.argv[1])
thread2 = movieThread(sys.argv[1])
thread2.start()

thread2.join()
print(dict)

#以下是把爬取到的结果放进数据库中
mycol = mydb["zonatorrent_movie_info"]
if dict:
    if(mycol.find_one({'page_url':dict['page_url']})==None):
        mycol.insert(dict)
    else:print("数据库中已有此链接")