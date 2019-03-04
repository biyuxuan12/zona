import dbsetting
import sys
import pipe
import fix
myclient=dbsetting.myclient
mydb=dbsetting.mydb

mycol = mydb["situation"]


x=mycol.find_one()
if(x['running']=='done'):
    print('新的开始')
    mycol.find_one_and_update({}, {
        "$set": {"running": 'running', 'stepone': 'running', 'steptwo': 'running', 'stepthree': 'running',
                 'stepfour': 'running', 'stepfive': 'running'}})


    #初始化需要爬取得字母页
    mycol = mydb["letterlist"]
    x = mycol.delete_many({})
    for i in range(26):
      letter=chr(i+ord('a'))
      mydict = {"letter":letter}
      x = mycol.insert_one(mydict)
    mydict = {"letter":'0-9'}
    x = mycol.insert_one(mydict)

    #初始化字母页队列
    mycol2=mydb["letterqueue"]
    x = mycol2.delete_many({})
    for x in mycol.find():
        x = mycol2.insert_one(x)
    mydb["letterresult"].delete_many({})
    #状态写入
    mycol = mydb["situation"]

else:
    print('继续')
print(mydb["situation"].find_one())


#
# #初始化二级页面url清单
#
thread = pipe.letterbreakThread()
thread.start()


mycol2=mydb["catalogqueue"]
x = mycol2.delete_many({})
mycol = mydb["cataloglsit"]
for x in mycol.find():
    x = mycol2.insert_one(x)

thread = pipe.moviequeueThread()
thread.start()

thread = pipe.tvqueueThread()
thread.start()


thread = pipe.moviefinnalThread()
thread.start()

thread = pipe.tvdownloadurlThread()
thread.start()

thread = fix.fixThread()
thread.start()

thread = pipe.tvfinnalThread()
thread.start()

