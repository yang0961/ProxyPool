import datetime
import random
import re
import threading
import time
import faker
from requests import get
import pandas as pd


class GetProxyIP(object):
    global_headers = {
        'user-agent': faker.Factory().create().user_agent(),
    }

    def __init__(self, ip_list: dict, proxy=None):
        self.ip_list = ip_list
        self.useful_ip_list = None
        self.proxy = proxy
        suc_proxy = []
        proxy_ip = []
        if proxy is not None:
            for ele in proxy[:50]:
                proxy_ip.append({'ip': ele.split(':')[0], 'port': ele.split(':')[1]})
            self.batch_verify_ip(proxy_ip, suc_proxy)
            self.proxy = suc_proxy
            if len(suc_proxy) < 10: self.proxy = None

    def get_66ip_proxy_ip(self, number: int = 1, proxy_type: int = 0, proxy_area: int = 1, proxy=None) -> list:
        """http://www.66ip.cn/nmtq.php?   最多一次提取300个"""
        assert number <= 300, '最多一次获取300个ip'
        assert proxy is None or isinstance(proxy, dict), "proxy必须是一个字典"
        ip_url = 'http://www.66ip.cn/nmtq.php?'
        headers = self.global_headers.copy()
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

    def get_89ip_proxy_ip(self, number, proxy=None):
        """https://www.89ip.cn/  最多一次提取999个"""
        assert number <= 999, '最多一次获取999个ip'
        assert proxy is None or isinstance(proxy, dict), "proxy必须是一个字典"
        ip_url = 'https://www.89ip.cn/tqdl.html?'
        headers = self.global_headers.copy()
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

    def batch_verify_ip(self, batch_verify_ip: list, batch_verify_success_ip_list: list):

        def verify_ip(ver_ip, ver_suc_list):
            proxy = {"http": f"http//{ver_ip['ip']}:{ver_ip['port']}"}
            try:
                res = get('https://www.baidu.com', headers=self.global_headers, proxies=proxy, timeout=2).text
                ver_suc_list.append(ver_ip['ip'] + ':' + ver_ip['port'])
                return ver_ip
            except Exception:
                return None

        thread = []
        for element in batch_verify_ip:
            if element == '' or element['ip'] == '' or element['port'] == '':
                continue
            th = threading.Thread(target=verify_ip, args=(element, batch_verify_success_ip_list))
            thread.append(th)
            th.start()
        for th_ele in thread:
            th_ele.join()

    def run(self, file):
        file.write(
            f'---------------------------------------------------------------' +
            f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}----------' +
            f'-----------------------------------------------------\n')
        # 如果ip池里有ip首先用ip池里数据
        # 国内http代理ip
        if self.proxy is not None:
            random.shuffle(self.proxy)
            request_proxy = {'ip': self.proxy[0].split(':')[0], "port": self.proxy[0].split(':')[1]}
            proxy = {'http': f"http://{request_proxy['ip']}:{request_proxy['port']}"}
            file.write('INFO-----国内http----https://www.89ip.cn/正在获取代理ip中----有代理\n')
            response_ip = self.get_89ip_proxy_ip(700, proxy=proxy)
            self.batch_verify_ip(response_ip, proxy_ip_to_csv['domestic_http'])
            get89_success_ip_length = len(proxy_ip_to_csv['domestic_http'])
            file.write(f'INFO-----获取到代理ip--->{len(response_ip)}<---' +
                       f'可用ip--->{get89_success_ip_length}<---\n')

            proxy = {'https': f"https://{proxy_ip_to_csv['domestic_http'][0]}"}
            file.write('INFO-----国内http----http://www.66ip.cn/正在获取代理ip中\n')
            try:
                response_ip = self.get_66ip_proxy_ip(300, proxy=proxy)
            except:
                proxy = {'http': f"http://{proxy_ip_to_csv['domestic_http'][0]}"}
                response_ip = self.get_66ip_proxy_ip(300, proxy=proxy)
            self.batch_verify_ip(response_ip, proxy_ip_to_csv['domestic_http'])
            get66_success_ip_length = len(proxy_ip_to_csv['domestic_http']) - get89_success_ip_length
            file.write(f'INFO-----获取到代理ip--->{len(response_ip)}<---' +
                       f'可用ip--->{get66_success_ip_length}<---\n')
        else:
            file.write('INFO-----国内http----https://www.89ip.cn/正在获取代理ip中----无代理\n')
            response_ip = self.get_89ip_proxy_ip(700)
            self.batch_verify_ip(response_ip, proxy_ip_to_csv['domestic_http'])
            get89_success_ip_length = len(proxy_ip_to_csv['domestic_http'])
            file.write(f'INFO-----获取到代理ip--->{len(response_ip)}<---' +
                       f'可用ip--->{get89_success_ip_length}<---\n')

            proxy = {'https': f"https://{proxy_ip_to_csv['domestic_http'][0]}"}
            file.write('INFO-----国内http----http://www.66ip.cn/正在获取代理ip中\n')
            try:
                response_ip = self.get_66ip_proxy_ip(300, proxy=proxy)
            except:
                proxy = {'http': f"http://{proxy_ip_to_csv['domestic_http'][0]}"}
                response_ip = self.get_66ip_proxy_ip(300, proxy=proxy)
            self.batch_verify_ip(response_ip, proxy_ip_to_csv['domestic_http'])
            get66_success_ip_length = len(proxy_ip_to_csv['domestic_http']) - get89_success_ip_length
            file.write(f'INFO-----获取到代理ip--->{len(response_ip)}<---' +
                       f'可用ip--->{get66_success_ip_length}<---\n')

        # 国外http
        request_proxy = {'ip': proxy_ip_to_csv['domestic_http'][1].split(':')[0],
                         "port": proxy_ip_to_csv['domestic_http'][1].split(':')[1]}
        proxy = {'https': f"https://{request_proxy['ip']}:{request_proxy['port']}"}
        file.write('INFO-----国外http----http://www.66ip.cn/正在获取代理ip中\n')
        try:
            response_ip = self.get_66ip_proxy_ip(300, proxy=proxy, proxy_area=2)
        except:
            proxy = {'http': f"http://{request_proxy['ip']}:{request_proxy['port']}"}
            response_ip = self.get_66ip_proxy_ip(300, proxy=proxy, proxy_area=2)
        self.batch_verify_ip(response_ip, proxy_ip_to_csv['abroad_http'])
        get66_success_ip_length = len(proxy_ip_to_csv['abroad_http'])
        file.write(f'INFO-----国内http----http://www.66ip.cn/获取到代理ip-{len(response_ip)}--' +
                   f'可用ip-{get66_success_ip_length}\n')
        file.write('INFO-----本次代理ip获取完毕\n')


