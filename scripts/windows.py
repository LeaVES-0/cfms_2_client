#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 18/6/2023 下午2:12
# @Author  : LeaVES
# @FileName: windows.py
# coding: utf-8

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import *
from qfluentwidgets import *
from qframelesswindow import StandardTitleBar, FramelessWindow

from interface.login_window import LoginWindow
from interface.main_window import MainWindow

RESOURCE_IMAGES = "interface/resource/images/"
DEFAULT_THEME_COLOUR = "#28afe9"


def info_message_display(object_name, information_type: str = "info",
                         information: str = "",
                         title: str = "Null",
                         whereis: str = "TOP",
                         duration_time: int = 2000):
    info_type = {"info": InfoBar.success,
                 "warn": InfoBar.warning,
                 "error": InfoBar.error}
    position = {"TOP": InfoBarPosition.TOP,
                "TOP_LEFT": InfoBarPosition.TOP_LEFT,
                "TOP_RIGHT": InfoBarPosition.TOP_RIGHT,
                "BUTTON": InfoBarPosition.BOTTOM,
                "BUTTON_LEFT": InfoBarPosition.BOTTOM_LEFT,
                "BUTTON_RIGHT": InfoBarPosition.BOTTOM.BOTTOM_RIGHT}

    info_type[information_type.lower()](
        title,
        information,
        isClosable=True,
        position=position[whereis.upper()],
        duration=duration_time,
        parent=object_name
    )


class MessageDisplay(MessageDialog):
    """重写message_dialog控件"""

    def __init__(self, title: str, content: str, parent, btn_display: tuple = (True, True),
                 btn_text: tuple = ("OK", "Cancel")):
        super(MessageDisplay, self).__init__(title=title, content=content, parent=parent)
        self.contentLabel.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        if btn_display[0]:
            self.yesButton.setText(f"{btn_text[0]}")
        else:
            self.yesButton.setVisible(False)
        if btn_display[1]:
            self.cancelButton.setText(f"{btn_text[1]}")
        else:
            self.cancelButton.setVisible(False)


class LeaVESTitleBar(StandardTitleBar):
    """LeaVES Title Bar"""

    def __init__(self, parent):
        super(LeaVESTitleBar, self).__init__(parent=parent)
        self.titleLabel.setStyleSheet("QLabel{ color: black}")
        spacer_item = QSpacerItem(40, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.titlebarBtn = ToolButton(FluentIcon.CONSTRACT, parent=self)
        self.hBoxLayout.insertItem(3, spacer_item)
        self.hBoxLayout.insertWidget(4, self.titlebarBtn, 0, Qt.AlignmentFlag.AlignRight)
        self.titlebarBtn.clicked.connect(lambda: ShowWindows.setThemeState(parent))

    def set_leaves_titlebar_theme(self, title_bar_theme: str = "DARK"):
        if title_bar_theme.upper() == "DARK":
            self.titleLabel.setStyleSheet("QLabel{ color: white}")
        elif title_bar_theme.upper() == "LIGHT":
            self.titleLabel.setStyleSheet("QLabel{ color: black}")


class ShowWindows(FramelessWindow):
    def __init__(self):
        """所有窗口采用统一的样式,
        统一设置,避免重复"""
        super().__init__()
        self.theme = Theme.LIGHT
        # 主题色
        setThemeColor(f'{DEFAULT_THEME_COLOUR}')
        # 标题栏
        self.titleBarObj = LeaVESTitleBar(parent=self)
        self.setTitleBar(self.titleBarObj)
        self.titleBar.raise_()
        self.setWindowTitle('cfms__2.0')
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
            interface_theme = "LIGHT"
            # titlebar theme
            self.titleBarObj.set_leaves_titlebar_theme(title_bar_theme="LIGHT")
        else:
            self.theme = Theme.DARK
            interface_theme = "DARK"
            self.titleBarObj.set_leaves_titlebar_theme(title_bar_theme="DARK")
        # label theme
        self.set_interface_theme(interface_theme)
        # widgets theme
        setTheme(self.theme)

    def set_interface_theme(self, interface_theme):
        pass


class LoginUI(ShowWindows, LoginWindow):
    def __init__(self):
        super().__init__()
        self.label.setPixmap(QPixmap(f"{RESOURCE_IMAGES}login_b.jpg"))
        self.label_head_icon.setPixmap(QPixmap(f"{RESOURCE_IMAGES}logo.png"))
        self.titleBar.hBoxLayout.removeWidget(self.titleBar.maxBtn)
        # self.setFixedSize(self.width(), self.height())
        self.setLoginState(0)

    def set_interface_theme(self, interface_theme: str = "LIGHT"):
        if interface_theme == "DARK":
            interface_style_sheet = "background-color: #333333;"
            label_style = """QLabel{
            font: 'Microsoft YaHei';
            font-weight: bold;
            color: white
            }"""
        else:
            interface_style_sheet = "background-color: white;"
            label_style = """QLabel{
            font: 'Microsoft YaHei';
            color: black
            }"""
        self.setStyleSheet(interface_style_sheet)
        self.widget.setStyleSheet(label_style)

    def __set_qvboxlayout_user_visible(self, value: bool = False):
        """显示/隐藏账户密码栏"""
        for i in range(self.QVBoxLayout_2.count()):
            if not isinstance(self.QVBoxLayout_2.itemAt(i), QSpacerItem):
                item = self.QVBoxLayout_2.itemAt(i)
                item.widget().setVisible(value)

    def __setGridLayoutServerVisible(self, value: bool = True):
        for i in range(self.GridLayoutFServer.count()):
            if not isinstance(self.GridLayoutFServer.itemAt(i), QSpacerItem):
                item = self.GridLayoutFServer.itemAt(i)
                item.widget().setVisible(value)

    def setLoginState(self, state: int = 0):
        """为1时显示用户登陆界面, 为0时显示服务器连接界面"""
        if state == 1:
            self.label_title.setText("Login")
            self.__set_qvboxlayout_user_visible(True)
            self.__setGridLayoutServerVisible(False)
        elif state == 0:
            self.label_title.setText("Link Server")
            self.__set_qvboxlayout_user_visible(False)
            self.__setGridLayoutServerVisible(True)
        else:
            raise TypeError

    def getServerAddress(self):
        hostname = self.serverAdLE.text().strip()
        port = self.serverPortLE.text().strip()
        return hostname, port

    def getUserAccount(self):
        username = self.userNameLE.text().strip()
        password = self.userPasswordLE.text().strip()
        return username, password

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
        # 防止导航栏挡住标题栏
        # 因为titleBar不在MainWindows.py,所以在此处设置hBoxLayout的边距
        self.file_list = []
        self.hBoxLayout.setContentsMargins(0, self.titleBar.height(), 0, 0)
        self.addSubInterface(self.file_page, FluentIcon.FOLDER, 'File', self.load_file_page(),
                             position=NavigationItemPosition.SCROLL)

    def load_file_page(self):
        self.stackWidget.setCurrentWidget(self.file_page)

    def set_interface_theme(self, interface_theme: str = "LIGHT"):
        if interface_theme == "DARK":
            interface_style_sheet = "background-color: #333333;"
            label_style = """QLabel{
            font: 13px 'Microsoft YaHei';
            font-weight: bold;
            background-color:transparent;
            color: white
            }"""
        else:
            interface_style_sheet = "background-color: white;"
            label_style = """QLabel{
            font: 13px 'Microsoft YaHei';
            background-color: transparent;
            color: black
            }"""
        self.stackWidget.setStyleSheet(label_style)
        self.setStyleSheet(interface_style_sheet)

    def mainUI(self):
        self.show()
