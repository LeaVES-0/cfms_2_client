#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 18/6/2023 下午5:24
# @Author  : LeaVES
# @FileName: Main.py
# coding: utf-8

import sys, socket

from PyQt6.QtCore import QLocale, QThread, pyqtSignal
from PyQt6.QtWidgets import QApplication
from qfluentwidgets import FluentTranslator

from ui import LoginUI, MainUI, InfoBarDisplay
from client import Client

linkState = None

class LinkServerThread(QThread):
    """连接服务器子线程"""
    state_socketObj_signal = pyqtSignal(list)

    def __init__(self, address):
        super(LinkServerThread, self).__init__()
        self.address = address
        tranAddress = (str(self.address[0]),int(self.address[1]))
        self.clientSocket = Client(*tranAddress)

    def run(self):
        try:
            self.clientSocket.connectServer()
            self.state_socketObj_signal.emit([self.clientSocket.clientstate, self.clientSocket])
        except (TypeError, ValueError, OSError, UnboundLocalError, ConnectionRefusedError, ConnectionError) as e:
            self.state_socketObj_signal.emit([False,e])

class MainClient():
    def __init__(self):
        self.QtApp = QApplication(sys.argv)
        translator = FluentTranslator(QLocale())
        self.QtApp.installTranslator(translator)
    
        self.login_w = LoginUI()
        self.main_w = MainUI()

    def __linkisSuccess(self, state_socket):
        if state_socket[0]:
            InfoBarDisplay(self.login_w, type="info", whereis="TOP", title="连接成功!", infomation="")
            self.client_socket_obj = state_socket[1]
            self.login_w.setLoginState(1)
        elif not state_socket[0]:
            InfoBarDisplay(self.login_w, type="error", whereis="TOP_RIGHT", title="错误", infomation=f"{state_socket[1]}")

    def linkServerFunction(self,address):
        if not address[0] or not address[1]:
            InfoBarDisplay(self.login_w, type="warn", whereis="TOP_RIGHT", title="警告", infomation="地址不得为空")
        elif not isinstance(address[1], str):
            print(isinstance(address[1], int))
            InfoBarDisplay(self.login_w, type="warn", whereis="TOP_RIGHT", title="警告", infomation="地址格式有误")
        else:
            print("Connecting......")
            self.linkServerThread = LinkServerThread(address)
            self.linkServerThread.start()
            self.linkServerThread.state_socketObj_signal.connect(self.__linkisSuccess)

    def userLoginFunction(self, account):
        self.client_socket_obj.userLogin(*account)
        print(self.client_socket_obj.state_token)
        if self.client_socket_obj.state_token == "time out":
            InfoBarDisplay(self.login_w, type="warn", whereis="TOP", title="登陆超时", infomation="")
        elif self.client_socket_obj.state_token["code"] == 0:
            self.token = self.client_socket_obj.state_token["token"]
            self.login_w.close()
            self.main_w.mainUI()
            InfoBarDisplay(self.main_w, type="info", whereis="TOP", title="登陆成功!", infomation="")
        elif self.client_socket_obj.state_token["code"] == 401:
            msg = self.client_socket_obj.state_token["msg"]
            InfoBarDisplay(self.login_w, type="warn", whereis="TOP", title="登陆失败。", infomation=f"{msg}")

    def backAct(self):
        self.login_w.setLoginState(0)
        self.client_socket.close()
        print("Socket has been closed.")

    def main(self):
        self.login_w.setLoginState(0)
        self.login_w.loginUI()
        self.login_w.link_server_button.clicked.connect(lambda: self.linkServerFunction(self.login_w.getServerAddess()))
        self.login_w.back_Button.clicked.connect(lambda: self.backAct())
        self.login_w.login_Button.clicked.connect(lambda: self.userLoginFunction(self.login_w.getUserAccount()))
        # 启动Qt应用程序
        self.QtApp.exec()
    
if __name__ == '__main__':
    ClientObject = MainClient()
    ClientObject.main()