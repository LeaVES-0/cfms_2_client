#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 18/6/2023 下午5:24
# @Author  : LeaVES
# @FileName: Main.py
# coding: utf-8

import sys

from PyQt6.QtCore import QLocale, QThread, pyqtSignal
from PyQt6.QtWidgets import QApplication
from qfluentwidgets import FluentTranslator

from ui import LoginUI, MainUI, InfoBarDisplay
from client import Client

linkState = None

class LinkThread(QThread):
    data_signal = pyqtSignal(dict)

    def __init__(self, address):
        super(LinkThread, self).__init__()
        self.address = address
        tranAddress = (str(self.address[0]),int(self.address[1]))
        self.clientSocket = Client(*tranAddress)

    def run(self):
        try:
            self.clientSocket.connectServer()
            self.data_signal.emit(self.clientSocket.clientstate)
        except (TypeError, ValueError, OSError, UnboundLocalError) as e:
            self.data_signal.emit({'errorcode': e})
 
        
class MainClient():
    def __init__(self):
        self.QtApp = QApplication(sys.argv)
        translator = FluentTranslator(QLocale())
        self.QtApp.installTranslator(translator)
    
        self.login_w = LoginUI()

    def linkServerFunction(self,address):
        def isSuccess(state):
            if state["errorcode"] == 300:
                InfoBarDisplay(self.login_w, type="info", whereis="TOP", title="连接成功!", infomation="")
                self.login_w.setLoginState(1)
                
            else:
                InfoBarDisplay(self.login_w, type="error", whereis="TOP", title="错误", infomation=f"{state}")
        if not address[0] or not address[1]:
            InfoBarDisplay(self.login_w, type="warn", whereis="TOP", title="警告", infomation="地址不得为空")
        elif not isinstance(address[1], str):
            print(isinstance(address[1], int))
            InfoBarDisplay(self.login_w, type="warn", whereis="TOP", title="警告", infomation="地址格式有误")
        else:
            print(1)
            self.linkThread = LinkThread(address)
            self.linkThread.start()
            self.linkThread.data_signal.connect(isSuccess)
            
    def backAct(self):
        self.login_w.setLoginState(0)
        self.clientSocket.clientClose()
        print("Socket has been closed.")

    def main(self):

        self.login_w.setLoginState(0)
        self.login_w.loginUI()
        self.login_w.link_server_button.clicked.connect(lambda: self.linkServerFunction(self.login_w.getServerAddess()))
        self.login_w.back_Button.clicked.connect(lambda: self.backAct())
        # 启动Qt应用程序
        self.QtApp.exec()
    
if __name__ == '__main__':
    ClientObject = MainClient()
    ClientObject.main()