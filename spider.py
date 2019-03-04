import dbsetting
import threading
import clawercommon
import _thread
import fix
from pynput.keyboard import Key,Listener
import sys

myclient=dbsetting.myclient
mydb=dbsetting.mydb



threads=[]
i=0
while True:
    try:
        situation = mydb["situation"].find_one()
        if(bool(situation['stepone']=='done') and bool(situation['steptwo']=='done') and bool(situation['stepthree']=='done') and bool(situation['stepfour']=='done') and bool(situation['stepfive']=='done')):
            break
        while True:
            if len(threading.enumerate()) < 20:
                break
        if(bool(mydb["letterqueue"].count()>0)  and  bool(situation['stepone']=='running' )):
            print('线程数：'+str(len(threading.enumerate()))+'')
            mycol=mydb["letterqueue"]
            x=mycol.find_one_and_delete({})
            mycol = mydb["letterrunning"]
            mycol.insert_one(x)
            thread = clawercommon.letterThread(x['letter'])
            thread.start()
            threads.append(thread)



        if (bool(mydb["catalogqueue"].count() > 0)  and  bool(situation['steptwo'] == 'running')):
            print('线程数：' + str(len(threading.enumerate())) + '')
            mycol=mydb["catalogqueue"]
            x = mycol.find_one_and_delete({})
            mycol = mydb["catalogrunning"]
            mycol.insert_one({'catalogurl':x['catalogurl']})
            thread = clawercommon.urlThread(x['catalogurl'])
            thread.start()
            threads.append(thread)


        if (bool(mydb["moviequeue"].count() > 0)  and  bool(situation['stepthree'] == 'running')):
            print('线程数：' + str(len(threading.enumerate())) + '')
            mycol=mydb["moviequeue"]
            x = mycol.find_one_and_delete({})
            mycol = mydb["movierunning"]
            mycol.insert_one({'url':x['url']})
            thread = clawercommon.movieThread(x['url'])
            thread.start()
            threads.append(thread)

        if (bool(mydb["tvqueue"].count() > 0)  and  bool(situation['stepfour'] == 'running')):
            print('线程数：' + str(len(threading.enumerate())) + '')
            mycol=mydb["tvqueue"]
            x = mycol.find_one_and_delete({})
            mycol = mydb["tvrunning"]
            mycol.insert_one({'url':x['url']})
            thread = clawercommon.tvThread(x['url'])
            thread.start()
            threads.append(thread)


        if (bool(mydb["tvdownloadlqueue"].count() > 0)  and  bool(situation['stepfive'] == 'running')):
            print('线程数：' + str(len(threading.enumerate())) + '')
            mycol=mydb["tvdownloadlqueue"]
            x = mycol.find_one_and_delete({})
            mycol = mydb["tvdownloadrunning"]

            mycol.insert_one({'page_url':x['page_url'],'name':x['name'],'url':x['url']})
            thread = clawercommon.tvdownload(x['page_url'],x['name'],x['url'])
            thread.start()
            threads.append(thread)

        thread2 = fix.threadskill(threads)
        thread2.start()
    except Exception as ex:
        print(ex)




    i=i+1


