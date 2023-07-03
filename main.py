#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 18/6/2023 下午5:24
# @Author  : LeaVES
# @FileName: Main.py
# coding: utf-8

import sys

from PyQt6.QtCore import QLocale
from PyQt6.QtWidgets import QApplication
from qfluentwidgets import FluentTranslator
from ui import LoginUI, MainUI

def main():
    app = QApplication(sys.argv)
    translator = FluentTranslator(QLocale())
    app.installTranslator(translator)
    # 创建登入窗口实例
    login_w = LoginUI()
    login_w.loginUI()
    # 创建主窗口实例
    main_w = MainUI()
    main_w.mainUI()
    # 启动Qt应用程序
    app.exec()


if __name__ == '__main__':
    main()