# -*- coding: utf-8 -*-
# @Time    : 29/9/2023 上午8：26
# @Author  : LeaVES
# @FileName: uie.py
# coding: utf-8

from PyQt6.QtCore import *
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import *
from qfluentwidgets import *
from qframelesswindow import StandardTitleBar
from qframelesswindow import FramelessWindow

class MessageDisplay(MessageDialog):
    """重写message_dialog控件"""

    def __init__(self, title: str, content: str, parent, btn_text: tuple = ("OK", "Cancel")):
        super(MessageDisplay, self).__init__(title=title, content=content, parent=parent)
        self.contentLabel.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        if len(btn_text) == 2:
            self.yesButton.setText(btn_text[0])
            self.cancelButton.setText(btn_text[1])
        else:
            self.yesButton.setVisible(False)
            self.cancelButton.setText(btn_text[0])


class LeaVESTitleBar(StandardTitleBar):
    """LeaVES Title Bar"""
    funcs = []
    def __init__(self, parent, functions: list):
        super(LeaVESTitleBar, self).__init__(parent)
        self.funcs = functions
        self.titleLabel.setStyleSheet("QLabel{ color: black}")
        spacer_item = QSpacerItem(40, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.titlebarBtn = ToolButton(FluentIcon.CONSTRACT, parent=self)  # Dark Mode button
        self.hBoxLayout.insertItem(3, spacer_item)
        self.hBoxLayout.insertWidget(4, self.titlebarBtn, 0, Qt.AlignmentFlag.AlignRight)
        self.titlebarBtn.clicked.connect(self.dark_mode_btn_func)

    @pyqtSlot()
    def dark_mode_btn_func(self):
        for i in self.funcs:
            i()

    def set_theme(self, th: Theme=None):
        if not th:
            th = theme()
        if th == Theme.DARK:
            self.titleLabel.setStyleSheet("QLabel{ color: white}")
            self.minBtn.setStyleSheet("{ color: white}")
        else:
            self.titleLabel.setStyleSheet("QLabel{ color: black}")


RESOURCE_IMAGES = "interface/resource/images/"
DEFAULT_THEME_COLOUR = "#28afe9"


class CfmsUIBase(FramelessWindow):
    def __init__(self, *args, **kwargs):
        """所有窗口采用统一的样式"""
        super().__init__()
        # 主题色
        setThemeColor(f'{DEFAULT_THEME_COLOUR}')
        # 标题栏
        self.titleBarObj = LeaVESTitleBar(parent=self, functions=[self.setThemeState,])
        self.setTitleBar(self.titleBarObj)
        self.titleBarObj.raise_()
        self.setWindowTitle('cfms  2.0')
        self.setWindowIcon(QIcon(f"{RESOURCE_IMAGES}logo.png"))
        self.splashScreen = SplashScreen(self.windowIcon(), parent = self)
        self.splashScreen.setIconSize(QSize(106, 106))
        self.splashScreen.raise_()
        # 大小
        self.resize(1000, 650)
        self.windowEffect.setMicaEffect(self.winId())
        self.desktop = QApplication.screens()[0].availableGeometry()
        width, height = self.desktop.width(), self.desktop.height()
        self.setMinimumSize(QSize(800, 500))
        self.setMaximumSize(QSize(width, height))
        # 移动窗口的位置，让它位于屏幕正中间
        center = width // 2 - self.width() // 2, height // 2 - self.height() // 2
        self.move(center[0], center[1])

        # 默认主题模式
        setTheme(Theme.AUTO)
        self.titleBarObj.set_theme(Theme.AUTO)
        
    @staticmethod
    def themeState():
        return theme()

    def setTitle(self, title_text:str):
        if title_text:
            self.setWindowTitle(self.windowTitle + "   " + title_text)

    def setThemeColour(c: str):
        setThemeColor(c)

    def setThemeState(self, th=None):
        """切换主题模式"""
        opposing = {Theme.DARK:Theme.LIGHT, Theme.LIGHT:Theme.DARK}
        if not th:
            th = opposing[theme()]
        if th == Theme.LIGHT:
            setTheme(Theme.LIGHT)
            self.titleBarObj.set_theme(Theme.LIGHT)
            self.set_widget_theme(Theme.LIGHT)

        else:
            setTheme(Theme.DARK)
            self.titleBarObj.set_theme(Theme.DARK)
            self.set_widget_theme(Theme.DARK)

    def set_widget_theme(self, interface_theme: Theme):
        """切换组件主题模式,此方法需要被继承"""
        ...


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