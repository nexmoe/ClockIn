import requests
import json
from hashlib import md5
from urllib import parse
import time
import urllib3
import sys
urllib3.disable_warnings()


# --------------------------------------------------------------------------
phone = sys.argv[1]
pwd = sys.argv[2]
address = sys.argv[3]
lat = sys.argv[4]
lng = sys.argv[5]
district = sys.argv[6]
deviceToken = sys.argv[7]
sckey = sys.argv[8]
# ---------------------------------------------------------------------------
session = requests.Session()
now = time.time()+28800
date = time.strftime("%m月%d日",time.localtime(now))


# Wxpush()消息推送模块
def Wxpush(msg):
    url = f'https://sc.ftqq.com/{sckey}.send?text={date}{msg}'
    for _ in range(3):
        err = requests.get(url)
        if not err.json()['errno']:
            break


# 指点天下登录模块
def login():
    url = 'http://app.zhidiantianxia.cn/api/Login/pwd'
    encoded_pwd = md5('axy_{}'.format(pwd).encode()).hexdigest()
    global flag
    header = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Content-Length': '201',
        'Host': 'app.zhidiantianxia.cn',
        'Connection': 'Keep-Alive',
        'Accept-Encoding': 'gzip',
        'User-Agent': 'okhttp/3.10.0'
    }
    data = {
        'phone': phone,
        'password': encoded_pwd,
        'mobileSystem': '10',
        'appVersion': '1.6.4',
        'mobileVersion': 'Mate30',
        'deviceToken': deviceToken,
        'pushToken': '0938765546475757478765800CN01',
        'romInfo': 'hw'
    }

    response = session.post(url=url, headers=header, data=data)
    if response.json()['status'] == 1:
        print('登录成功')
        flag = 1
    else:
        print(response.json()['msg'])
        msg = parse.quote_plus(response.json()['msg'])
        Wxpush(msg)
        flag = 0
    return response.json()['data']


# 获取每日宿舍签到的signInId模块
def get_signInId(token):
    url = 'http://zua.zhidiantianxia.cn/applets/signin/my'
    header = {
        'axy-phone': phone,
        'axy-token': token,
        'user-agent': 'TAS-AN00(Android/5.1.1) (com.axy.zhidian/1.5.5) Weex/0.18.0 720x1280',
        'Host': 'zua.zhidiantianxia.cn',
        'Connection': 'Keep-Alive',
        'Accept-Encoding': 'gzip'
    }
    data = {
        'page': '0',
        'size': '10'
    }
    try:
        signInId = session.get(url=url, headers=header, data=data).json()['data']['content'][0]['id']
        return signInId
    except:
        pass


# 22点宿舍签到模块
def sign_in_evening(token):
    url = 'http://zua.zhidiantianxia.cn/applets/signin/sign'
    header = {
        'axy-phone': phone,
        'axy-token': token,
        'Content-Type': 'application/json',
        'user-agent': 'TAS-AN00(Android/5.1.1) (com.axy.zhidian/1.5.5) Weex/0.18.0 720x1280',
        'Host': 'zua.zhidiantianxia.cn',
        'Connection': 'Keep-Alive',
        'Accept-Encoding': 'gzip',
        'Content-Length': '146'
    }
    data = {
        "locale": address,
        "lat": lat,
        "lng": lng,
        "signInId": get_signInId(token)
    }
    data = json.dumps(data)
    response = session.post(url=url, headers=header, data=data)
    if response.json()['status'] == 1:
        print("签到成功")
    else:
        print("签到失败")
    msg = parse.quote_plus(response.json()['msg'])
    Wxpush(msg)


if __name__ == "__main__":
    token = login()
    time.sleep(3)
    now_H = int(time.strftime("%H"))
    if flag:
        if 13 <= now_H <= 14: # 世界协调时间
            sign_in_evening(token)
        else:
            sign_in(token)
    else:
        pass
