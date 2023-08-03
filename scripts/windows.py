#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 18/6/2023 下午2:12
# @Author  : LeaVES
# @FileName: windows.py
# coding: utf-8
import threading

from PyQt6.QtCore import *
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import *
from qfluentwidgets import *
from qframelesswindow import StandardTitleBar, FramelessWindow

from interface.login_window import LoginWindow
from interface.main_window import MainWindow

RESOURCE_IMAGES = "interface/resource/images/"
DEFAULT_THEME_COLOUR = "#28afe9"


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
        super(LeaVESTitleBar, self).__init__(parent)
        self.titleLabel.setStyleSheet("QLabel{ color: black}")
        spacer_item = QSpacerItem(40, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.titlebarBtn = ToolButton(FluentIcon.CONSTRACT, parent=self)
        self.hBoxLayout.insertItem(3, spacer_item)
        self.hBoxLayout.insertWidget(4, self.titlebarBtn, 0, Qt.AlignmentFlag.AlignRight)
        self.titlebarBtn.clicked.connect(lambda: ShowWindows.setThemeState(parent))

    def set_leaves_titlebar_theme(self, title_bar_theme: Theme):
        if title_bar_theme == Theme.DARK:
            self.titleLabel.setStyleSheet("QLabel{ color: white}")
        else:
            self.titleLabel.setStyleSheet("QLabel{ color: black}")


class ShowWindows(FramelessWindow):
    def __init__(self, *args, **kwargs):
        """所有窗口采用统一的样式,
        统一设置,避免重复"""
        super().__init__()
        self.theme = Theme.LIGHT
        # 主题色
        setThemeColor(f'{DEFAULT_THEME_COLOUR}')
        # 标题栏
        self.titleBarObj = LeaVESTitleBar(parent=self)
        self.setTitleBar(self.titleBarObj)
        self.titleBarObj.raise_()
        self.setWindowTitle('cfms  2.0')
        self.setWindowIcon(QIcon(f"{RESOURCE_IMAGES}logo.png"))
        self.splashScreen = SplashScreen(self.windowIcon(), kwargs["parent"])
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

        self.interface_theme = Theme.LIGHT
        setTheme(self.interface_theme)

    def setThemeState(self, interface_theme: Theme = None):
        """切换主题模式"""
        if interface_theme:
            self.set_interface_theme(interface_theme)
            setTheme(interface_theme)
            self.titleBarObj.set_leaves_titlebar_theme(self.interface_theme)
            return
        if self.interface_theme == Theme.DARK:
            self.interface_theme = Theme.LIGHT
            # titlebar theme
            self.titleBarObj.set_leaves_titlebar_theme(self.interface_theme)
        else:
            self.interface_theme = Theme.DARK
            self.titleBarObj.set_leaves_titlebar_theme(self.interface_theme)
        # label theme
        # widgets theme
        setTheme(self.interface_theme)
        self.set_interface_theme(self.interface_theme)

    def set_interface_theme(self, interface_theme: Theme):
        pass


class LoginUI(ShowWindows, LoginWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(parent=self)
        self.setup_ui(self)
        self.set_interface_theme(self.interface_theme)
        # titlebar theme
        self.titleBarObj.set_leaves_titlebar_theme(self.interface_theme)
        # widgets theme
        self.login_finished = False
        self.client_thread = kwargs["thread"]
        self.label.setPixmap(QPixmap(f"{RESOURCE_IMAGES}login_b.jpg"))
        self.label_head_icon.setPixmap(QPixmap(f"{RESOURCE_IMAGES}logo.png"))
        self.titleBar.hBoxLayout.removeWidget(self.titleBar.maxBtn)
        # self.setFixedSize(self.width(), self.height())
        self.setLoginState(0)

    def set_interface_theme(self, interface_theme: Theme):
        if interface_theme == Theme.DARK:
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

    def set_layout_visible(self, q_layout, value: bool = True):
        for i in range(q_layout.count()):
            if not isinstance(q_layout.itemAt(i), QSpacerItem):
                item = q_layout.itemAt(i)
                item.widget().setVisible(value)
        self.titleBarObj.raise_()

    def setLoginState(self, state: int = 0):
        """为0时显示服务器连接界面，为1时显示用户登陆界面."""
        if state == 0:
            self.label_title.setText("Link Server")
            self.set_layout_visible(self.QVBoxLayout_2, False)
            self.set_layout_visible(self.GridLayoutFServer, True)
            self.set_layout_visible(self.QVBoxLayout_3, False)
        elif state == 1:
            self.label_title.setText("Login")
            self.set_layout_visible(self.QVBoxLayout_2, True)
            self.set_layout_visible(self.GridLayoutFServer, False)
            self.set_layout_visible(self.QVBoxLayout_3, False)
        elif state == 2:
            self.label_title.setText("Login")
            self.set_layout_visible(self.QVBoxLayout_2, False)
            self.set_layout_visible(self.GridLayoutFServer, False)
            self.set_layout_visible(self.QVBoxLayout_3, True)
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
        self.label.lower()

    def closeEvent(self, event):
        if not self.login_finished:
            self.client_thread.close_connection()
        event.accept()

    def loginUI(self):
        self.show()
        _timer = threading.Timer(1, self.splashScreen.finish)
        _timer.start()


class MainUI(ShowWindows, MainWindow):

    def __init__(self, *args, **kwargs):
        super(MainUI, self).__init__(parent=self)
        self.setup_ui(self)
        self.set_interface_theme(self.interface_theme)
        # titlebar theme
        self.titleBarObj.set_leaves_titlebar_theme(self.interface_theme)
        # widgets theme
        self.client_thread = kwargs["thread"]
        self.home_page.setup_ui()
        self.file_page.setup_ui(kwargs["functions"])
        self.task_page.setup_ui(kwargs["functions"])
        self.get_files_function = kwargs["functions"]["get_files_function"]
        # 在导航栏添加组件
        self.addSubInterface(self.home_page, FluentIcon.HOME_FILL,
                             lambda: self.stackWidget.setCurrentWidget(self.home_page), "Home")
        self.navigationInterface.addSeparator()
        self.addSubInterface(self.file_page, FluentIcon.FOLDER, self.show_file_page, "Files")
        self.addSubInterface(self.task_page, FluentIcon.TAG,
                             lambda: self.stackWidget.setCurrentWidget(self.task_page), "Tasks")

        # 因为titleBar不在MainWindows.py,所以在此处设置hBoxLayout的边距
        self.hBoxLayout.setContentsMargins(0, self.titleBar.height(), 0, 0)

    def show_file_page(self):
        self.stackWidget.setCurrentWidget(self.file_page)
        self.get_files_function(self.file_page.current_path[0])

    def set_interface_theme(self, interface_theme: Theme):
        if interface_theme == Theme.DARK:
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
        self.setStyleSheet(interface_style_sheet)
        self.stackWidget.setStyleSheet(label_style)

    def closeEvent(self, event):
        self.client_thread.close_connection()
        event.accept()

    def mainUI(self):
        self.show()
        self.setThemeState(self.interface_theme)
        _timer = threading.Timer(1, self.splashScreen.finish)
        _timer.start()
