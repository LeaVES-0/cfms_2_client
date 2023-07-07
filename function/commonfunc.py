# -*- coding: utf-8 -*-
# @Time    : 6/7/2023 下午7:47
# @Author  : LeaVES
# @FileName: common.function.py
# coding: utf-8

import os

def writePerclip(msg:str):
    os.system(f"echo {msg} | clip")