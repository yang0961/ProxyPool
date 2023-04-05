# coding: utf-8
# @Author: 小杨大帅哥
import time

import faker
from requests import get
import re

global_headers = {
    'user-agent': faker.Factory().create().user_agent(),
}

def get_89ip_proxy_ip(number, proxy=None):
    """https://www.89ip.cn/  最多一次提取999个"""
    assert number <= 999, '最多一次获取999个ip'
    assert proxy is None or isinstance(proxy, dict), "proxy必须是一个字典"
    ip_url = 'https://www.89ip.cn/tqdl.html?'
    headers = global_headers.copy()
    headers['cookie'] = f"https_waf_cookie=b233809a-92e9-4d394d686618d0c25fb78b1e4fc4eec74f86; " \
                        f"Hm_lvt_f9e56acddd5155c92b9b5499ff966848=1680577470; Hm_lpvt_f9e56acddd5155c92b9b5" \
                        f"499ff966848={int(time.time())} "
    headers['Referer'] = 'https://www.89ip.cn/ti.html'
    params = {'num': number, 'address': '', 'kill_address': '', 'port': '', 'kill_port': '', 'isp': '', }
    proxy_ip_list = []
    proxy_ip_key = ['ip', 'port']
    if proxy is None:
        response = get(url=ip_url, headers=headers, params=params).text
    else:
        response = get(url=ip_url, headers=headers, params=params, proxies=proxy, timeout=8).text
    result = re.findall('(?:<!DOCTYPE html>.*?<div style="padding-left:20px;">\s+)?(.*?):(.*?)<br>', response, re.S)
    for ele in result:
        proxy_ip_list.append(dict(zip(proxy_ip_key, ele)))
    return proxy_ip_list


print(get_89ip_proxy_ip(10, proxy={'ip': '27.158.127.206', 'port': '8089'}))
