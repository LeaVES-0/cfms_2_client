#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 18/6/2023 下午5:24
# @Author  : LeaVES
# @FileName: Main.py
# coding: utf-8

import sys

from PyQt6.QtCore import QLocale, QThread, pyqtSignal
from PyQt6.QtWidgets import QApplication
from qfluentwidgets import FluentTranslator, Theme

from ui import LoginUI, MainUI, MessageDisplay, InfoBarDisplay
from function.commonfunc import writePerclip
from client import Client

linkState = None

class ClientSubThread(QThread):
    """子线程"""
    # 信号必须在此定义
    state_socketObj_signal = pyqtSignal(list)
    state_token_signal = pyqtSignal(list)
    def __init__(self, action, **kwargs):
        """action
        0:link server
        1:login
        2:send message
        3:recive message"""
        super(ClientSubThread, self).__init__()
        self.kwargs = kwargs
        self.action = action
        if self.action == 0:
            address = self.kwargs["address"]
            tranAddress = (str(address[0]),int(address[1]))
            self.clientSocket = Client(*tranAddress)

        elif self.action == 1:
            self.sock = self.kwargs["sock"]
            self.username = self.kwargs["name"]
            self.userpassword = self.kwargs["password"]

    def run(self):
        if self.action == 0:
            try:
                self.clientSocket.connectServer()
                self.state_socketObj_signal.emit([self.clientSocket.clientstate, self.clientSocket])
            except (TypeError, ValueError, OSError, UnboundLocalError, ConnectionRefusedError, ConnectionError) as e:
                self.state_socketObj_signal.emit([False, e])

        elif self.action == 1:
            try:
                self.sock.userLogin(username = self.username, password = self.userpassword)
                self.state_token_signal.emit([self.sock.state_token])
            except (TypeError, ValueError, OSError, UnboundLocalError, ConnectionRefusedError, ConnectionError) as e:
                self.state_token_signal.emit([False, e])

class MainClient():
    """客户端主类"""
    def __init__(self):
        self.QtApp = QApplication(sys.argv)
        translator = FluentTranslator(QLocale())
        self.login_w = LoginUI()
        self.login_w.setLoginState(0)
        self.main_w = MainUI()
        self.QtApp.installTranslator(translator)
        self.__loginUI_setButtons()

    def __loginUI_showPublicKey(self, parent):
        """展示公钥"""
        title = 'The Public Key of the Server:'
        content = f"{self.client_socket_obj.public_key}"
        w = MessageDisplay(title, content, parent=parent, btndisplay=(False, True), btnText=("","OK"))
        if w.exec():
            pass

    def __loginUI_backToLinkPageFunction(self):
        self.login_w.setLoginState(0)
        self.client_socket_obj.close()
        InfoBarDisplay(self.login_w, type="info", whereis="TOP_LEFT", title="断开了与服务器的连接", infomation="")
        self.login_w.connectedServerLable.setVisible(False)
        self.login_w.connectedServerLable.setText("")
        print("Socket has been closed.")

    def __loginUI_setButtons(self):
        self.login_w.link_server_button.clicked.connect(lambda: self.loginUI_linkServerFunction(self.login_w.getServerAddess()))
        self.login_w.back_Button.clicked.connect(lambda: self.__loginUI_backToLinkPageFunction())
        self.login_w.login_Button.clicked.connect(lambda: self.loginUI_userLoginFunction(self.login_w.getUserAccount()))
        self.login_w.connectedServerLable.clicked.connect(lambda: self.__loginUI_showPublicKey(self.login_w))

    def __loginUI_checkLinkState(self, state_socket):
        """检测是否连接成功"""
        if state_socket[0]:
            InfoBarDisplay(self.login_w, type="info", whereis="TOP_LEFT", title="连接成功!", infomation="")
            self.client_socket_obj = state_socket[1] # 获取到socket_client对象
            self.login_w.setLoginState(1)
            self.login_w.connectedServerLable.setVisible(True)
            self.login_w.connectedServerLable.setText(f"已连接到 {self.serverAddress[0]}:{self.serverAddress[1]}")
            self.login_w.loadProgressBar.setVisible(False)

        elif not state_socket[0]:
            InfoBarDisplay(self.login_w, durationTime=5000, type="error", whereis="TOP_RIGHT", title="错误", infomation=f"{state_socket[1]}")
            print(f"{state_socket[1]}")
            self.login_w.loadProgressBar.setVisible(False)

    def __loginUI_checkLoginState(self, state_token):
        """检测登陆状态"""
        if state_token[0]:
            if state_token[0]["code"] == 0:
                # 同步主题
                if self.login_w.theme == Theme.DARK:
                    pass
                    self.main_w.setThemeState()
                    self.main_w.setThemeState()
                self.userToken = state_token[0]["token"]
                self.login_w.close()
                self.main_w.mainUI()
                InfoBarDisplay(self.main_w, type="info", whereis="TOP", title="登录成功!", infomation="")
            elif state_token[0]["code"] == 401:
                msg = state_token[0]["msg"]
                InfoBarDisplay(self.login_w, type="warn", whereis="TOP_LEFT", title="登陆失败。", infomation=f"密码错误:{msg}")                    
            # InfoBarDisplay(self.login_w, type="warn", whereis="TOP_LEFT", title="登陆超时", infomation="")
            elif not state_token[0]:
                InfoBarDisplay(self.main_w, type="error", whereis="TOP_LEFT", title="错误", infomation=f"{state_token[1]!s}")

    def loginUI_linkServerFunction(self, address):
        self.serverAddress = address
        if not address[0] or not address[1]:
            InfoBarDisplay(self.login_w, type="warn", whereis="TOP_LEFT", title="警告", infomation="地址不得为空")
        elif not isinstance(address[1], str):
            InfoBarDisplay(self.login_w, type="warn", whereis="TOP_LEFT", title="警告", infomation="地址格式有误")
        else:
            print("Connecting......")
            self.login_w.loadProgressBar.setVisible(True)
            self.linkServerThread = ClientSubThread(action=0, address=address)
            self.linkServerThread.start()
            self.linkServerThread.state_socketObj_signal.connect(self.__loginUI_checkLinkState)

    def loginUI_userLoginFunction(self, account):
        if not account[0] or not account[1]:
            InfoBarDisplay(self.login_w, type="warn", whereis="TOP_LEFT", title="警告", infomation="用户名或密码不得为空")
        else:
            print('Logining......')
            self.userLoginThread = ClientSubThread(action=1, sock=self.client_socket_obj, name=account[0], password=account[1])
            self.userLoginThread.start()
            self.userLoginThread.state_token_signal.connect(self.__loginUI_checkLoginState)

    def run(self):
        self.login_w.loginUI()
        # start Qt app
        self.QtApp.exec()
    
if __name__ == '__main__':
    ClientObject = MainClient()
    ClientObject.run()