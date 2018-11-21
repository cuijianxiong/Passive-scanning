# -*- coding: utf-8 -*-

import difflib
import re


REFLECTED_VALUE_MARKER = "__REFLECTED_VALUE__"
TEXT_TAG_REGEX = r"(?si)<(abbr|acronym|b|blockquote|br|center|cite|code|dt|em|font|h\d|i|li|p|pre|q|strong|sub|sup|td|th|title|tt|u)(?!\w).*?>(?P<result>[^<]+)"


def extractTextTagContent(page):
    """
    Returns list containing content from "textual" tags

    >>> extractTextTagContent(u'<html><head><title>Title</title></head><body><pre>foobar</><a href="#link">Link</a></body></html>')
    [u'Title', u'foobar']
    """

    page = page or ""

    if REFLECTED_VALUE_MARKER in page:
        try:
            page = re.sub(r"(?i)[^\s>]*%s[^\s<]*" %
                          REFLECTED_VALUE_MARKER, "", page)
        except MemoryError:
            page = page.replace(REFLECTED_VALUE_MARKER, "")

    return filter(None, (_.group("result").strip() for _ in re.finditer(TEXT_TAG_REGEX, page)))


def getFlagString(trueRawResponse, falseRawResponse):
    """获取两个页面中的正常页面中的flag信息

    Arguments:
        trueRawResponse {string} -- 正常页面
        falseRawResponse {string} -- 错误页面

    Returns:
        string -- 标志字符串
    """

    trueSet = set(extractTextTagContent(trueRawResponse))
    trueSet = trueSet.union(__ for _ in trueSet for __ in _.split())
    falseSet = set(extractTextTagContent(falseRawResponse))
    falseSet = falseSet.union(__ for _ in falseSet for __ in _.split())
    candidates = filter(None, (_.strip() if _.strip() in trueRawResponse and _.strip(
    ) not in falseRawResponse else None for _ in (trueSet - falseSet)))

    candidates = list(candidates)  # python3 的坑，python2这个值是［］python是个迭代对象
    print("ca--", candidates)
    if candidates:
        candidates = sorted(candidates, key=lambda _: len(_))
        for candidate in candidates:
            if re.match(r"\A\w+\Z", candidate):
                break
        return candidate
    else:
        return False


def getPagesRatio(trueRawResponse, falseRawResponse):
    """获取两个页面的相似度

    Arguments:
        trueRawResponse {string} -- 正常页面
        falseRawResponse {string} -- 错误页面

    Returns:
        float -- 相似度
    """
    mt = difflib.SequenceMatcher(None)
    mt.set_seq1(trueRawResponse)
    mt.set_seq2(falseRawResponse)
    ratio = round(mt.quick_ratio(), 3)
    return ratio
