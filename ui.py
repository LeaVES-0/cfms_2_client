#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 18/6/2023 下午2:12
# @Author  : LeaVES
# @FileName: LoginWindow.py
# coding: utf-8

import sys

from PyQt6.QtCore import Qt, QLocale, QSize
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import QApplication
from qfluentwidgets import setThemeColor, FluentTranslator
from qframelesswindow import StandardTitleBar, AcrylicWindow, FramelessWindow

from Windows.LoginWindow import LoginWindow
from Windows.MainWindow import MainWindow

RESOURCE_IMAGES = "resource/images/"


class ShowWindows (AcrylicWindow):
    def __init__(self):
        super().__init__()

    def winSet(self):
        """所有窗口采用统一的样式,
        统一设置,避免重复"""
        # 主题色
        setThemeColor('#28afe9')
        # 标题栏
        self.setTitleBar(StandardTitleBar(parent=self))
        self.titleBar.raise_()
        self.setWindowTitle('sfms__2.0')
        self.setWindowIcon(QIcon(f"{RESOURCE_IMAGES}logo.png"))
        # 大小
        self.resize(1000, 650)
        self.windowEffect.setMicaEffect(self.winId())
        self.setMinimumSize(QSize(700, 500))
        # 标题栏风格设置
        style = """QLabel{
            background: transparent;
            font: 13px 'Segoe UI';
            color: black;padding: 0 4px
        }
        """
        self.titleBar.titleLabel.setStyleSheet(style)
        # 移动窗口的位置，让它位于屏幕正中间
        desktop = QApplication.screens()[0].availableGeometry()
        width, height = desktop.width(), desktop.height()
        center = width // 2 - self.width() // 2, height // 2 - self.height() // 2
        self.move(center[0], center[1])


class LoginUI(LoginWindow, ShowWindows):
    def __init__(self):
        super().__init__()
        super().setup_login_ui()
        super().winSet()
        self.label.setPixmap(QPixmap(f"{RESOURCE_IMAGES}login_b.jpg"))
        self.label_ground.setPixmap(QPixmap(f"{RESOURCE_IMAGES}logo.png"))

    def resizeEvent(self, e):
        self.label.setScaledContents(False)
        super().resizeEvent(e)
        pixmap = QPixmap(f"{RESOURCE_IMAGES}login_b.jpg").scaled(
            self.label.size(),
            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation
        )
        self.label.setPixmap(pixmap)

    def loginUI(self):
        self.show()


class MainUI(ShowWindows, MainWindow):
    def __init__(self):
        super().__init__()


    def mainUI(self):
        super().setup_main_ui()
        super().winSet()
        """初始化父类"""
        # windows_init(self)
        # 防止导航栏挡住标题栏
        # 因为titleBar不在MainWindows.py,所以在此处设置hBoxLayout的边距
        self.hBoxLayout.setContentsMargins(0, self.titleBar.height(), 0, 0)
        self.show()
