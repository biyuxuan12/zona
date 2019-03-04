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

class fixThread (threading.Thread):
    myclient = dbsetting.myclient
    mydb = dbsetting.mydb

    mycol = mydb["situation"]
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        while True:
            time.sleep(5)

            if bool(self.mycol.find_one({})['stepone']=='done') and  bool(bool(self.mydb["letterrunning"].count()>0 )or bool(self.mydb["letterqueue"].count()>0)):
                if(self.mydb["letterqueue"].count()==0):
                    x= self.mydb['letterrunning'].find({})
                    mycol = self.mydb['letterqueue']
                    for url in x:
                        mycol.insert(x)
                self.mydb["situation"].find_one_and_update({}, {'$set': {'stepone': 'running'}})

            if bool(self.mycol.find_one({})['steptwo']=='done') and  bool(bool(self.mydb["catalogrunning"].count()>0) or bool(self.mydb["catalogqueue"].count()>0)):
                if(self.mydb["catalogqueue"].count()==0):
                    x= self.mydb['catalogrunning'].find({})
                    mycol = self.mydb['catalogqueue']
                    for url in x:
                        mycol.insert(x)
                self.mydb["situation"].find_one_and_update({}, {'$set': {'steptwo': 'running'}})

            if bool(self.mycol.find_one({})['stepthree'] == 'done' ) and  bool(bool(self.mydb["movierunning"].count() > 0 )or bool( self.mydb["moviequeue"].count()>0)):
                if (self.mydb["moviequeue"].count() == 0):
                    x = self.mydb['movierunning'].find({})
                    mycol = self.mydb['moviequeue']
                    for url in x:
                        mycol.insert(x)
                self.mydb["situation"].find_one_and_update({}, {'$set': {'stepthree': 'running'}})

            if bool(self.mycol.find_one({})['stepfour'] == 'done')  and  bool(bool(self.mydb["tvrunning"].count() > 0) or bool( self.mydb["tvqueue"].count()>0)):

                if (self.mydb["tvqueue"].count() == 0):
                    x = self.mydb['tvrunning'].find({})
                    mycol = self.mydb['tvqueue']
                    for url in x:
                        mycol.insert(x)

                self.mydb["situation"].find_one_and_update({}, {'$set': {'stepfour': 'running'}})



            if bool(self.mycol.find_one({})['stepfive'] == 'done' ) and  bool(bool(self.mydb["tvdownloadrunning"].count() >0 )| bool(self.mydb["tvdownloadlqueue"].count()>0)) :
                if (self.mydb["tvdownloadlqueue"].count() == 0):
                    x = self.mydb['tvdownloadrunning'].find({})
                    mycol = self.mydb['tvdownloadlqueue']
                    for url in x:
                            mycol.insert(x)
                self.mydb["situation"].find_one_and_update({}, {'$set': {'stepfive': 'running'}})

class threadskill (threading.Thread):
    myclient = dbsetting.myclient
    mydb = dbsetting.mydb
    def __init__(self,li=[]):
        threading.Thread.__init__(self)
        self.threads=li
    def run(self):
       for t in self.threads:
           t.join()

       # for t in self.threads:
       #     t.join()

