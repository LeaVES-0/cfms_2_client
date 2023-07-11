#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 18/6/2023 下午5:24
# @Author  : LeaVES
# @FileName: main.py
# coding: utf-8

from controller.cfms_main import MainClient

def main():
        ClientObject = MainClient()
        ClientObject.run()

if __name__ == '__main__':
    main()