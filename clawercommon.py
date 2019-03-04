import time
import sys

import dbsetting
import re
import socket
timeout = 100
socket.setdefaulttimeout(timeout)
import threading
import urllib
from urllib import request
from bs4 import BeautifulSoup
import pymongo
import datetime as dt


# 此类中的每一个方法都是一个下载器
# 以获得27个字母每个字母有几页为例
# spider将 letterqueue 中的字母喂给 letterThread
# letterThread 拿到字母等于拿到对应的url
# letterThread用该url 发起request
# 将获得的response 解析 并放入letterlist 中
# 如果期间发生超时等异常 如果成功捕捉到 字母会重新放进 letterqueue队列
#
# 正在发送request的letterThread 会将它手中的字母（也就是url）放进letterrunning队列中 以防异常退出导致 fix函数会将异常退出导致而停留在letterrunning中的字母放回letterqueue



class letterThread (threading.Thread):
  Rurl = 'https://zonatorrent.tv/letters/'
  headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}
  myclient = dbsetting.myclient
  mydb = dbsetting.mydb

  def __init__(self, r1):
    threading.Thread.__init__(self)
    self.r1 = r1

  def run(self):
    try:
      print('开始获取'+self.r1+'页数')
      req = urllib.request.Request(url=self.Rurl + self.r1, headers=self.headers)
      response = urllib.request.urlopen(req).read()
      soup = BeautifulSoup(response, "html.parser")
      pagenum = soup.find("span", attrs={'class': 'pages'})
      print(self.r1+'页面获取成功')
      pattern = re.compile(r'\d+')
      m = pattern.search(pagenum.string, 9)

      mycol = self.mydb["letterresult"]
      mydict = {"letter": self.r1,"page":m.group(0)}
      x = mycol.insert_one(mydict)
      print('字母'+self.r1+'的页数为'+m.group(0))
      if(self.mydb["letterresult"].count()==self.mydb["letterlist"].count()):
          self.mydb["situation"].find_one_and_update({}, {'$set': {'stepone': 'done'}})
          print("字母页面数爬取完毕")

    except (Exception,SystemExit) as ex:
      print(self.r1+'页数获取失败（可能由于超时等原因）')
      mycol = self.mydb["letterqueue"]
      mydict = {"letter":self.r1 }
      x=mycol.insert_one(mydict)
      print(ex)
    finally:
      mycol = self.mydb["letterrunning"]
      mycol.find_one_and_delete({'letter':self.r1})

  def stop(self):
    self._stop_event.set()

  def stopped(self):
    return self._stop_event.is_set()

class urlThread (threading.Thread):
    Rurl = 'https://zonatorrent.tv/letters/'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}
    myclient = dbsetting.myclient
    mydb = dbsetting.mydb

    def __init__(self, r2):
        threading.Thread.__init__(self)
        self.r2 = r2

    def run(self):
        try:
            print(self.Rurl+self.r2)
            req = urllib.request.Request(url=self.Rurl+self.r2, headers=self.headers)

            response = urllib.request.urlopen(req).read()
            soup = BeautifulSoup(response, "html.parser")
            tbody = soup.table.tbody
            print(self.r2 + '页面获取成功')
            for tr in tbody:
                # print(tr)
                mycol = self.mydb["movieurl"]
                mydict = {"url": tr.a['href'] }
                if tr.find("span", attrs={'class': 'TpTv BgA'}):
                    mycol = self.mydb["tvurl"]
                x = mycol.insert_one(mydict)
                if (bool(self.mydb["catalogqueue"].count()==0 )and  bool(self.mydb["catalogrunning"].count()==0)):
                  self.mydb["situation"].find_one_and_update({}, {'$set': {'steptwo': 'done'}})
                  print("url页面数爬取完毕")
        except Exception as ex:
            print(self.r2 + '页面获取失败')
            mycol = self.mydb["catalogqueue"]
            mydict = {"catalogurl": self.r2}
            x = mycol.insert_one(mydict)
            print(ex)
        finally:
          mycol = self.mydb["catalogrunning"]
          mycol.find_one_and_delete({"catalogurl": self.r2})

    def stop(self):
      self._stop_event.set()

    def stopped(self):
      return self._stop_event.is_set()


class movieThread (threading.Thread):
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
            mycol = self.mydb["movieitem"]

            mydict = {"ablume_type":ablume_type,'backdrop_path':backdrop_path,'bludv_name':bludv_name,'original_title':original_title,'director':director,'service_type':service_type,
                      'main_actor':main_actor,'language':language,'download_url':download_url,'overview':overview,'page_url':page_url,'poster_path':poster_path,'release_date':release_date,'year':year,'vote_average':vote_average}
            print(mydict)
            x = mycol.insert_one(mydict)
            if (bool(self.mydb["moviequeue"].count() == 0 ) and  bool(self.mydb["movierunning"].count() == 0)):
                self.mydb["situation"].find_one_and_update({}, {'$set': {'stepthree': 'done'}})
                print("movie页面爬取完毕")
        except Exception as ex:
            print(self.murl + '页数获取失败（可能由于超时等原因）')
            mycol = self.mydb["moviequeue"]
            mydict = {"url": self.murl}
            x = mycol.insert_one(mydict)
            print(ex)
        finally:
            mycol = self.mydb["movierunning"]
            mycol.find_one_and_delete({"url": self.murl})

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()


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

            mycol = self.mydb["tvitem"]
            print(mydict)
            x = mycol.insert_one(mydict)
            mycol2=self.mydb["tvtemp"]
            x = mycol2.insert_one(mydict)
            print('获取到一条tv条目')
            if (bool(self.mydb["tvqueue"].count() == 0)  and bool( self.mydb["tvrunning"].count() == 0)):
                self.mydb["situation"].find_one_and_update({}, {'$set': {'stepfour': 'done'}})
                print("tvitem爬取完毕")

        # except urllib.error.URLError as ex:
        except Exception as ex:
            print(self.murl + '页数获取失败（可能由于超时等原因）')
            mycol = self.mydb["tvqueue"]
            mydict = {"url": self.murl}
            x = mycol.insert_one(mydict)
            print(ex)
        finally:
            mycol = self.mydb["tvrunning"]
            mycol.find_one_and_delete({"url": self.murl})


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

            mycol = self.mydb["downloadresult"]
            mydict = {'page_url': self.rpage,'name': self.rname,'url': realurl,'language':language}
            x = mycol.insert_one(mydict)
            print("爬取到一集tv下载链接")
            if (bool(self.mydb["tvdownloadlqueue"].count()==0 )and  bool(self.mydb["tvdownloadrunning"].count()==0)):
                self.mydb["situation"].find_one_and_update({}, {'$set': {'stepfive': 'done'}})
                print("爬取tv下载链接爬取完毕")
        except Exception as ex:
            print(self.rurl + 'tv下载链接爬取失败')
            mycol = self.mydb["tvdownloadlqueue"]
            mydict = {'page_url': self.rpage,'name': self.rname,'url':self.rurl}
            x = mycol.insert_one(mydict)
            print(ex)
        finally:
          mycol = self.mydb["tvdownloadrunning"]
          mycol.find_one_and_delete({'url':self.rurl})

    def stop(self):
      self._stop_event.set()

    def stopped(self):
      return self._stop_event.is_set()
