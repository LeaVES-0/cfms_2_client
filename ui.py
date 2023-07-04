#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 18/6/2023 下午2:12
# @Author  : LeaVES
# @FileName: LoginWindow.py
# coding: utf-8

import sys

from PyQt6.QtCore import Qt, QSize, qSetFieldWidth
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import *
from qfluentwidgets import *
from qframelesswindow import StandardTitleBar, AcrylicWindow

from Windows.LoginWindow import LoginWindow
from Windows.MainWindow import MainWindow

RESOURCE_IMAGES = "resource/images/"

def InfoBarDisplay(objectName, type:str="info",
                        infomation:str="null",
                          title:str="Null",
                            whereis:str="TOP",
                            durationTime:int=2000):
    infoType = {"info":InfoBar.success,
                "warn":InfoBar.warning,
                "error":InfoBar.error}
    position = {"TOP":InfoBarPosition.TOP,
                "TOP_LEFT":InfoBarPosition.TOP_LEFT,
                "TOP_RIGHT":InfoBarPosition.TOP_RIGHT,
                "BUTTON":InfoBarPosition.BOTTOM,
                "BUTTON_LEFT":InfoBarPosition.BOTTOM_LEFT,
                "BUTTON_RIGHT":InfoBarPosition.BOTTOM.BOTTOM_RIGHT}

    infoType[type](
        title,
        infomation,
        isClosable=True,
        position=position[whereis],
        duration=durationTime,
        parent=objectName
    )

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
        self.setup_login_ui()
        self.winSet()
        self.label.setPixmap(QPixmap(f"{RESOURCE_IMAGES}login_b.jpg"))
        self.label_head_icon.setPixmap(QPixmap(f"{RESOURCE_IMAGES}logo.png"))
        self.setFixedSize(self.width(), self.height())
        self.setLoginState(0)

        self.back_Button.clicked.connect(lambda: self.setLoginState(0))
        self.link_server_button.clicked.connect(lambda: InfoBarDisplay(self))

    def __setQVBoxLayoutUserVisible(self, value:bool=False):
        """显示/隐藏账户密码栏"""
        for i in range(self.QVBoxLayout_2.count()):
            if not isinstance(self.QVBoxLayout_2.itemAt(i),(QSpacerItem)):
                item = self.QVBoxLayout_2.itemAt(i)
                item.widget().setVisible(value)
    
    def __setGridLayoutServerVisible(self, value:bool=True):
        for i in range(self.GridLayoutFServer.count()):
            if not isinstance(self.GridLayoutFServer.itemAt(i),(QSpacerItem)):
                item = self.GridLayoutFServer.itemAt(i)
                item.widget().setVisible(value)

    def setLoginState(self, state:int=0):
        if state == 1: 
            self.__setQVBoxLayoutUserVisible(True)
            self.__setGridLayoutServerVisible(False)
        elif state == 0:
            self.__setQVBoxLayoutUserVisible(False)
            self.__setGridLayoutServerVisible(True)
        else:
            raise TypeError

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
        self.setup_main_ui()
        self.winSet()
        """初始化父类"""
        # windows_init(self)
        # 防止导航栏挡住标题栏
        # 因为titleBar不在MainWindows.py,所以在此处设置hBoxLayout的边距
        self.hBoxLayout.setContentsMargins(0, self.titleBar.height(), 0, 0)
        self.show()
