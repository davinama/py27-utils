# coding=utf-8

"""
encode_decode_utils.py

This script contains some useful functions related with python2.7 encoding/decoding,
especially for Chinese characters.

Author: Davina Ma Heming
Date: 2025.06.12
Environment: Python 2.7
"""


import os
import sys
import chardet
from xpinyin import Pinyin

import logging
logger = logging.getLogger(__name__)


def detect_encoding(text):
	"""
	Detect text encoding method.
    This function may make mistakes if the given text length is too short.
	
	:type text: unicode or str
	:rtype: string    # "unicode" / "utf-8" / "gbk" / "GB2312"
	"""
	if isinstance(text, unicode):
		return "unicode"
	detected = chardet.detect(text)
	
	# If chardet has a result, return the guessed result
	if detected.get("encoding"):
		return detected["encoding"].lower()
	# If chardet does not have a result, try decoding from provided decode methods
	else:
		for enc in ["utf-8", "gbk", "big5"]:
			try:
				text.decode(enc)
			except UnicodeDecodeError:
				continue
			else:
				return enc
	return ""
	
	
def coding_transition(text, target_encoding):
	"""
	Get unicode / utf-8 str / gbk str version of the given text.
	
	:type s: unicode or str
	:type target_encoding: string    "unicode" / "utf-8" / "gbk" / "GB2312"
	:rtype: unicode or str
	"""
	from_encoding = detect_encoding(text)
	if not from_encoding:
		return ""
	
	if from_encoding == target_encoding:
		return text
		
	text_unicode = text if from_encoding == "unicode" else text.decode(from_encoding)
	
	if target_encoding == "unicode":
		return text_unicode
	return text_unicode.encode(target_encoding)


def chinese_to_pinyin(name_CN):
    """
    Convert Chinese input pinyin characters, with first letter capitalized

    :type nameCN: string        # 白烟雾
    :rtype: string      # BaiYanWu
    """
    if not name_CN:
        return ""
    
    pinyin_chars = Pinyin().get_pinyin(name_CN).split('-')      # ["bai", "yan", "wu"]
    pinyin_chars = [char.capitalize() if char.islower() else char for char in pinyin_chars]     # ["Bai", "Yan", "Wu"]
    result_str = ''.join(pinyin_chars)      # BaiYanWu
    return result_str