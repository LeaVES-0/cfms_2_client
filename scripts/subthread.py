#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 9/7/2023 下午9:14
# @Author  : LeaVES
# @FileName: subthread.py
# coding: utf-8

from PyQt6.QtCore import QThread, pyqtSignal
from scripts.client import Client


class ClientSubThread(QThread):
    """子线程"""
    # 信号必须在此定义
    state_signal = pyqtSignal(dict)

    def __init__(self, action, **kwargs):
        """action
        0:link server
        1:login
        2:send message
        3:receive message"""
        super(ClientSubThread, self).__init__()
        self.kwargs = kwargs
        self.action = action
        if self.action == 0:
            address = self.kwargs["address"]
            self.tran_address = (str(address[0]), int(address[1]))
            self.clientSocket = Client()

        elif self.action == 1:
            self.sock = self.kwargs["sock"]
            self.username = self.kwargs["name"]
            self.user_password = self.kwargs["password"]

    def run(self):
        if self.action == 0:
            try:
                self.clientSocket.connect_cfms_server(*self.tran_address)
                self.state_signal.emit({"address": self.tran_address,
                                        "clientState": self.clientSocket.clientstate,
                                        "isSameKey": self.clientSocket.samePublicKey,
                                        "clientObj": self.clientSocket})
            except (TypeError, ValueError, OSError, UnboundLocalError, ConnectionRefusedError, ConnectionError) as e:
                self.state_signal.emit({"address": self.tran_address,
                                        "clientState": False,
                                        "isSameKey": self.clientSocket.samePublicKey,
                                        "error": e,
                                        "clientObj": self.clientSocket})
                print(e)
        elif self.action == 1:
            try:
                self.sock.cfms_user_login(username=self.username, password=self.user_password)
                self.state_signal.emit({"loginState": True, "recv": self.sock.recv_token})
            except (TimeoutError, TypeError, ValueError, OSError, ConnectionRefusedError, ConnectionError) as e:
                self.state_signal.emit({"loginState": False, "error": e})
                print(e)
