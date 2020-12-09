from pymongo import MongoClient

# 몽고db에 연결

client = MongoClient('mongodb://coderkang:123123@15.165.240.205', 27017)

# db name == anabada

db = client.anabada


"""
(Doc -> Collection)
user -> Users
"""