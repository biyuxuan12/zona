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
dict={}

class tvThread(threading.Thread):
    Rurl = 'https://zonatorrent.tv/letters/'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}
    myclient = dbsetting.myclient
    mydb = dbsetting.mydb

    def __init__(self, murl):
        threading.Thread.__init__(self)
        self.murl = murl

    def run(self):
        try:

            print(self.murl)

            req = urllib.request.Request(url=self.murl, headers=self.headers)

            response = urllib.request.urlopen(req).read()

            soup = BeautifulSoup(response, "html.parser")

            ablume_type = '1'

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


            backdrop_path = soup.find("div", attrs={'class': 'TPostBg Objf'}).img['src']

            download_url = []
            season = soup.find_all("div", attrs={'class': 'Wdgt AABox'})
            print(season)
            snum = 1
            language = ''
            soup2 = 0
            for s in season:
                print(s)
                enum = 1

                sdurls = s.find_all("a", attrs={'class': 'MvTbImg'})
                for sdurl in sdurls:
                    print(sdurl['href'])
                    # req2 = urllib.request.Request(url=sdurl['href'], headers=self.headers)
                    # response2 = urllib.request.urlopen(req2).read()
                    # soup2 = BeautifulSoup(response2, "html.parser")
                    # if soup2.find("a", attrs={'class': 'Button STPb'}):
                    #     realurl = soup2.find("a", attrs={'class': 'Button STPb'})['href']
                    download_url.append({"name": 's' + str(snum) + 'e' + str(enum), "url": sdurl['href']})
                    #language = soup2.find("img", attrs={'alt': 'Idioma'}).find_parent().text.lstrip()
                    enum = enum + 1
                snum = snum + 1

            print(download_url)
            if soup.find("div", attrs={'class': 'Description'}).p:
                overview = soup.find("div", attrs={'class': 'Description'}).p.text
            else:
                overview = soup.find("div", attrs={'class': 'Description'}).text
            print(overview)
            page_url = self.murl
            poster_path = soup.find("div", attrs={'class': 'Image'}).figure.img['src']
            print(poster_path)
            if soup.find("span", attrs={'class': 'Date AAIco-date_range'}):
                release_date = soup.find("span", attrs={'class': 'Date AAIco-date_range'}).string
                time = dt.datetime.strptime(release_date, '%d-%m-%Y')
                release_date = time.strftime('%Y-%m-%d')
                print(release_date)
                year = time.strftime('%Y')
                print(year)
            else:
                release_date = ''
                year = ''
            vote_average = soup.find("div", attrs={'id': 'TPVotes'})['data-percent']
            vote_average = str(float(vote_average) / 10)
            print(vote_average)



            mydict = {"ablume_type": ablume_type, 'backdrop_path': backdrop_path, 'bludv_name': bludv_name,
                      'original_title': original_title, 'director': director, 'service_type': service_type,
                      'main_actor': main_actor, 'language': language, 'download_url': download_url,
                      'overview': overview, 'page_url': page_url, 'poster_path': poster_path,
                      'release_date': release_date, 'year': year, 'vote_average': vote_average}

            mycol = self.mydb["singletvtemp"]
            print(mydict)
            x = mycol.insert_one(mydict)
            print('获取到一条tv条目')
            global flag
            flag=1

        # except urllib.error.URLError as ex:
        except Exception as ex:
            print(self.murl + '页数获取失败（可能由于超时等原因）')

            print(ex)
        finally:
            mycol = self.mydb["tvrunning"]
            mycol.find_one_and_delete({"url": self.murl})



class tvdownloadurlThread (threading.Thread):
    myclient = dbsetting.myclient
    mydb = dbsetting.mydb
    situation = mydb["situation"].find_one()
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        mycol = self.mydb["singletvtemp"]
        mycol2 = self.mydb["singletvdownloadlist"]
        mycol3=self.mydb["singletvdownloadlqueue"]
        #mycol4 = self.mydb["catalogqueue"]

        x = mycol.find_one({})

        for downloadurl in x['download_url']:
            mycol2.insert({'page_url':x['page_url'],'name':downloadurl['name'],'url':downloadurl['url']})
            mycol3.insert({'page_url':x['page_url'],'name':downloadurl['name'],'url':downloadurl['url']})


        print('更新了一条下载链接的结果')



class tvdownload (threading.Thread):
    Rurl = 'https://zonatorrent.tv/letters/'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}
    myclient = dbsetting.myclient
    mydb = dbsetting.mydb

    def __init__(self, rpage,rname,rurl):
        threading.Thread.__init__(self)
        self.rpage = rpage
        self.rname = rname
        self.rurl = rurl


    def run(self):
        try:
            print(self.rurl)
            req = urllib.request.Request(url=self.rurl, headers=self.headers)

            response = urllib.request.urlopen(req).read()
            soup = BeautifulSoup(response, "html.parser")
            if soup.find("a", attrs={'class': 'Button STPb'}):
                realurl = soup.find("a", attrs={'class': 'Button STPb'})['href']
                language = soup.find("img", attrs={'alt': 'Idioma'}).find_parent().text.lstrip()
            else:
                realurl=''
                language=''

            mycol = self.mydb["singledownloadresult"]
            mydict = {'page_url': self.rpage,'name': self.rname,'url': realurl,'language':language}
            x = mycol.insert_one(mydict)
            print("爬取到一集tv下载链接")

        except Exception as ex:
            print(self.rurl + 'tv下载链接爬取失败')
            mycol = self.mydb["singletvdownloadlqueue"]
            mydict = {'page_url': self.rpage,'name': self.rname,'url':self.rurl}
            x = mycol.insert_one(mydict)
            print(ex)
        finally:
          mycol = self.mydb["singletvdownloadrunning"]
          mycol.find_one_and_delete({'url':self.rurl})

    def stop(self):
      self._stop_event.set()

    def stopped(self):
      return self._stop_event.is_set()


class tvfinnalThread (threading.Thread):
    myclient = dbsetting.myclient
    mydb = dbsetting.mydb
    situation = mydb["situation"].find_one()
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):


        print("汇总")
        mycol = self.mydb["singletvtemp"]

        mycol3=self.mydb["singledownloadresult"]
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
        global result
        result = self.mydb['singletvtemp'].find_one({})

        print('已获得所有tv的下载链接')






#
if(len(sys.argv)<1):
    sys.exit('请传入需要爬取的url')
print("开始爬取"+sys.argv[1])
print(sys.argv[1])
while True:
    thread2 = tvThread('https://zonatorrent.tv/the-flash-serie-tv-spanish-online-torrent')
    thread2.start()
    thread2.join()
    if(flag==1):
        break



thread2=tvdownloadurlThread()
thread2.start()
thread2.join()
threads=[]
while True:
    mycol=mydb["singletvdownloadlqueue"]
    x = mycol.find_one_and_delete({})
    mycol = mydb["singletvdownloadrunning"]
    if x:
        mycol.insert_one({'page_url':x['page_url'],'name':x['name'],'url':x['url']})
        thread = tvdownload(x['page_url'],x['name'],x['url'])
        thread.start()
        threads.append(thread)
    if mydb["singledownloadresult"].count()==mydb["singletvdownloadlist"].count():
        break



thread2=tvfinnalThread()
thread2.start()
thread2.join()

mycol = mydb["zonatorrent_movie_info"]
if dict:
    if(mycol.find_one({'page_url':result['page_url']})==None):
        mycol.insert(result)
    else:print("数据库中已有此tv")

#所得到的数据已在singletvtemp 中
print('end')




