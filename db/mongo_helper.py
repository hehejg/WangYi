# encoding: utf-8
'''
@author: He
@file: mongo.py
@time: 2019/4/22/0022 下午 03:44
'''
import pymongo
from ..logger.log import storage

from .import Config
# 数据库基本信息
db_configs = {
    'type': 'mongo',
    'host': '127.0.0.1',
    'port': '27017',
    "user": "",
    "password": "",
    'db_name':Config.DBNAME
}


class Mongo():
    def __init__(self):
        self.db_name = db_configs.get("db_name")
        self.host = db_configs.get("host")
        self.port = db_configs.get("port")
        self.client = pymongo.MongoClient(f'mongodb://{self.host}:{self.port}')
        self.username = db_configs.get("user")
        self.password = db_configs.get("passwd")
        if self.username and self.password:
            self.db = self.client[self.db_name].authenticate(self.username, self.password)
        self.db = self.client[self.db_name]

    def find_data(self, col=Config.TABLENAME):
        # 获取状态为0的数据
        data = self.db[col].find({"status": 0}, {"_id": 0})
        gen = (item for item in data)
        return gen

    def change_status(self, id, item, col=Config.TABLENAME, status_code=0):
        # status_code 0:初始,1:开始下载，2下载完了
        item["status"] = status_code
        self.db[col].update_one({'id': id}, {'$set': item})

    def save_data(self, items, col=Config.TABLENAME):
        if isinstance(items, list):
            for item in items:
                try:
                    self.db[col].update_one({
                        'id': item.get("id")},
                        {'$set': item},
                        upsert=True)
                except Exception as e:
                    storage.error(f"数据插入出错:{e.args},此时的item是:{item}")
        else:
            try:
                self.db[col].update_one({
                    'id': items.get("id")},
                    {'$set': items},
                    upsert=True)
            except Exception as e:
                storage.error(f"数据插入出错:{e.args},此时的item是:{item}")


if __name__ == '__main__':
    m = Mongo()
    m.find_data()
