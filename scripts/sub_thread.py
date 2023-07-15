#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 9/7/2023 下午9:14
# @Author  : LeaVES
# @FileName: sub_thread.py
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
        self.action = action
        if self.action == 0:
            address = kwargs["address"]
            self.tran_address = (str(address[0]), int(address[1]))
            self.clientSocket = Client()

        elif self.action == 1:
            self.sock = kwargs["sock"]
            self.username = kwargs["name"]
            self.user_password = kwargs["password"]

        elif self.action == 2:
            self.sock = kwargs["sock"]
            self.request = kwargs["request"]
            self.data = kwargs["data"]

    def run(self):
        if self.action == 0:
            try:
                self.clientSocket.connect_cfms_server(*self.tran_address)
                self.state_signal.emit({"address": self.tran_address,
                                        "clientState": self.clientSocket.client_state,
                                        "isSameKey": self.clientSocket.samePublicKey,
                                        "clientObj": self.clientSocket,
                                        "isFirstTimeConnection": self.clientSocket.first_time_connection})
            except (TypeError, ValueError, OSError, UnboundLocalError, ConnectionRefusedError, ConnectionError) as e:
                self.state_signal.emit({"address": self.tran_address,
                                        "clientState": False,
                                        "isSameKey": self.clientSocket.samePublicKey,
                                        "error": e,
                                        "clientObj": self.clientSocket})
                print(e)
        elif self.action == 1:
            try:
                recv, account = self.sock.cfms_user_login(username=self.username, password=self.user_password)
                self.state_signal.emit({"loginState": True, "recv": recv, "account": account})
                # recv_token为从cfms_user_login获取到的服务器相应数据和登录原始数据
            except (TimeoutError, TypeError, ValueError, OSError, ConnectionRefusedError, ConnectionError) as e:
                self.state_signal.emit({"loginState": False, "error": e})
                print(e)
        elif self.action == 2:
            try:
                self.sock.cfms_send_request(request=self.request, data=self.data)

            except (TimeoutError, TypeError, ValueError, OSError, ConnectionRefusedError, ConnectionError) as e:

