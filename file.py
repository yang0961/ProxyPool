# coding: utf-8
# @Author: 小杨大帅哥
import time

import faker
from requests import get
import re

global_headers = {
    'user-agent': faker.Factory().create().user_agent(),
}


def get_66ip_proxy_ip(number: int = 1, proxy_type: int = 0, proxy_area: int = 1, proxy=None) -> list:
    """http://www.66ip.cn/nmtq.php?   最多一次提取300个"""
    assert number <= 300, '最多一次获取300个ip'
    assert proxy is None or isinstance(proxy, dict), "proxy必须是一个字典"
    ip_url = 'http://www.66ip.cn/nmtq.php?'
    headers = global_headers.copy()
    headers['cookie'] = f"Hm_lvt_1761fabf3c988e7f04bec51acd4073f4=1680425293,1680576974; " \
                        f"Hm_lpvt_1761fabf3c988e7f04bec51acd4073f4={int(time.time())} "
    proxy_ip_list = []
    proxy_ip_key = ['ip', 'port']
    params = {
        "getnum": number,  # 数量
        "isp": 0,  # 运营商选择
        "anonymoustype": 3,  # 匿名程度
        "start": '',  # 指定IP段
        "ports": '',  # 指定端口
        "export": '',  # 排除端口
        "ipaddress": '',  # 指定地区
        "area": proxy_area,  # 过滤条件 0--国内外 1--国内  2--国外
        "proxytype": proxy_type,  # 选择代理类型 0--http  1--https  3--全部
        "api": "66ip",
    }
    if proxy is None:
        response = get(url=ip_url, headers=headers, params=params, timeout=8)
    else:
        response = get(url=ip_url, headers=headers, params=params, proxies=proxy, timeout=8)
    response.encoding = 'GBK'
    result_list = re.findall('\s+(.*?):(.*?)<br />', response.text)
    for i in range(len(result_list)):
        proxy_ip_list.append(dict(zip(proxy_ip_key, result_list[i])))
    return proxy_ip_list


print(get_66ip_proxy_ip(10))
