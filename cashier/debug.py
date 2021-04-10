#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
import json

def checkout():
    url = 'http://localhost:8080/cashier/checkout_byvip/'
    body = {
        "company": "dsdemo",
        "storecode": "88",
        "cashier": "admin",
        'vipuuid':'e76a1c3c7b3311eb88f900163e0324aa'
        }

    headers = {'content-type': "application/json", 'Authorization': 'APP appid = 4abf1a,token = 9480295ab2e2eddb8'}
    #print type(body)
    #print type(json.dumps(body))
    # 这里有个细节，如果body需要json形式的话，需要做处理
    # 可以是data = json.dumps(body)
    # response = requests.post(url, data = json.dumps(body), headers = headers)
    # 也可以直接将data字段换成json字段，2.4.3版本之后支持
    # response  = requests.post(url, json = body, headers = headers)
    url = 'http://localhost:8080/cashier/checkout_byvip/?company=dsdemo&storecode=88&cashier=admin&vipuuid=e76a1c3c7b3311eb88f900163e0324aa'
    response = requests.get(url)
    # 返回信息
    print(response.text)
    # 返回响应头
    print(response.status_code)
    return 0

checkout()