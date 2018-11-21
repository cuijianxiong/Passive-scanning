# -*- coding: utf-8 -*-

"""
Copyright (c) 2018 hualala Security (https://www.beysec.com)
author : bey0nd
"""
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
    
    def get_url_params(self):   #  get 参数解析器
        self.get_url,self.params = self.url.split('?')
        print(self.get_url)
        self.params = self.params.split('&')
    

    def post_params(self):
        pass

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
                    if self.method == "GET":
                        for parm in self.params:
                            sql_test1 = self.url.replace(parm,parm+compare1).replace(
                                RANDOM_INT_STR2, self.randomint2).replace(RANDOM_INT_STR1, self.randomint1)
                            sql_test2 = self.url.replace(parm,parm+compare2).replace(
                                RANDOM_INT_STR2, self.randomint2).replace(RANDOM_INT_STR1, self.randomint1)
                            
                            html1 = requests.get(
                                sql_test1, headers=self.headers).text
                            html2 = requests.get(
                                sql_test2, headers=self.headers).text
                            
                            flagString = getFlagString(html1, html2)
                            if flagString:
                                # print('--string type')
                                sql_test3 = self.url.replace(parm,parm+compare1).replace(RANDOM_INT_STR2, str(
                                    random.randint(81, 99))).replace(RANDOM_INT_STR1, str(random.randint(61, 80)))
                                sql_test4 = self.url.replace(parm,parm+compare2).replace(RANDOM_INT_STR2, str(
                                    random.randint(81, 99))).replace(RANDOM_INT_STR1, str(random.randint(61, 80)))
                                html3 = trimResponseTag(requests.get(
                                    sql_test3, headers=self.headers).text)
                                html4 = trimResponseTag(requests.get(
                                    sql_test4, headers=self.headers).text)
                                if (flagString in html3 and flagString not in html4) or (flagString not in html3 and flagString in html4):
                                    # print('--string SQLI type')
                                    self.isSQLI = True
                                    self.sqliPayload = sql_test3
                                    self.sqliParam = parm
                                    return self.isSQLI
                            if getPagesRatio(html1, html2) < DEFAULT_RADIO:
                                self.isSQLI = True
                                self.sqliPayload = "%s" % (sql_test1)
                                self.sqliParam = parm
                                return self.isSQLI
                
            else:
                return self.isSQLI

    def sqlitime(self):
        root = minidom.parse(sqlitimefile).documentElement
        for node in root.getElementsByTagName('couple'):
            if self.scanlevel >= int(node.getAttribute('id')):
                payloads = node.getElementsByTagName(
                    'requests')[0].childNodes[0].nodeValue.strip()
                for payitem in payloads.splitlines():
                    if self.method == "GET":
                        for parm in self.params:
                            sql_test = self.url.replace(parm,parm+payitem.strip())
                            time_start = time.time()
                            html = requests.get(
                                sql_test, headers=self.headers).text
                            time_end = time.time()
                            cost_time = time_end - time_start
                            if cost_time >= 5:
                                self.isSQLI = True
                                self.sqliPayload = "%s" % (payitem)
                                self.sqliParam = parm
                                return self.isSQLI
            else:
                return self.isSQLI


    def sqlierror(self):
        root = minidom.parse(sqlierrorfile).documentElement
        for node in root.getElementsByTagName('couple'):
            if self.scanlevel >= int(node.getAttribute('id')):
                payloads = node.getElementsByTagName(
                    'requests')[0].childNodes[0].nodeValue.strip()
                for payitem in payloads.splitlines():

                    if self.method == "GET":
                        for parm in self.params:
                            sql_test = self.url.replace(parm,parm+payitem.strip())
                            html = requests.get(
                                sql_test, headers=self.headers).text
                            for response_rule in node.getElementsByTagName('responses')[0].childNodes[0].nodeValue.strip().splitlines():
                                if re.search(response_rule.strip(), html):
                                    self.isSQLI = True
                                    self.sqliPayload = "%s" % (payitem)
                                    self.sqliParam = parm
                                    return self.isSQLI
            else:
                return self.isSQLI
                            


    def run(self):
        if self.method == 'GET':
            self.get_url_params()
        issqli =  self.sqlierror() or self.sqlibool() or self.sqlitime()#self.sqlibool()#self.sqlierror() or self.sqlitime()#or self.sqlibool() or self.sqlitime()
        print(issqli)
        return self


def main():
    url1 = "10.246.190.63/DVWA-master/vulnerabilities/sqli/?id=1&Submit=Submit#"
    postdata = {
        "uid": "1"
    }

    headers = {
        "cookie": "security=low; PHPSESSID=moreos061jjhfrnirbdblbat83"
    }

    sqli = SqliCheck(url1, method="GET", postdata=postdata, headers=headers, skip=[
                     'allecIDs', 'beginDate', '_t', 'billBeginDate', 'billEndDate', 'note', 'level', 'goodsIDs', 'pageNo', 'pageSize'], scanlevel=3).run()
    if sqli.isSQLI:
        print('[+] URL : ', sqli.url)
        print('[+] isSQLI : ', sqli.isSQLI)
        print('[+] Scan level : ', sqli.scanlevel)
        print('[+] Sqli param : ', sqli.sqliParam)
        print('[+] Sqli payload : ', sqli.sqliPayload)
        


if __name__ == '__main__':
    main()
