import dbsetting
import sys
myclient=dbsetting.myclient
mydb=dbsetting.mydb
#myclient.drop_database(mydb)

mycol = mydb["situation"]

x = mycol.find_one()

print('即将清空数据并完成初始化')

myclient.drop_database(mydb)


mydict = {"running": 'done', 'stepone': 'running', 'steptwo': 'running', 'stepthree': 'running',
                 'stepfour': 'running', 'stepfive': 'running'}
x = mycol.insert_one(mydict)

print('初始化完毕！')