import requests
import json


'''微信通知接口   需要修改token_url corpid corpsecret的值以及agentid应用id'''

token_url = "https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=wwa4c406ce6d8457c0&corpsecret=ZrKF2JmDGj3boIPa1c_3qRZDD7qHgzVRw3zn8PNVIuw"

def send_data(data):
    tok = requests.get(url=token_url)
    token = json.loads(tok.content)['access_token']
    print(token)
    data_url = "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token="+token
    data = '{"touser" : "beifengpiaoran","toparty" :"@all","totag" :"@all","agentid" : 1000003,"msgtype" : "text","text" : {"content" : "'+data+'"},"safe":0}'
    
    print(data)
    a = requests.post(url=data_url,data=data)
    print(a.content)

