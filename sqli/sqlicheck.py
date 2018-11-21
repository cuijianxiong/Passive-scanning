# -*- coding: utf-8 -*-


import requests
from xml.dom import minidom
from urllib.parse import urlparse
import copy
import urllib
import time
import re
import os
import random
from sqlconf.config import BOUNDED_INJECTION_MARKER
from sqlconf.config import DEFAULT_RADIO
from sqlihelper import getPagesRatio, getFlagString
from sqlconf.config import SKIP_PARAMETERS
from sqlconf.config import RANDOM_INT_STR1, RANDOM_INT_STR2
from utils.function import trimResponseTag

sqliboolfile = os.path.join("sqlconf", 'sqlibool.xml')
sqlierrorfile = os.path.join("sqlconf", 'sqlierror.xml')
sqlitimefile = os.path.join("sqlconf", 'sqlitime.xml')


class SqliCheck(object):
    def __init__(self, url, method="", postdata={}, headers=[], skip=[], scanlevel=1, callbacks=''):
        self.url = url
        self.postdata = postdata  # 表单的数据
        self.method = method
        self.skip = skip  # 忽略的参数
        self.headers = headers
        self.isSQLI = False
        self.scanlevel = scanlevel
        # self.postdatas = {}  # post数据转换成字典格式
        self.sqliPayload = ''  # 注入使用的payload
        self.sqliParam = ''  # 存在注入参数
        self.randomint1 = str(random.randint(10, 30))
        self.randomint2 = str(random.randint(40, 60))

        # requests = reqeusts(callbacks)

    # bool类型注入检测
    def sqlibool(self):
        root = minidom.parse(sqliboolfile).documentElement
        # 扫描等级判断
        for node in root.getElementsByTagName('couple'):
            if self.scanlevel >= int(node.getAttribute('id')):
                for compare in node.getElementsByTagName("compare"):
                    compare1 = compare.getElementsByTagName(
                        "compare1")[0].childNodes[0].nodeValue
                    compare2 = compare.getElementsByTagName(
                        "compare2")[0].childNodes[0].nodeValue
                    if self.method == "POST":
                        for k, v in self.postdata.items():
                            if k in SKIP_PARAMETERS:
                                # log.info('ignore parameter [%s] ' % k)
                                continue
                            print(v)
                            # print '[-] Test Parameter %s' % k
                            compare1 = compare1.replace(RANDOM_INT_STR2, self.randomint2).replace(
                                RANDOM_INT_STR1, self.randomint1)
                            compare2 = compare2.replace(RANDOM_INT_STR2, self.randomint2).replace(
                                RANDOM_INT_STR1, self.randomint1)
                            # 正常注入逻辑
                            teststr = v.replace(
                                BOUNDED_INJECTION_MARKER, compare1)
                            # .encode('utf-8').decode('utf-8')
                            html1 = trimResponseTag(requests.post(
                                self.url, data=teststr, headers=self.headers).text)
                            html2 = trimResponseTag(requests.post(self.url, data=v.replace(
                                BOUNDED_INJECTION_MARKER, compare2), headers=self.headers).text)  # .encode('utf-8').decode('utf-8')

                            flagString = getFlagString(html1, html2)
                            # 页面中存在关键字
                            if flagString:
                                print('--string type')
                                compare3 = compare1.replace(RANDOM_INT_STR2, str(random.randint(
                                    81, 99))).replace(RANDOM_INT_STR1, str(random.randint(61, 80)))
                                compare4 = compare2.replace(RANDOM_INT_STR2, str(random.randint(
                                    81, 99))).replace(RANDOM_INT_STR1, str(random.randint(81, 99)))
                                html3 = trimResponseTag(requests.post(self.url, data=v.replace(
                                    BOUNDED_INJECTION_MARKER, compare3), headers=self.headers).text)
                                html4 = trimResponseTag(requests.post(self.url, data=v.replace(
                                    BOUNDED_INJECTION_MARKER, compare4), headers=self.headers).text)
                                if (flagString in html3 and flagString not in html4) or (flagString not in html3 and flagString in html4):
                                    self.isSQLI = True
                                    self.sqliPayload = compare3
                                    self.sqliParam = k
                                    return self.isSQLI

                            if getPagesRatio(html1, html2) < DEFAULT_RADIO:
                                self.isSQLI = True
                                self.sqliPayload = v.replace(
                                    BOUNDED_INJECTION_MARKER, compare1)
                                self.sqliParam = k
                                return self.isSQLI

                    if self.method == "GET":

                        for k, v in self.postdata.items():
                            if k in SKIP_PARAMETERS:
                                continue
                            # print '[-] Test Parameter %s' % k
                            getpayload1 = v.replace(BOUNDED_INJECTION_MARKER, compare1).replace(
                                RANDOM_INT_STR2, self.randomint2).replace(RANDOM_INT_STR1, self.randomint1)
                            getpayload2 = v.replace(BOUNDED_INJECTION_MARKER, compare2).replace(
                                RANDOM_INT_STR2, self.randomint2).replace(RANDOM_INT_STR1, self.randomint1)
                            # .encode('utf-8').decode('utf-8')
                            html1 = trimResponseTag(requests.get(
                                getpayload1, headers=self.headers).text)
                            # .encode('utf-8').decode('utf-8')
                            html2 = trimResponseTag(requests.get(
                                getpayload2, headers=self.headers).text)

                            flagString = getFlagString(html1, html2)
                            # 页面中存在关键字
                            if flagString:
                                print('--string type')
                                getpayload3 = v.replace(BOUNDED_INJECTION_MARKER, compare1).replace(RANDOM_INT_STR2, str(
                                    random.randint(81, 99))).replace(RANDOM_INT_STR1, str(random.randint(61, 80)))
                                getpayload4 = v.replace(BOUNDED_INJECTION_MARKER, compare2).replace(RANDOM_INT_STR2, str(
                                    random.randint(81, 99))).replace(RANDOM_INT_STR1, str(random.randint(61, 80)))

                                html3 = trimResponseTag(requests.get(
                                    getpayload3, headers=self.headers).text)
                                html4 = trimResponseTag(requests.get(
                                    getpayload4, headers=self.headers).text)
                                if (flagString in html3 and flagString not in html4) or (flagString not in html3 and flagString in html4):
                                    print('--string SQLI type')
                                    self.isSQLI = True
                                    self.sqliPayload = getpayload3
                                    self.sqliParam = k
                                    return self.isSQLI
                            if getPagesRatio(html1, html2) < DEFAULT_RADIO:
                                self.isSQLI = True
                                self.sqliPayload = "%s" % (getpayload1)
                                self.sqliParam = k
                                return self.isSQLI
            else:
                return self.isSQLI

    # 基于时间的注入检测
    def sqlitime(self):
        root = minidom.parse(sqlitimefile).documentElement
        for node in root.getElementsByTagName('couple'):
            if self.scanlevel >= int(node.getAttribute('id')):
                payloads = node.getElementsByTagName(
                    'requests')[0].childNodes[0].nodeValue.strip()
                for payitem in payloads.splitlines():
                    if self.method == 'POST':
                        for k, v in self.postdata.items():
                            if k in SKIP_PARAMETERS:
                                continue
                            time_start = time.time()
                            requests.post(self.url, data=v.replace(
                                BOUNDED_INJECTION_MARKER, payitem.strip()), headers=self.headers)
                            time_end = time.time()
                            cost_time = time_end - time_start
                            if cost_time >= 5:
                                self.isSQLI = True
                                self.sqliPayload = v.replace(
                                    BOUNDED_INJECTION_MARKER, payitem.strip())
                                self.sqliParam = k
                                return self.isSQLI

                    if self.method == 'GET':
                        for k, v in self.postdata.items():
                            if k in SKIP_PARAMETERS:
                                continue
                            #  print '[-] Test Parameter %s' % k
                            getpayload = v.replace(
                                BOUNDED_INJECTION_MARKER, payitem.strip())
                            time_start = time.time()
                            requests.get(getpayload, headers=self.headers)
                            time_end = time.time()
                            cost_time = time_end - time_start
                            if cost_time >= 5:
                                self.isSQLI = True
                                self.sqliPayload = getpayload
                                self.sqliParam = k
                                return self.isSQLI
            else:
                return self.isSQLI

    # 报错类型的注入检测

    def sqlierror(self):
        root = minidom.parse(sqlierrorfile).documentElement
        # 扫描等级判断
        for node in root.getElementsByTagName('couple'):
            if self.scanlevel >= int(node.getAttribute('id')):
                payloads = node.getElementsByTagName(
                    'requests')[0].childNodes[0].nodeValue.strip()
                for payitem in payloads.splitlines():
                    if self.method == 'POST':
                        for k, v in self.postdata.items():
                            # 不检测的参数
                            if k in SKIP_PARAMETERS:
                                continue
                            html = requests.post(self.url, data=v.replace(BOUNDED_INJECTION_MARKER, payitem.strip(
                            )), headers=self.headers).text  # .encode('utf-8').decode('utf-8')
                            for response_rule in node.getElementsByTagName('responses')[0].childNodes[0].nodeValue.strip().splitlines():
                                if re.search(response_rule.strip(), html):
                                    self.isSQLI = True
                                    self.sqliPayload = v.replace(
                                        BOUNDED_INJECTION_MARKER, payitem.strip())
                                    self.sqliParam = k

                                    # print self.sqliPayload
                                    return self.isSQLI

                    if self.method == "GET":
                        for k, v in self.postdata.items():
                            if k in SKIP_PARAMETERS:
                                continue
                            # print '[-] Test Parameter %s' % k
                            getpayload = v.replace(
                                BOUNDED_INJECTION_MARKER, payitem.strip())
                            # .encode('utf-8').decode('utf-8')
                            html = requests.get(
                                getpayload, headers=self.headers).text
                            # print html.encode('utf-8')#.decode('utf-8')
                            for response_rule in node.getElementsByTagName('responses')[0].childNodes[0].nodeValue.strip().splitlines():
                                if re.search(response_rule.strip().encode("utf-8"), html):
                                    self.isSQLI = True
                                    self.sqliPayload = "%s" % (getpayload)
                                    self.sqliParam = k
                                    return self.isSQLI

            else:
                return self.isSQLI

    def run(self):
        issqli = self.sqlierror() or self.sqlibool() or self.sqlitime()
        return self


def main():
    url = "http://service2.winic.org/service.asmx/GetMessageRecord"
    url1 = "http://demo.aisec.cn/demo/aisec/html_link.php?id=2"
    postdata = {
        "id": "1"
    }

    headers = {
        "cookie": "access_token=e0f2a4a2-5671-4c5c-9868-071150f69765"
    }

    sqli = SqliCheck(url1, method="GET", postdata=postdata, headers=headers, skip=[
                     'allecIDs', 'beginDate', '_t', 'billBeginDate', 'billEndDate', 'note', 'level', 'goodsIDs', 'pageNo', 'pageSize'], scanlevel=3).run()
    if sqli.isSQLI:
        print('[+] URL : ', sqli.url)
        print('[+] isSQLI : ', sqli.isSQLI)
        print('[+] Scan level : ', sqli.scanlevel)
        print('[+] Sqli payload : ', sqli.sqliPayload)


if __name__ == '__main__':
    main()
