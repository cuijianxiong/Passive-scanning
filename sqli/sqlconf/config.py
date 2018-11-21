# -*- coding: utf-8 -*-



DEFAULT_GET_POST_DELIMITER = '&'
DEFAULT_COOKIE_DELIMITER = ';'
BOUNDED_INJECTION_MARKER= '__INSERT_VUL_PAYLOAD_HERE__'
PARAMETER_AMP_MARKER = "__AMP__"
PARAMETER_SEMICOLON_MARKER = "__SEMICOLON__"
RANDOM_INT_STR1 = "RANDINT"
RANDOM_INT_STR2 = "RANDINT2"

# 注入相关配置

## 页面相似度阀值
DEFAULT_RADIO = 0.95
## 忽略检测参数
SKIP_PARAMETERS = ['_t','__VIEWSTATE','pageSize','pageNo','jsonType (pageSize)',
            'jsonType (pageNo)','pageCount','startTime','endTime','loginName','groupID',
            '_groupID','_role','_loginName','_groupName','_groupLoginName'
        ]
BLACK_RESPONSE_FLAG = [
    u"请重新登录",
    u"验证码错误"

]

RESPONSE_TRIM_FLAGS = [
    ['[a-zA-Z0-9]{8}-[a-zA-Z0-9]{4}-[a-zA-Z0-9]{4}-[a-zA-Z0-9]{4}-[a-zA-Z0-9]{12}','xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'],  # traceid

]
