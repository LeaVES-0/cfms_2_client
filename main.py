#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 18/6/2023 下午5:24
# @Author  : LeaVES
# @FileName: Main.py
# coding: utf-8

import sys

from PyQt6.QtCore import Qt, QLocale, QSize
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import QApplication
from qfluentwidgets import setThemeColor, FluentTranslator
from qframelesswindow import StandardTitleBar, AcrylicWindow, FramelessWindow

from Windows.LoginWindow import LoginWindow
from Windows.MainWindow import MainWindow
from ui import LoginUI, MainUI

def main():
    """创建Qt应用程序实例"""
    app = QApplication(sys.argv)
    # Internationalization
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