#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 18/6/2023 下午2:12
# @Author  : LeaVES
# @FileName: cfms_ui.py
# coding: utf-8
import threading

from PyQt6.QtCore import *
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import *
from qfluentwidgets import *
from interface.login_window import LoginWindow
from interface.main_window import MainWindow
from util.cfms_common import *

RESOURCE_IMAGES = "resource/images/"
OPPOSING_THEME = {Theme.DARK: Theme.LIGHT, Theme.LIGHT: Theme.DARK}


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
        self.setFixedSize(self.width(), self.height())
        self.setLoginPage(0)

    def setLoginPage(self, state: int = 0):
        """为0时显示服务器连接界面,为1时显示用户登陆界面."""
        if state == 0:
            self.label_title.setText("Link Server")
            self.stackWidget.setCurrentWidget(self.server_info_bar)
        elif state == 1:
            self.label_title.setText("Login")
            self.user_info_bar.stackWidget.setCurrentWidget(self.user_info_bar.page00)
            self.stackWidget.setCurrentWidget(self.user_info_bar)
        elif state == 2:
            self.label_title.setText("Login")
            self.user_info_bar.stackWidget.setCurrentWidget(self.user_info_bar.page01)
            self.stackWidget.setCurrentWidget(self.user_info_bar)
        else:
            raise TypeError

    def setLoadingState(self, isLoading: bool):
        """
        设置登陆界面的UI加载状态
        为假时停止加载条
        """
        if not isLoading:
            self.loadProgressBar.stop()
            self.server_info_bar.link_server_button.setEnabled(True)
            self.server_info_bar.link_cancel_button.setEnabled(False)
            self.user_info_bar.back_Button.setEnabled(True)
            self.user_info_bar.login_Button.setEnabled(True)
            self.user_info_bar.page01.login_out_Button.setEnabled(True)
        else:
            self.loadProgressBar.start()
            self.server_info_bar.link_server_button.setEnabled(False)
            self.server_info_bar.link_cancel_button.setEnabled(True)
            self.user_info_bar.back_Button.setEnabled(False)
            self.user_info_bar.login_Button.setEnabled(False)
            self.user_info_bar.page01.login_out_Button.setEnabled(False)

    def getServerAddress(self):
        ...
        hostname = self.server_info_bar.serverAdLE.text().strip()
        port = self.server_info_bar.serverPortLE.text().strip()
        return hostname, port

    def getUserAccount(self):
        username = self.user_info_bar.page00.userNameLE.text().strip()
        password = self.user_info_bar.page00.userPasswordLE.text().strip()
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

    def actions_connector(self, action_name: str = "", func=None, disconnect: bool = False):
        reflection = {
            "back": self.user_info_bar.back_Button,
            "cancel": self.server_info_bar.link_cancel_button,
            "link": self.server_info_bar.link_server_button,
            "login": self.user_info_bar.login_Button,
            "logout": self.user_info_bar.page01.login_out_Button,
            "show_connected_server_info": self.user_info_bar.connected_server_info,
        }
        if disconnect:
            try:
                reflection[action_name].disconnect()
            except TypeError:
                pass
            return

        reflection[action_name].clicked.connect(func)
        return

    def loginUI(self):
        self.show()
        self.splashScreen.finish()


class MainUI(MainWindow):
    def __init__(self, *args, **kwargs):
        super(MainUI, self).__init__(parent=self)
        self.set_widget_theme(theme())

        # widgets theme
        self.client_thread = kwargs["thread"]
        try:
            self.functions = kwargs["functions"]
        except KeyError:
            self.functions = {}
        for p in self.pages:
            p.setup_ui(self.functions, functions=self.functions)

        self.get_files_function = self.functions.get(self.GET_FILES, do_nothing)
        # 在导航栏添加组件
        self.addSubInterface(self.home_page, FluentIcon.HOME_FILL,
                             lambda: self.stackWidget.setCurrentWidget(self.home_page), "Home")

        self.navigationInterface.addSeparator()

        self.addSubInterface(self.file_page, FluentIcon.FOLDER, self.show_file_page, "Files")

        self.addSubInterface(self.task_page, FluentIcon.TAG,
                             lambda: self.stackWidget.setCurrentWidget(self.task_page), "Tasks")

        # 在此处设置hBoxLayout的边距
        self.hBoxLayout.setContentsMargins(0, self.titleBar.height(), 0, 0)
        self.titleBarObj.funcs.append(
            lambda: self.file_page.set_files_list(files=self.file_page.file_information, force=True))

    def show_file_page(self):
        self.stackWidget.setCurrentWidget(self.file_page)
        self.get_files_function(self.file_page.current_path[0])

    def closeEvent(self, event):
        self.client_thread.close_connection()
        event.accept()

    def actions_connector(self, action_name: str = "", func=None, disconnect: bool = False):
        if disconnect:
            del self.functions[action_name]
            return

        self.functions[action_name] = func

        for p in self.pages:
            p.connect_signal_solt(self.functions)

        self.get_files_function = self.functions.get(self.GET_FILES, lambda: ...)

    def mainUI(self):
        self.show()
        self.splashScreen.finish()