fp = open('use.log', mode='a+', encoding='utf-8')
proxy_ip_to_csv = {
    'number': [],
    'domestic_http': [],
    'domestic_https': [],
    'abroad_http': [],
    'abroad_https': [],
}
try:
    proxy_ip_file = pd.read_csv('save_proxy_ip.csv')
    csv_domestic_http = proxy_ip_file['domestic_http'].dropna().tolist()
    if len(csv_domestic_http) > 20:
        ip = GetProxyIP(ip_list=proxy_ip_to_csv, proxy=csv_domestic_http)
    else:
        ip = GetProxyIP(ip_list=proxy_ip_to_csv)
except:
    ip = GetProxyIP(ip_list=proxy_ip_to_csv)
try:
    ip.run(fp)
except Exception as e:
    fp.write(f'ERROR----- 运行失败{e}\n')
    fp.close()
proxy_ip_to_csv = pd.concat([
                             pd.DataFrame({'number': list(range(1, len(proxy_ip_to_csv['domestic_http']) + 1))}),
                             pd.DataFrame({'domestic_http': proxy_ip_to_csv['domestic_http']}),
                             # pd.DataFrame({'domestic_https': proxy_ip_to_csv['domestic_https']}),
                             pd.DataFrame({'abroad_http': proxy_ip_to_csv['abroad_http']}),
                             # pd.DataFrame({'abroad_https': proxy_ip_to_csv['abroad_https']})
                             ], axis=1)
proxy_ip_to_csv.to_csv('save_proxy_ip.csv', index=False)
