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
from qframelesswindow import StandardTitleBar, FramelessWindow

from interface.LoginWindow import LoginWindow
from interface.MainWindow import MainWindow

RESOURCE_IMAGES = "resource/images/"
DEFAULT_THEME_COLOUR = "#28afe9"

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

    infoType[type.lower()](
        title,
        infomation,
        isClosable=True,
        position=position[whereis.upper()],
        duration=durationTime,
        parent=objectName
    )

class MessageDisplay(MessageDialog):
    """重写message_dialog控件"""
    def __init__(self, title: str, content: str, parent, btndisplay:tuple=(True, True), btnText: tuple=("OK","Cancel")):
        super(MessageDisplay, self).__init__(title=title, content=content, parent=parent)
        self.contentLabel.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        if btndisplay[0]: self.yesButton.setText(f"{btnText[0]}")
        else: self.yesButton.setVisible(False)
        if btndisplay[1]: self.cancelButton.setText(f"{btnText[1]}")
        else: self.cancelButton.setVisible(False)
 
class LeaVESTitleBar(StandardTitleBar):
    """LeaVES Title Bar"""
    def __init__(self, parent):
        super(LeaVESTitleBar, self).__init__(parent=parent)
        self.titleLabel.setStyleSheet("QLabel{ color: black}")
        spacerItem = QSpacerItem(220, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.titlebarBtn = ToolButton(FluentIcon.CONSTRACT,parent = self)
        self.hBoxLayout.insertItem(3,spacerItem)
        self.hBoxLayout.insertWidget(4, self.titlebarBtn, 0, Qt.AlignmentFlag.AlignRight)
        self.titlebarBtn.clicked.connect(lambda: ShowWindows.setThemeState(parent))

    def setLeaVESTitBarTheme(self, titleBarTheme:str="DARK"):
        if titleBarTheme.upper() == "DARK":
            self.titleLabel.setStyleSheet("QLabel{ color: white}")
        elif titleBarTheme.upper() == "LIGHT":
            self.titleLabel.setStyleSheet("QLabel{ color: black}")

    def useBackGround(self):
        desktop = QApplication.screens()[0].availableGeometry()
        width, height = desktop.width(), desktop.height()
        self.backgroundLable = QLabel(parent=self)
        self.backgroundLable.setGeometry(0, 0, width, height)
        self.backgroundLable.lower()

class ShowWindows(FramelessWindow):
    def __init__(self):
        """所有窗口采用统一的样式,
        统一设置,避免重复"""
        super().__init__()
        self.theme = Theme.LIGHT
        # 主题色
        setThemeColor(F'{DEFAULT_THEME_COLOUR}')
        # 标题栏
        self.titleBarObj = LeaVESTitleBar(parent=self)
        self.setTitleBar(self.titleBarObj)
        self.titleBar.raise_()
        self.setWindowTitle('sfms__2.0')
        self.setWindowIcon(QIcon(f"{RESOURCE_IMAGES}logo.png"))
        # 大小
        self.resize(1000, 650)
        self.windowEffect.setMicaEffect(self.winId())
        self.desktop = QApplication.screens()[0].availableGeometry()
        width, height = self.desktop.width(), self.desktop.height()
        self.setMinimumSize(QSize(700, 500))
        self.setMaximumSize(QSize(width, height))
        # 移动窗口的位置，让它位于屏幕正中间
        center = width // 2 - self.width() // 2, height // 2 - self.height() // 2
        self.move(center[0], center[1])

    def setThemeState(self):
        """切换主题模式"""
        if isDarkTheme():
            self.theme = Theme.LIGHT
            interfaceTheme = "LIGHT"
            # titlebar theme
            self.titleBarObj.setLeaVESTitBarTheme(titleBarTheme="LIGHT")
        elif not isDarkTheme():
            self.theme = Theme.DARK
            interfaceTheme = "DARK"
            self.titleBarObj.setLeaVESTitBarTheme(titleBarTheme="DARK")
        # label theme
        self.setInterfaceTheme(interfaceTheme)
        # widgets theme
        setTheme(self.theme)

class LoginUI(ShowWindows, LoginWindow):
    def __init__(self):
        super().__init__()
        self.label.setPixmap(QPixmap(f"{RESOURCE_IMAGES}login_b.jpg"))
        self.label_head_icon.setPixmap(QPixmap(f"{RESOURCE_IMAGES}logo.png"))
        self.titleBar.hBoxLayout.removeWidget(self.titleBar.maxBtn)
        # self.setFixedSize(self.width(), self.height())
        self.setLoginState(0)

    def setInterfaceTheme(self, interfaceTheme:str="LIGHT"):
        if interfaceTheme == "DARK":
            styleSheet = "background-color: #333333;"
            labelStyle = """QLabel{
            font: 13px 'Microsoft YaHei';
            font-weight: bold;
            color: white
            }"""
        elif interfaceTheme == "LIGHT":
            styleSheet = "background-color: white;"
            labelStyle = """QLabel{
            font: 13px 'Microsoft YaHei';
            color: black
            }"""
        self.setStyleSheet(styleSheet)
        self.widget.setStyleSheet(labelStyle)

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
        """为1时显示用户登陆界面, 为0时显示服务器连接界面"""
        if state == 1: 
            self.label_title.setText("Login")
            self.__setQVBoxLayoutUserVisible(True)
            self.__setGridLayoutServerVisible(False)
        elif state == 0:
            self.label_title.setText("Link Server")
            self.__setQVBoxLayoutUserVisible(False)
            self.__setGridLayoutServerVisible(True)
        else:
            raise TypeError

    def getServerAddess(self):
        hostname = self.serverAdLE.text().strip()
        port = self.serverPortLE.text().strip()
        return (hostname, port)
    
    def getUserAccount(self):
        username = self.userNameLE.text().strip()
        password = self.userPasswordLE.text().strip()
        return (username, password)
    
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
        self.titleBarObj.useBackGround()
        # 防止导航栏挡住标题栏
        # 因为titleBar不在MainWindows.py,所以在此处设置hBoxLayout的边距
        self.hBoxLayout.setContentsMargins(0, self.titleBar.height(), 0, 0)

    def setInterfaceTheme(self, interfaceTheme:str="LIGHT"):
        styleSheet = "background-color: #333333;" if interfaceTheme == "DARK" else "background-color: white;"
        self.titleBarObj.setStyleSheet(styleSheet)
    def mainUI(self):
        self.show()
