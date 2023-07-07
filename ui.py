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

from windows.LoginWindow import LoginWindow
from windows.MainWindow import MainWindow

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

class ShowWindows(FramelessWindow):
    def __init__(self):
        super().__init__()
        self.theme = Theme.LIGHT

    def setThemeState(self):
        """切换主题模式"""
        if isDarkTheme():
            self.theme = Theme.LIGHT
            styleSheet = "background-color: white;"
            labelStyle = """QLabel{
            font: 13px 'Microsoft YaHei';
            color: black
            }"""
            # titlebar theme
            self.titleBarObj.setLeaVESTitBarTheme(titleBarTheme="LIGHT")
        elif not isDarkTheme():
            self.theme = Theme.DARK
            styleSheet = "background-color: #333333;"
            labelStyle = """QLabel{
            font: 13px 'Microsoft YaHei';
            font-weight: bold;
            color: white
            }"""
            self.titleBarObj.setLeaVESTitBarTheme(titleBarTheme="DARK")
        # winodow background
        self.setStyleSheet(styleSheet)
        # label theme
        self.setLabelTheme(labelStyle)
        # widgets theme
        setTheme(self.theme)

    def winSet(self):
        """所有窗口采用统一的样式,
        统一设置,避免重复"""
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
        self.titleBar.hBoxLayout.removeWidget(self.titleBar.maxBtn)
        self.setFixedSize(self.width(), self.height())
        self.setLoginState(0)

    def setLabelTheme(self, labelstyle):
        self.widget.setStyleSheet(labelstyle)

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
            self.__setQVBoxLayoutUserVisible(True)
            self.__setGridLayoutServerVisible(False)
        elif state == 0:
            self.__setQVBoxLayoutUserVisible(False)
            self.__setGridLayoutServerVisible(True)
        else:
            raise TypeError

    def getServerAddess(self):
        hostname = self.serverAdLE.text()
        port = self.serverPortLE.text()
        return (hostname, port)
    
    def getUserAccount(self):
        username = self.userNameLE.text()
        password = self.userPasswordLE.text()
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

class MainUI(MainWindow, ShowWindows):
    def __init__(self):
        super().__init__()
        self.setup_main_ui()
        self.winSet()
        # 防止导航栏挡住标题栏
        # 因为titleBar不在MainWindows.py,所以在此处设置hBoxLayout的边距
        self.hBoxLayout.setContentsMargins(0, self.titleBar.height(), 0, 0)

    def setLabelTheme(self, labelstyle):
        self.stackWidget.setStyleSheet(labelstyle)

    def mainUI(self):
        self.show()
