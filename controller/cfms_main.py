#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 10/7/2023 下午10:00
# @Author  : LeaVES
# @FileName: cfms_main.py
# coding: utf-8

import os
import sys
import time

from PyQt6.QtCore import *
from PyQt6.QtWidgets import QApplication
from qfluentwidgets import FluentTranslator, Theme

from controller.cfms_user import CfmsUserManager
from scripts.client_thread import ClientSubThread, ClientFtpThread
from scripts.method import info_message_display
from scripts.windows import LoginUI, MainUI, MessageDisplay


class MainClient:
    """客户端主类"""

    def __init__(self):
        self.sub_thread = ClientSubThread()
        self.usermanager = CfmsUserManager()
        self.QtApp = QApplication(sys.argv)
        self.login_w = LoginUI(thread=self.sub_thread)
        self.main_w = MainUI(functions={'get_files_function': self.get_dir_function,
                                        'rename_file_function': self.rename_file_function,
                                        'download_file_function': self.download_file_function,
                                        'delete_file_function': self.delete_file_function,
                                        'upload_new_file_function': self.upload_new_file_function},
                             thread=self.sub_thread)
        self.public_key = None
        self._is_cancel_link = False  # 是否取消连接的内部特性
        self.files_information = []
        translator = FluentTranslator(QLocale())
        self.login_w.setLoginState(0)
        self.QtApp.installTranslator(translator)

        self.__login_ui_set_buttons()
        server_items = [i[0] for i in self.usermanager.saved_servers]
        self.login_w.serverAdLE.addItems(server_items)
        self.login_w.serverAdLE.setCurrentIndex(0)

    def show_public_key_meg(self):
        title = 'The Public Key of the Server:'
        content = f"{self.public_key}"
        w = MessageDisplay(title, content, parent=self.login_w, btn_display=(False, True), btn_text=("", "OK"))
        w.exec()

    def __diff_public_key_meg(self):
        title = 'The Public Key of the Server:'
        content = f"""服务器上的公钥与本地不同,这可能意味着服务器已被重置。
但若非如此,则意味着您可能已遭受中间人攻击。
获取的服务器公钥:
{self.public_key}"""
        w = MessageDisplay(title, content, parent=self.login_w, btn_display=(True, True),
                           btn_text=("断开连接", "更换公钥"))
        if w.exec():
            self.close_connection_function()
        else:
            self.sub_thread.pem_file.write_pem_file(pem_content=self.public_key)
            info_message_display(object_name=self.login_w, information_type="info", title="公钥替换成功")
            self.close_connection_function()

    def close_connection_function(self):
        self.sub_thread.reset_sock()
        self.login_w.setLoginState(0)
        info_message_display(self.login_w, information_type="info", whereis="TOP_LEFT", title="断开了与服务器的连接")
        self.login_w.connectedServerLabel.setVisible(False)
        self.login_w.connectedServerLabel.setText("")

    def cancel_link(self):
        self._is_cancel_link = True
        self.sub_thread.reset_sock()
        info_message_display(self.login_w, information_type="info", whereis="TOP_LEFT", title="已取消", )

    def __login_ui_set_buttons(self):
        """login_ui buttons bind"""
        self.login_w.link_server_button.clicked.connect(lambda: self.link_server_function(
            self.login_w.getServerAddress()))
        self.login_w.back_Button.clicked.connect(lambda: self.close_connection_function())
        self.login_w.login_Button.clicked.connect(lambda: self.user_login_function(self.login_w.getUserAccount()))
        self.login_w.connectedServerLabel.clicked.connect(lambda: self.show_public_key_meg())
        self.login_w.link_cancel_button.clicked.connect(self.cancel_link)

    def __check_link_state(self, args: dict):
        """检测连接状态"""
        self.public_key = args["public_key"]
        state = args["clientState"]
        server_address = args["address"]
        if state:
            self.ftp_host = server_address[0]
            print(f"Server state: 0. \nLink successful.")
            info_message_display(self.login_w, information_type="info", whereis="TOP_LEFT", title="连接成功!")
            if args["isFirstTimeConnection"]:
                info_message_display(self.login_w, information_type="info", whereis="BUTTON_LEFT", title="注意",
                                     information="首次连接到该服务器，公钥已保存。")
            self.login_w.setLoginState(1)
            self.login_w.connectedServerLabel.setVisible(True)
            self.login_w.connectedServerLabel.setText(f"已连接到 {server_address[0]}:{server_address[1]}")
            self.login_w.loadProgressBar.stop()
            self.usermanager.remember_linked_server(address=list(server_address))  # 储存连接成功的服务器信息
            self.login_w.userNameLE.addItems(self.usermanager.saved_users)
            self.login_w.userNameLE.setCurrentIndex(0)

        else:
            self.login_w.link_server_button.setEnabled(True)
            self.login_w.link_cancel_button.setEnabled(False)
            self.login_w.loadProgressBar.stop()
            if not args["isSameKey"]:
                info_message_display(self.login_w, duration_time=1500, information_type="warn", whereis="TOP_RIGHT",
                                     title=" 公钥异常")
                self.__diff_public_key_meg()
            else:

                if not self._is_cancel_link:
                    info_message_display(self.login_w, duration_time=2000, information_type="error",
                                         whereis="TOP_RIGHT", title="错误", information=f"{args['error']}")
                self._is_cancel_link = False
        self.sub_thread.signal.disconnect(self.__check_link_state)  # 断开信号槽连接

    def __check_login_state(self, signal: dict):
        """检测登陆状态"""
        if signal["loginState"]:
            recv_from_server = signal["recv"]  # 服务器返回值
            if recv_from_server["code"] == 0:
                # 登录成功
                self.login_w.login_finished = True
                self.ftp_port = recv_from_server["ftp_port"]  # ftp 端口
                print("Login successful!")
                info_message_display(self.main_w, information_type="info", whereis="TOP",
                                     title="登录成功!", duration_time=1000)
                login_information = signal['account']  # 存有用户账户的元组
                # 同步主题
                if self.login_w.theme == Theme.DARK:
                    self.main_w.setThemeState()
                    self.main_w.setThemeState()
                user_token = recv_from_server["token"]  # 获取到token
                # 设置窗口
                self.login_w.close()
                # self.main_w.close()  # 正常情况无需先关闭，此处是为了ui debug模式考量
                self.main_w.mainUI()
                username = login_information[0]
                hashed_password = login_information[1]
                self.sub_thread.set_auth(user=username, token=user_token)
                if self.login_w.checkBox_remember_uer.isChecked():
                    # 是否保存密码
                    self.usermanager.remember_logined_user([username, hashed_password])
                else:
                    self.usermanager.remember_logined_user([username, None])

            elif recv_from_server["code"] == 401:
                # 登录失败, 密码错误
                msg = recv_from_server.get("msg", '')
                info_message_display(self.login_w, information_type="warn", whereis="TOP_LEFT", title="登陆失败。",
                                     information=f"密码错误:{msg!s}")
        elif not signal["loginState"]:
            # 其他异常
            info_message_display(self.login_w, information_type="error", whereis="TOP_LEFT", title="错误",
                                 information=f"{signal['error']!s}")
        self.sub_thread.signal.disconnect(self.__check_login_state)  # 不管登录成功与否,都断开信号槽连接

    def link_server_function(self, address: tuple):
        """连接服务器"""
        if not address[0] or not address[1]:
            info_message_display(self.login_w, information_type="warn", whereis="TOP_LEFT", title="警告",
                                 information="地址不得为空")
        elif not isinstance(address[1], str):
            info_message_display(self.login_w, information_type="warn", whereis="TOP_LEFT", title="警告",
                                 information="地址格式有误")
        else:
            self.login_w.link_server_button.setEnabled(False)
            self.login_w.link_cancel_button.setEnabled(True)
            self.login_w.loadProgressBar.start()
            print("Connecting......")
            try:
                self.sub_thread.signal.disconnect()  # 再次确认断开
            except TypeError:
                ...
            self.sub_thread.load_sub_thread(action=0, address=address)
            self.sub_thread.signal.connect(self.__check_link_state)
            self.sub_thread.start()

    def user_login_function(self, account: tuple):
        """登录"""
        if not account[0] or not account[1]:
            info_message_display(self.login_w, information_type="warn", whereis="TOP_LEFT", title="警告",
                                 information="用户名或密码不得为空")
        else:
            print('Logining......')
            self.sub_thread.load_sub_thread(action=1, name=account[0], password=account[1])
            self.sub_thread.signal.connect(self.__check_login_state)
            self.sub_thread.start()

    def get_dir_function(self, dir_id: str = None):
        self.current_dir_id = dir_id
        self.main_w.file_page.loadProgressBar.start()
        try:
            self.sub_thread.signal.disconnect()
        except TypeError:
            pass

        def transform_file_dict(recv: dict) -> tuple:
            """转化为列表并返回"""
            self.files_information = []
            del recv["code"]
            files_id = list(recv["dir_data"].keys())
            for index, i in enumerate(list(recv["dir_data"].values())):
                try:
                    time_string = time.strftime("%Y-%m-%d %H:%M:%S",
                                                time.localtime(i['properties']["created_time"]))
                except KeyError:
                    time_string = "Unknown"
                size_units = ["B", "KB", "MB", "GB", "TB", "PB"]
                size = "Unknown"
                try:
                    f_size = "Unknown"
                    size = int(i["properties"].get("size", "Unknown"))
                    for i_index in range(0, 6):
                        if size >= 1024:
                            size /= 1024
                        else:
                            round(size, 2)
                            f_size = f"{size!s} {size_units[i_index]}"
                            break
                except (ValueError, TypeError):
                    f_size = "Unknown"
                    # 名称|类型|大小|权限|原始大小|id
                file_info = {"name": i.get("name", "Untitled"), "type": i.get("type", "Unknown"),
                             "transformed_size": f_size, "create_time": time_string,
                             "permission": i.get("permission", "Unknown"), "primary_size": size,
                             "file_id": files_id[index]}
                if file_info["file_id"]:
                    self.files_information.append(file_info)
                for file in self.files_information:
                    if file["type"] == "dir":
                        file["transformed_size"] = ""
            return (self.files_information,)

        def get_recv(recv):
            self.sub_thread.signal.disconnect(get_recv)
            # _timer = threading.Timer(1, self.main_w.file_page.loadProgressBar.stop)
            # _timer.start()
            self.main_w.file_page.loadProgressBar.stop()
            if recv["state"]:
                if recv["recv"]["code"] == 0:
                    result = transform_file_dict(recv["recv"])
                    self.main_w.file_page.set_file_tree_list(result)
                    # _timer.start()
                elif recv["recv"]["code"] == 404:
                    # 失败 设置当前目录为前一次所处目录
                    if self.main_w.file_page.last_dir_path:
                        self.current_dir_id = self.main_w.file_page.last_dir_path[0]
                    else:
                        self.current_dir_id = None
                    self.main_w.file_page.current_path = self.main_w.file_page.last_dir_path
                    info_message_display(self.main_w, information_type="error", whereis="TOP_LEFT", title="错误",
                                         information="目录不存在")
                    # _timer.start()
            else:
                info_message_display(self.main_w, information_type="error", whereis="TOP_LEFT", title="错误",
                                     information=f"获取文件时出错{recv['error']}")
                # _timer.start()

        self.sub_thread.signal.connect(get_recv)
        if not dir_id:
            self.sub_thread.load_sub_thread(request="getRootDir", data={"action": "list"})
            self.sub_thread.start()
        else:
            self.sub_thread.load_sub_thread(request="operateDir", data={"action": "list", "dir_id": dir_id})
            self.sub_thread.start()

    def rename_file_function(self, data, file_id: str, obj_type: str):
        try:
            self.sub_thread.signal.disconnect()
        except TypeError:
            ...
        if obj_type == "dir":
            self.sub_thread.load_sub_thread(request="operateDir", data={"dir_id": file_id, "action": 'rename',
                                                                        'new_dirname': data})
        elif obj_type == "file":
            self.sub_thread.load_sub_thread(request="operateFile", data={"file_id": file_id, "action": 'rename',
                                                                         'new_filename': data})
        self.sub_thread.start()

    def delete_file_function(self, file_id: str, obj_type: str):
        try:
            self.sub_thread.signal.disconnect()
        except TypeError:
            ...

        def __get_recv(recv):
            self.sub_thread.signal.disconnect(__get_recv)
            self.get_dir_function(self.current_dir_id)
            return recv

        if obj_type == "dir":
            self.sub_thread.load_sub_thread(request="operateDir", data={"dir_id": file_id, "action": 'delete'})
        elif obj_type == "file":
            self.sub_thread.load_sub_thread(request="operateFile", data={"file_id": file_id, "action": 'delete'})
        self.sub_thread.start()
        self.sub_thread.signal.connect(__get_recv)

    def download_file_function(self, file_index: int):
        try:
            self.sub_thread.signal.disconnect()
        except TypeError:
            pass
        ftp_task = ClientFtpThread(address=(self.ftp_host, self.ftp_port))
        file = self.files_information[file_index]
        file_id = file['file_id']
        file_name = str(file['name'])
        file_size = int(file['primary_size'])

        def __ftp_respond(signal):  # 结果处理
            ftp_task.ftp_signal.disconnect()
            if not signal['state']:
                if signal["error"] == "FEE":
                    info_message_display(self.main_w, title="注意", information="文件已存在")
                else:
                    info_message_display(self.main_w, title="未知错误", information=signal["error"])

        def __get_recv(recv):
            self.sub_thread.signal.disconnect(__get_recv)
            if recv["state"]:
                if recv["recv"]["code"] == 0:
                    # task
                    task_id = recv["recv"]["data"]["task_id"]
                    task_token = recv["recv"]["data"]["task_token"]
                    ftp_file_names = recv["recv"]["data"]["t_filename"]  # ftp文件名(字典)
                    file_info = [(file_name, file_size)]  # file_info 每一项的1索引为文件大小, 0索引为文件名称
                    ftp_task.load_ftp_obj(action="download_file",
                                          args=(task_id, task_token, ftp_file_names, file_info, False))
                    ftp_task.ftp_signal.connect(__ftp_respond)
                    ftp_task.start()

        # send request
        self.sub_thread.load_sub_thread(2, request="operateFile", data={"action": "read", "file_id": file_id})
        self.sub_thread.signal.connect(__get_recv)
        self.sub_thread.start()

    def download_folder_function(self):
        ...

    def upload_new_file_function(self, file_path):
        try:
            self.sub_thread.signal.disconnect()
        except TypeError:
            pass
        ftp_task = ClientFtpThread(address=(self.ftp_host, self.ftp_port))
        file_name = str(os.path.basename(file_path))

        def __ftp_respond(signal):
            ftp_task.ftp_signal.disconnect(__ftp_respond)
            self.get_dir_function(self.current_dir_id)

        def __get_recv(recv):
            self.sub_thread.signal.disconnect(__get_recv)
            task_id = recv["recv"]["data"]["task_id"]
            task_token = recv["recv"]["data"]["task_token"]
            ftp_file_names = recv["recv"]["data"]["t_filename"]  # 要上传的ftp文件名(字典)
            ftp_task.load_ftp_obj(action="upload_new_file", args=(task_id, task_token, ftp_file_names, file_path))
            ftp_task.ftp_signal.connect(__ftp_respond)
            ftp_task.start()

        self.sub_thread.signal.connect(__get_recv)
        self.sub_thread.load_sub_thread(2, request="createFile",
                                        data={"directory_id": (self.current_dir_id if self.current_dir_id else ''),
                                              "filename": file_name})
        self.sub_thread.start()

    def upload_file_function(self):
        ...

    def upload_folder_function(self):
        ...

    def run(self, debug: bool = False):
        self.login_w.loginUI()
        if debug:
            self.main_w.mainUI()
        # start Qt app
        self.QtApp.exec()
