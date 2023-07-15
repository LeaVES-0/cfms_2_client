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
from scripts.sub_thread import ClientSubThread
from scripts.windows import LoginUI, MainUI, MessageDisplay, info_message_display


class MainClient:
    """客户端主类"""

    def __init__(self):
        self.usermanager = CfmsUserManager()
        self.QtApp = QApplication(sys.argv)
        translator = FluentTranslator(QLocale())
        self.login_w = LoginUI()
        self.login_w.setLoginState(0)
        self.main_w = MainUI()
        self.request_thread = ClientSubThread(2)
        self.QtApp.installTranslator(translator)
        self.__login_ui_set_buttons()

    def show_public_key_meg(self):
        title = 'The Public Key of the Server:'
        content = f"{self.client_socket_obj.public_key}"
        w = MessageDisplay(title, content, parent=self.login_w, btn_display=(False, True), btn_text=("", "OK"))
        w.exec()

    def __diff_public_key_meg(self):
        title = 'The Public Key of the Server:'
        content = f"""服务器上的公钥与本地不同,这可能意味着服务器已被重置。
但若非如此,则意味着您可能已遭受中间人攻击。
获取的服务器公钥:
{self.client_socket_obj.public_key}"""
        w = MessageDisplay(title, content, parent=self.login_w, btn_display=(True, True),
                           btn_text=("断开连接", "更换公钥"))
        if w.exec():
            self.close_connection_function(True)
        else:
            self.client_socket_obj.pem_file.write_pem_file(pem_content=self.client_socket_obj.public_key)
            info_message_display(object_name=self.login_w, information_type="info", title="公钥替换成功")

    def close_connection_function(self, directly=False):
        self.login_w.setLoginState(0)
        self.client_socket_obj.close_connection(directly)
        info_message_display(self.login_w, information_type="info", whereis="TOP_LEFT", title="断开了与服务器的连接")
        self.login_w.connectedServerLabel.setVisible(False)
        self.login_w.connectedServerLabel.setText("")

    def __login_ui_set_buttons(self):
        """login_ui buttons bind"""
        self.login_w.link_server_button.clicked.connect(
            lambda: self.link_server_function(self.login_w.getServerAddress()))
        self.login_w.back_Button.clicked.connect(lambda: self.close_connection_function())
        self.login_w.login_Button.clicked.connect(lambda: self.user_login_function(self.login_w.getUserAccount()))
        self.login_w.connectedServerLabel.clicked.connect(lambda: self.show_public_key_meg())

    def __check_link_state(self, args):
        """检测连接状态"""
        state = args["clientState"]
        server_address = args["address"]
        self.client_socket_obj = args['clientObj']  # 获取到clientObj对象
        if state:
            info_message_display(self.login_w, information_type="info", whereis="TOP_LEFT", title="连接成功!")
            if args["isFirstTimeConnection"]:
                info_message_display(self.login_w, information_type="info", whereis="BUTTON_LEFT", title="注意",
                                     information="首次登录到该服务器，公钥已保存。")
            self.login_w.setLoginState(1)
            self.login_w.connectedServerLabel.setVisible(True)
            self.login_w.connectedServerLabel.setText(f"已连接到 {server_address[0]}:{server_address[1]}")
            self.login_w.loadProgressBar.setVisible(False)
            self.usermanager.remember_linked_server(address=list(server_address))

        else:
            if not args["isSameKey"]:
                self.login_w.loadProgressBar.setVisible(False)
                info_message_display(self.login_w, duration_time=6000, information_type="warn", whereis="TOP_RIGHT",
                                     title=" 公钥异常")
                self.__diff_public_key_meg()
            else:
                info_message_display(self.login_w, duration_time=5000, information_type="error", whereis="TOP_RIGHT",
                                     title="错误",
                                     information=f"{args['error']}")
                self.login_w.loadProgressBar.setVisible(False)

    def __check_login_state(self, signal):
        """检测登陆状态"""
        if signal["loginState"]:
            recv_from_server = signal["recv"]  # 服务器返回值
            if recv_from_server["code"] == 0:
                # 登录成功
                login_information = signal['account']  # 存有用户账户的元组
                # 同步主题
                if self.login_w.theme == Theme.DARK:
                    self.main_w.setThemeState()
                    self.main_w.setThemeState()
                user_token = recv_from_server["token"]  # 获取到token
                self.client_socket_obj.set_token(user_token)
                # 设置窗口
                self.login_w.close()
                # self.main_w.close()  # 正常情况无需先关闭，此处是为了ui debug模式考量
                self.main_w.mainUI()
                username = login_information[0]
                hashed_password = login_information[1]
                if self.login_w.checkBox_remember_uer.isChecked():
                    # 是否保存密码
                    self.usermanager.remember_logined_user([username, hashed_password])
                else:
                    self.usermanager.remember_logined_user([username, None])
                info_message_display(self.main_w, information_type="info", whereis="TOP", title="登录成功!",
                                     information="")
            elif recv_from_server["code"] == 401:
                # 登录失败, 密码错误
                msg = recv_from_server["msg"]
                info_message_display(self.login_w, information_type="warn", whereis="TOP_LEFT", title="登陆失败。",
                                     information=f"密码错误:{msg!s}")
        elif not signal["loginState"]:
            # 其他异常
            info_message_display(self.main_w, information_type="error", whereis="TOP_LEFT", title="错误",
                                 information=f"{signal['error']!s}")

    def link_server_function(self, address):
        if not address[0] or not address[1]:
            info_message_display(self.login_w, information_type="warn", whereis="TOP_LEFT", title="警告",
                                 information="地址不得为空")
        elif not isinstance(address[1], str):
            info_message_display(self.login_w, information_type="warn", whereis="TOP_LEFT", title="警告",
                                 information="地址格式有误")
        else:
            print("Connecting......")
            self.login_w.loadProgressBar.setVisible(True)
            self.link_server_thread = ClientSubThread(action=0, address=address)
            self.link_server_thread.state_signal.connect(self.__check_link_state)
            self.link_server_thread.start()

    def user_login_function(self, account):
        if not account[0] or not account[1]:
            info_message_display(self.login_w, information_type="warn", whereis="TOP_LEFT", title="警告",
                                 information="用户名或密码不得为空")
        else:
            print('Logining......')
            self.user_login_thread = ClientSubThread(action=1, sock=self.client_socket_obj, name=account[0],
                                                     password=account[1])
            self.user_login_thread.state_signal.connect(self.__check_login_state)
            self.user_login_thread.start()

    def get_file_list(self):
        pass

    def get_file_list_dir(self):
        self.client_socket_obj.cfsm_get_dir()

    def run(self, debug: bool = False):
        self.login_w.loginUI()
        if debug:
            self.main_w.mainUI()
        # start Qt app
        self.QtApp.exec()
