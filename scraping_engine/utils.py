import re


def str_split_strip(delimiter, string):
    return list(map(str.strip, re.split(delimiter, string.strip())))
