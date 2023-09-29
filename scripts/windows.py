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
from interface.login_window import LoginWindow
from interface.main_window import MainWindow

RESOURCE_IMAGES = "interface/resource/images/"


class LoginUI(LoginWindow):
    login_finished = False
    def __init__(self, *args, **kwargs):
        super().__init__(parent=self)
        self.set_widget_theme(theme())
        # widgets theme
        self.client_thread = kwargs["thread"]
        self.label.setPixmap(QPixmap(f"{RESOURCE_IMAGES}login_b.jpg"))
        self.label_head_icon.setPixmap(QPixmap(f"{RESOURCE_IMAGES}logo.png"))
        self.titleBar.hBoxLayout.removeWidget(self.titleBar.maxBtn)
        # self.setFixedSize(self.width(), self.height())
        self.setLoginState(0)

    def set_widget_theme(self, interface_theme: Theme):
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
        """为0时显示服务器连接界面,为1时显示用户登陆界面."""
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


class MainUI(MainWindow):
    def __init__(self, *args, **kwargs):
        super(MainUI, self).__init__(parent=self)
        self.set_widget_theme(theme())

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

        # 在此处设置hBoxLayout的边距
        self.hBoxLayout.setContentsMargins(0, self.titleBar.height(), 0, 0)

    def show_file_page(self):
        self.stackWidget.setCurrentWidget(self.file_page)
        self.get_files_function(self.file_page.current_path[0])

    def set_widget_theme(self, interface_theme: Theme):
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
        _timer = threading.Timer(1, self.splashScreen.finish)
        _timer.start()
