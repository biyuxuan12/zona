import pymongo
import sys

import dbsetting
#
# myclient=dbsetting.myclient
# mydb=dbsetting.mydb
# mycol= mydb["sutiation"]
# myquery = { "running": "done" }
# mydoc = mycol.find(myquery)
# x=mycol.find_one()
#
#
#
# print( mydoc)
# print( type(mydoc))
# print( mydoc[0])
# print( x)
# print( type(x))
# print(x['running'])
import dbsetting
import sys
myclient=dbsetting.myclient
mydb=dbsetting.mydb

mycol = mydb["situation"]
x = mycol.delete_many({})
mydict = {"running": 'done', 'stepone': 'done', 'steptwo': 'done', 'stepthree': 'done'}
x = mycol.insert_one(mydict)