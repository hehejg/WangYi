# encoding: utf-8
'''
@author: He
@file: SpiderMusic.py
@time: 2019/5/1/0001 下午 03:18
网易云音乐评论爬取
'''
import requests
import execjs
from WangYImusic .db .mongo_helper import Mongo
from WangYImusic.logger.log import crawler

class SpiderMusic:
    def __init__(self):
        self.id=0
        self.url = 'https://music.163.com/weapi/v1/resource/comments/R_SO_4_1360829941?csrf_token='
        self.headers = {
            "Content-Length": "476",
            "Accept": "*/*",
            "Referer": "https://music.163.com/song?id=1360627776",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0",
            "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "Cookie": "JSESSIONID-WYYY=5xeB%2BIXBC2V%5CVlaP7TOSe08MMw%2Fl%5CMU2n6D5ShK6%2FezfCpOug15pUYMoNm6ZJgCB4pryiarBhTdRpwRjSMavH%5CrQqeK5SYF3AV9c1PD3tHbnp3y%2B36ob0lH7BM61Xa8%2BRabI9rG5uaKyRPw5ZnSbXDJgtC7BhhtSrfQMc59OX0aKE%2Bts%3A1556628197007; _iuqxldmzr_=32; _ntes_nnid=e9b4ed8d79454bd61d5e398a9f956679,1556626397036; _ntes_nuid=e9b4ed8d79454bd61d5e398a9f956679; WM_NI=2TDGmHi%2Bm8CTqr16NSlzikGrsyobYmu1KmP%2B34AyO5TAXnWDYR%2BoVPh8AJK%2BPr2I8pwOrIVkl7qD7CYPf6%2BbqyaY56rhbhVHQBlJIvsogj0ngyOIVFNqnqjEO%2BtCKmOBTjQ%3D; WM_NIKE=9ca17ae2e6ffcda170e2e6eea8dc6af2988da6ae469ca88fa7d54a879e8a84ee7381edc0b5e745f7e8f9a2cd2af0fea7c3b92af28c8ca8f044abf5a3d9c260b3aeffd7cd59b0a6a78cc67ab1a7a183dc67b7ef858ed321f1ec8f9ace3f989f988fd6509b8ee590d55cace88fabca2194aefeaabb7cb591beaad561b0e9bfa5b6499b90aad7aa6ab3a7afbab83eb2b8ae89d544939ea4abcc7eb1b1a98bb366a5a781aad54e8eafa292e94f8df5bca4ca678d9e9c8bd437e2a3; WM_TID=esv55lB7vSZFQEEAUFMpzCnoWca4o%2FFN; abt=85",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Host": "music.163.com",
        }
        self.Session = requests.session()
        self.Session.headers.update(self.headers)
        # 网易云音乐的js加密参数
        self.f = "00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7"
        self.g = '0CoJUm6Qyw8W8jud'
        self.e = "010001"

    def get_js(self, d):
        f = open("Yun.js", 'r', encoding='utf-8')  # 打开JS文件
        line = f.readline()
        htmlstr = ''
        while line:
            htmlstr = htmlstr + line
            line = f.readline()
        jsstr = htmlstr
        ctx = execjs.compile(jsstr)
        return (ctx.call('d', d, self.e, self.f, self.g))

    def req(self, d):
        data = self.get_js(d)
        data.update(params=data.pop('encText'))
        result = self.Session.post(url=self.url, data=data)
        if result.status_code in [200, 201]:
            return result.json()
    def save_data(self,req,):
        task = []
        datas = req['comments']
        for data in datas:
            dic = {}
            dic['id']=self.id
            dic['userId'] = data['user']['userId']
            dic['nickname'] = data['user']['nickname']
            dic['avatarUrl'] = data['user']['avatarUrl']
            dic['content'] = data['content']
            dic['time'] = data['time']
            task.append(dic)
            self.id+=1
        Mongo().save_data(task)
        crawler.info(f'添加了{len(task)}个到数据库中')
    def run(self):
        i = 0
        offset=0
        while i < 3:
            d = {"rid": "R_SO_4_1360829941",#后面的数字id为音乐id同url的id
                 "offset": offset,
                 "total": "false",
                 "limit": "20", "csrf_token": ""
                 }
            req=self.req(str(d))
            self.save_data(req)
            i+=1
            offset+=20
if __name__ == '__main__':
    sipder_music=SpiderMusic()
    sipder_music.run()