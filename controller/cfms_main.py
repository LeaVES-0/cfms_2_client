#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 10/7/2023 下午10:00
# @Author  : LeaVES
# @FileName: cfms_main.py
# coding: utf-8

import sys
from PyQt6.QtCore import QLocale
from PyQt6.QtWidgets import QApplication
from qfluentwidgets import FluentTranslator, Theme

from controller.cfms_user import CfmsUserManager
from scripts.subthread import ClientSubThread
from scripts.windows import LoginUI, MainUI, MessageDisplay, InfoMessageDisplay

class MainClient:
    """客户端主类"""

    def __init__(self):
        self.usermanager = CfmsUserManager()
        self.QtApp = QApplication(sys.argv)
        translator = FluentTranslator(QLocale())
        self.login_w = LoginUI()
        self.login_w.setLoginState(0)
        self.main_w = MainUI()
        self.QtApp.installTranslator(translator)
        self.__loginUI_setButtons()

    def showPublicKeyMeg(self):
        title = 'The Public Key of the Server:'
        content = f"{self.client_socket_obj.public_key}"
        w = MessageDisplay(title, content, parent=self.login_w, btndisplay=(False, True), btnText=("", "OK"))
        w.exec()

    def __diffPublicKeyMeg(self):
        title = 'The Public Key of the Server:'
        content = f"""服务器上的公钥与本地不同,这可能意味着服务器已被重置。
但若非如此,则意味着您可能已遭受中间人攻击。
获取的服务器公钥:
{self.client_socket_obj.public_key}"""
        w = MessageDisplay(title, content, parent=self.login_w, btndisplay=(True, True),
                           btnText=("断开连接", "更换公钥"))
        if w.exec():
            self.__loginUI_backToLinkPageFunction()
        else:
            self.client_socket_obj.pemfile.w_pemfile(pemcontent=self.client_socket_obj.public_key)

    def __loginUI_backToLinkPageFunction(self):
        self.login_w.setLoginState(0)
        self.client_socket_obj.close()
        InfoMessageDisplay(self.login_w, type="info", whereis="TOP_LEFT", title="断开了与服务器的连接", infomation="")
        self.login_w.connectedServerLable.setVisible(False)
        self.login_w.connectedServerLable.setText("")
        print("Socket has been closed.")

    def __loginUI_setButtons(self):
        self.login_w.link_server_button.clicked.connect(
            lambda: self.linkServerFunction(self.login_w.getServerAddess()))
        self.login_w.back_Button.clicked.connect(lambda: self.__loginUI_backToLinkPageFunction())
        self.login_w.login_Button.clicked.connect(lambda: self.userLoginFunction(self.login_w.getUserAccount()))
        self.login_w.connectedServerLable.clicked.connect(lambda: self.showPublicKeyMeg())

    def __checkLinkState(self, args):
        """检测是否连接成功"""
        state = args["clientState"]
        server_address = args["address"]
        self.client_socket_obj = args['clientObj']  # 获取到clientObj对象
        if state:
            print("Link successful")
            InfoMessageDisplay(self.login_w, type="info", whereis="TOP_LEFT", title="连接成功!", infomation="")
            self.login_w.setLoginState(1)
            self.login_w.connectedServerLable.setVisible(True)
            self.login_w.connectedServerLable.setText(f"已连接到 {server_address[0]}:{server_address[1]}")
            self.login_w.loadProgressBar.setVisible(False)
            self.usermanager.remember_linked_server(address=server_address)
            self.usermanager.save_memory()

        elif not state:
            if not args["isSameKey"]:
                self.__diffPublicKeyMeg()
                self.login_w.loadProgressBar.setVisible(False)
            else:
                InfoMessageDisplay(self.login_w, durationTime=5000, type="error", whereis="TOP_RIGHT", title="错误",
                                   infomation=f"{args['error']}")
                self.login_w.loadProgressBar.setVisible(False)

    def __checkLoginState(self, recv):
        """检测登陆状态"""
        if recv["loginState"]:
            if recv["recv"]["code"] == 0:
                # 同步主题
                if self.login_w.theme == Theme.DARK:
                    self.main_w.setThemeState()
                    self.main_w.setThemeState()
                self.userToken = recv["recv"]["token"]
                self.login_w.close()
                self.main_w.mainUI()
                InfoMessageDisplay(self.main_w, type="info", whereis="TOP", title="登录成功!", infomation="")
            elif recv["recv"]["code"] == 401:
                msg = recv["recv"]["msg"]
                InfoMessageDisplay(self.login_w, type="warn", whereis="TOP_LEFT", title="登陆失败。",
                                   infomation=f"密码错误:{msg!s}")
        elif not recv["loginState"]:
            InfoMessageDisplay(self.main_w, type="error", whereis="TOP_LEFT", title="错误",
                               infomation=f"{recv['error']!s}")

    def linkServerFunction(self, address):
        if not address[0] or not address[1]:
            InfoMessageDisplay(self.login_w, type="warn", whereis="TOP_LEFT", title="警告", infomation="地址不得为空")
        elif not isinstance(address[1], str):
            InfoMessageDisplay(self.login_w, type="warn", whereis="TOP_LEFT", title="警告", infomation="地址格式有误")
        else:
            print("Connecting......")
            self.login_w.loadProgressBar.setVisible(True)
            self.link_server_thread = ClientSubThread(action=0, address=address)
            self.link_server_thread.state_signal.connect(self.__checkLinkState)
            self.link_server_thread.start()

    def userLoginFunction(self, account):
        if not account[0] or not account[1]:
            InfoMessageDisplay(self.login_w, type="warn", whereis="TOP_LEFT", title="警告",
                               infomation="用户名或密码不得为空")
        else:
            print('Logining......')
            self.user_login_thread = ClientSubThread(action=1, sock=self.client_socket_obj, name=account[0],
                                                password=account[1])
            self.user_login_thread.state_signal.connect(self.__checkLoginState)
            self.user_login_thread.start()

    def run(self):
        self.login_w.loginUI()
        # start Qt app
        self.main_w.mainUI()
        self.QtApp.exec()