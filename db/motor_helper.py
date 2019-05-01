# encoding: utf-8
'''
@author: He
@file: motor.py
@time: 2019/4/22/0022 下午 03:56
mogoDB的异步存储
'''
import asyncio
from DoubanMovie.logger.log import storage
from motor.motor_asyncio import AsyncIOMotorClient
from bson import SON
import pprint

try:
    import uvloop

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    pass
# 数据库基本信息
db_configs = {
    'type': 'mongo',
    'host': '127.0.0.1',
    'port': '27017',
    "user": "",
    "password": "",
    'db_name': 'DoubanMovie'
}


class MotorBase():
    def __init__(self):
        self.__dict__.update(**db_configs)
        if self.user:
            self.motor_uri = f"mongodb://{self.user}:{self.passwd}@{self.host}:{self.port}/{self.db_name}?authSource={self.user}"
        self.motor_uri = f"mongodb://{self.host}:{self.port}/{self.db_name}"
        self.client = AsyncIOMotorClient(self.motor_uri)
        self.db = self.client.DoubanMovie

    async def save_data(self, item):
        try:
            await self.db.infoq_details.update_one({
                'id': item.get("id")},
                {'$set': item},
                upsert=True)
        except Exception as e:
            storage.error(f"数据插入出错:{e.args}此时的item是:{item}")

    async def change_status(self, id, status_code=0):
        # status_code 0:初始,1:开始下载，2下载完了
        # storage.info(f"修改状态,此时的数据是:{item}")
        item = {}
        item["status"] = status_code
        await self.db.movie.update_one({'id': id}, {'$set': item}, upsert=True)

    async def reset_status(self):
        await self.db.movie.update_many({'status': 1}, {'$set': {"status": 0}})

    async def reset_all_status(self):
        await self.db.movie.update_many({}, {'$set': {"status": 0}})

    async def get_detail_datas(self):
        data = self.db.movie.find({'status': 1})

        async for item in data:
            print(item)
        return data

    async def find(self):
        data = self.db.movie.find({'status': 0})
        async_gen = (item async for item in data)
        return async_gen

    async def use_count_command(self):
        response = await self.db.command(SON([("count", "movie")]))
        print(f'response:{pprint.pformat(response)}')


if __name__ == '__main__':
    m = MotorBase()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(m.find())
