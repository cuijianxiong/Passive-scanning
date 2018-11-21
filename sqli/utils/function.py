# -*- coding: utf-8 -*-


import re
from sqlconf.config import RESPONSE_TRIM_FLAGS

"""
    把response中的无用信息过滤，例如traceid，时间戳等
"""
def trimResponseTag(html):
    # 把返回包中的无用信息过滤

    result = html
    for flag in RESPONSE_TRIM_FLAGS:
        result = re.sub(flag[0],flag[1],html)
    return result

