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
from qfluentwidgets import FluentTranslator

from controller.cfms_user import CfmsUserManager
from scripts.client_thread import ClientSubThread, ClientFtpTask
from scripts.fileio import FtpFilesManager
from scripts.method import info_message_display, FILE_TYPES
from scripts.windows import LoginUI, MainUI, MessageDisplay


class MainClient:
    """客户端主类"""

    def __init__(self):
        self.sub_thread = ClientSubThread()
        self.usermanager = CfmsUserManager()
        self.QtApp = QApplication(sys.argv)
        self.QtApp.setAttribute(Qt.ApplicationAttribute.AA_DontCreateNativeWidgetSiblings)
        self.login_w = LoginUI(thread=self.sub_thread)
        self.main_w = MainUI(functions={'get_files_function': self.get_dir_function,
                                        'rename_file_function': self.rename_file_function,
                                        'download_file_function': self.download_file_function,
                                        'delete_file_function': self.delete_file_function,
                                        'upload_file_function': self.upload_file_function,
                                        'create_new_dir_function': self.create_new_dir_function},
                             thread=self.sub_thread)
        translator = FluentTranslator(QLocale())
        self.login_w.setLoginState(0)
        self.QtApp.installTranslator(translator)

        self.public_key = None
        self._is_cancel_link = False  # 是否取消连接的内部特性
        self._force_save_user_account = False
        self.files_information = []
        self.tasks = []

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
        self.login_w.back_Button_2.clicked.connect(lambda: self.close_connection_function())

    def __check_link_state(self, args: dict):
        """检测连接状态"""
        self.public_key = args.get("public_key", '')
        state = args["clientState"]
        server_address = args["address"]
        self.login_w.loadProgressBar.stop()
        self.login_w.link_server_button.setEnabled(True)
        self.login_w.link_cancel_button.setEnabled(False)
        if state:
            self.ftp_host = server_address[0]
            self.usermanager.remember_linked_server(address=server_address)  # 储存连接成功的服务器信息
            print(f"Server state: 0. \nLink successful.")
            info_message_display(self.login_w, information_type="info", whereis="TOP_LEFT", title="连接成功!")
            if args["isFirstTimeConnection"]:
                info_message_display(self.login_w, information_type="info", whereis="BUTTON_LEFT", title="注意",
                                     information="首次连接到该服务器，公钥已保存。")
            self.login_w.connectedServerLabel.setVisible(True)
            self.login_w.connectedServerLabel.setText(f"已连接到 {server_address[0]}:{server_address[1]}")
            saved_users = self.usermanager.saved_users
            last_login_password = None
            for u in saved_users[0]:
                if u[0] == saved_users[1]:
                    last_login_password = u[1]
                    break

            def logout():
                self.usermanager.remember_logined_user((saved_users[1], None))
                self.login_w.checkBox_remember_uer.setChecked(False)
                self.login_w.setLoginState(1)

            if saved_users[1] and last_login_password:
                self.login_w.show_user_name.setText(f"User: {saved_users[1]}")
                self.login_w.login_directly_button.clicked.connect(
                    lambda: self.user_login_function((saved_users[1], last_login_password), True))
                self.login_w.login_out_Button.clicked.connect(lambda: logout())
                self._force_save_user_account = True
                self.login_w.setLoginState(2)
            else:
                self.login_w.setLoginState(1)
                if saved_users[0]:
                    display_users = [u[0] for u in saved_users[0]]
                    self.login_w.userNameLE.addItems(display_users)
                    self.login_w.userNameLE.setCurrentIndex(0)

        else:
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
        self.login_w.loadProgressBar.stop()
        self.login_w.login_Button.setEnabled(True)
        self.login_w.back_Button.setEnabled(True)
        if signal["loginState"]:
            recv_from_server = signal["recv"]  # 服务器返回值
            if recv_from_server["code"] == 0:
                # 登录成功
                self.login_w.login_finished = True
                self.ftp_port = recv_from_server["ftp_port"]  # ftp 端口
                print("Login successful!")
                # 设置窗口
                self.login_w.close()
                # 同步主题
                self.main_w.interface_theme = self.login_w.interface_theme
                self.main_w.mainUI()
                info_message_display(self.main_w, information_type="info", whereis="TOP_RIGHT",
                                     title="登录成功!", duration_time=2000)

                login_information = signal['account']  # 存有用户账户的元组
                user_token = recv_from_server["token"]  # 获取到token
                username = login_information[0]
                hashed_password = login_information[1]
                self.sub_thread.set_auth(user=username, token=user_token)
                if self.login_w.checkBox_remember_uer.isChecked() or self._force_save_user_account:
                    # 是否保存密码
                    self.usermanager.remember_logined_user((username, hashed_password))
                else:
                    self.usermanager.remember_logined_user((username, None))
                self._force_save_user_account = False
                self.login_w.checkBox_remember_uer.setChecked(False)

            elif recv_from_server["code"] == 401:
                # 登录失败, 密码错误
                msg = recv_from_server.get("msg", '')
                info_message_display(self.login_w, information_type="warn", whereis="TOP_RIGHT", title="登陆失败。",
                                     information=f"密码错误:{msg!s}")
        elif not signal["loginState"]:
            # 其他异常
            info_message_display(self.login_w, information_type="error", whereis="TOP_RIGHT", title="错误",
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

    def user_login_function(self, account: tuple, hashed: bool = False):
        """登录"""
        if not account[0] or not account[1]:
            info_message_display(self.login_w, information_type="warn", whereis="TOP_RIGHT", title="警告",
                                 information="用户名或密码不得为空")
        else:
            print('Logining......')
            self.login_w.loadProgressBar.start()  # 禁用按键,开启进度条
            self.login_w.login_Button.setEnabled(False)
            self.login_w.back_Button.setEnabled(False)
            self.sub_thread.load_sub_thread(action=1, name=account[0], password=account[1], hashed=hashed)
            self.sub_thread.signal.connect(self.__check_login_state)
            self.sub_thread.start()

    def check_signal_recv(self, signal):
        if signal["state"]:
            return signal
        else:
            error = signal["error"]
            if type(error) == ValueError:
                info_message_display(self.main_w, information_type="error", whereis="TOP_LEFT", title="Server error",
                                     information=f"服务器错误:{error!s}")
            return None

    def get_dir_function(self, dir_id: str = ''):
        self.current_dir_id = dir_id
        self.main_w.file_page.loadProgressBar.start()
        try:
            self.sub_thread.signal.disconnect()
        except TypeError:
            pass
        self.files_information = []

        def transform_file_dict(recv: dict) -> list:
            """转化为列表并返回"""
            del recv["code"]
            files_id = list(recv["dir_data"].keys())
            parent_dir_id = ''
            size_units = ("B", "KB", "MB", "GB", "TB", "PB")
            for index, i in enumerate(list(recv["dir_data"].values())):
                try:
                    time_string = time.strftime("%Y-%m-%d %H:%M:%S",
                                                time.localtime(i['properties']["created_time"]))
                except KeyError:
                    time_string = "Unknown"
                file_type = i.get("type", "Unknown")
                primary_size = display_size = int(i["properties"].get("size", 0))
                for i_index in range(0, 6):
                    if display_size < 0:
                        display_size = "Unavailable"
                        break
                    if display_size >= 1024:
                        display_size /= 1024
                    else:
                        display_size = f"{display_size:.2f} {size_units[i_index]}"
                        break
                file_name = i.get("name", "Untitled")
                if file_type == "file":
                    suffix = os.path.splitext(file_name)[-1].strip(".").lower()
                    specific_file_type = FILE_TYPES.get(suffix, suffix + " File")
                elif file_type == "dir":
                    specific_file_type = "File folder"
                    primary_size = None
                    display_size = "---"
                else:
                    specific_file_type = "Unknown"
                file_info = {"name": file_name,
                             "type": file_type,
                             "specific_type": specific_file_type,
                             "size_transformed": display_size,
                             "primary_size": primary_size,
                             "time_created": time_string,
                             "permission": i.get("permission", "Unknown"),
                             "file_id": files_id[index]}
                if i.get("parent", False):
                    parent_dir_id = files_id[index]
                else:
                    self.files_information.append(file_info)
            for en, i in enumerate(self.files_information):
                i["parent_id"] = parent_dir_id
            return self.files_information

        def get_recv(signal):
            self.sub_thread.signal.disconnect(get_recv)
            recv = self.check_signal_recv(signal)
            if recv:
                if recv["recv"]["code"] == 0:
                    result = transform_file_dict(recv["recv"])
                    self.main_w.file_page.set_file_tree_list(result)

                elif recv["recv"]["code"] == 404:
                    # 失败 设置当前目录为前一次所处目录
                    self.current_dir_id = self.main_w.file_page.last_dir_path[0]
                    self.main_w.file_page.current_path = self.main_w.file_page.last_dir_path
                    info_message_display(self.main_w, information_type="error", whereis="TOP_LEFT", title="错误",
                                         information="目录不存在")
                else:
                    info_message_display(self.main_w, information_type="error", whereis="TOP_LEFT", title="未知错误")

        self.sub_thread.signal.connect(get_recv)
        if not dir_id:
            self.sub_thread.load_sub_thread(request="getRootDir")
            self.sub_thread.start()
        else:
            self.sub_thread.load_sub_thread(request="operateDir", data={"action": "list", "dir_id": dir_id})
            self.sub_thread.start()

    # file_index 是文件在self.files_information中的索引

    def create_new_dir_function(self, data: str = None):
        try:
            self.sub_thread.signal.disconnect()
        except TypeError:
            ...

        def __get_recv(signal):
            self.sub_thread.signal.disconnect(__get_recv)
            recv = self.check_signal_recv(signal)
            if recv:
                self.get_dir_function(self.current_dir_id)

        if not data:
            data = "New Folder " + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
        self.sub_thread.load_sub_thread(request="createDir", data={"parent_id": self.current_dir_id, "name": data})
        self.sub_thread.signal.connect(__get_recv)
        self.sub_thread.start()

    def rename_file_function(self, data: str, file_index: int):
        try:
            self.sub_thread.signal.disconnect()
        except TypeError:
            ...
        obj_type = self.files_information[file_index]["type"]
        file_id = self.files_information[file_index]["file_id"]

        def __get_recv(signal):
            self.sub_thread.signal.disconnect(__get_recv)
            recv = self.check_signal_recv(signal)
            if recv:
                ...
        if obj_type == "dir":
            self.sub_thread.load_sub_thread(request="operateDir", data={"dir_id": file_id, "action": 'rename',
                                                                        'new_dirname': data})
        elif obj_type == "file":
            self.sub_thread.load_sub_thread(request="operateFile", data={"file_id": file_id, "action": 'rename',
                                                                         'new_filename': data})
        self.sub_thread.signal.connect(__get_recv)
        self.sub_thread.start()

    def delete_file_function(self, file_index: int):
        try:
            self.sub_thread.signal.disconnect()
        except TypeError:
            ...
        obj_type = self.files_information[file_index]["type"]
        file_id = self.files_information[file_index]["file_id"]

        def __get_recv(signal):
            self.sub_thread.signal.disconnect(__get_recv)
            recv = self.check_signal_recv(signal)
            if recv:
                self.get_dir_function(self.current_dir_id)

        if obj_type == "dir":
            self.sub_thread.load_sub_thread(request="operateDir", data={"dir_id": file_id, "action": 'delete'})
        elif obj_type == "file":
            self.sub_thread.load_sub_thread(request="operateFile", data={"file_id": file_id, "action": 'delete'})
        self.sub_thread.signal.connect(__get_recv)
        self.sub_thread.start()

    def download_file_function(self, file_index: int):
        try:
            self.sub_thread.signal.disconnect()
        except TypeError:
            pass
        file = self.files_information[file_index]

        ftp_file_io = FtpFilesManager()
        file_name = str(file['name'])
        file_size = int(file['primary_size'])
        result = ftp_file_io.load_file(FtpFilesManager.WRITE, file_name, file_size)

        ftp_task = ClientFtpTask((self.ftp_host, self.ftp_port), ClientFtpTask.DOWNLOAD_FILE)

        def __ftp_respond(signal):  # 结果处理
            try:
                ftp_task.ftp_signal.disconnect()
            except TypeError:
                ...
            if not signal['state']:
                if signal["error"] == "FEE":
                    info_message_display(self.main_w, title="注意", information="文件已存在")
                else:
                    info_message_display(self.main_w, title="未知错误", information=str(signal["error"]))

        def __get_recv(signal):
            self.sub_thread.signal.disconnect(__get_recv)
            recv = self.check_signal_recv(signal)
            if recv:
                if recv["recv"]["code"] == 0:
                    # task
                    task_id = recv["recv"]["data"]["task_id"]
                    task_token = recv["recv"]["data"]["task_token"]
                    ftp_file_names = recv["recv"]["data"]["t_filename"]  # ftp文件名(字典)
                    ftp_file_name = list(ftp_file_names.values())[0]
                    ftp_task.load_task(task_id, task_token, ftp_file_io, ftp_file_name)

                    ftp_task.ftp_signal.connect(__ftp_respond)
                    ftp_task.start()

        # send request
        if result["state"]:
            self.sub_thread.load_sub_thread(2, request="operateFile",
                                            data={"action": "read", "file_id": file['file_id']})
            self.sub_thread.signal.connect(__get_recv)
            self.sub_thread.start()
        else:
            __ftp_respond({"state": False, "error": result["error"]})

    def download_folder_function(self):
        ...

    def upload_file_function(self, file_path: str):
        """上传文件"""
        try:
            self.sub_thread.signal.disconnect()
        except TypeError:
            pass
        ftp_file_io = FtpFilesManager()
        file_size = int(os.path.getsize(file_path))
        result = ftp_file_io.load_file(FtpFilesManager.READ, file_path, file_size)

        ftp_task = ClientFtpTask((self.ftp_host, self.ftp_port), ClientFtpTask.UPLOAD_FILE)

        def __ftp_respond(signal):
            try:
                ftp_task.ftp_signal.disconnect()
            except TypeError:
                ...
            if not signal['state']:
                info_message_display(self.main_w, title="未知错误", information=signal["error"])
            self.get_dir_function(self.current_dir_id)

        def __get_recv(signal):
            self.sub_thread.signal.disconnect(__get_recv)
            recv = self.check_signal_recv(signal)
            if recv:
                if recv["recv"]['code'] == 0:
                    task_id = recv["recv"]["data"]["task_id"]
                    task_token = recv["recv"]["data"]["task_token"]
                    ftp_file_names = recv["recv"]["data"]["t_filename"]  # ftp文件名(字典)
                    ftp_file_name = list(ftp_file_names.values())[0]
                    ftp_task.load_task(task_id, task_token, ftp_file_io, ftp_file_name)
                    ftp_task.ftp_signal.connect(__ftp_respond)
                    ftp_task.start()
                if recv["recv"]['code'] == -1:
                    info_message_display(self.main_w, information_type="warn", title="注意", information="文件被占用")

        file_name = str(os.path.basename(file_path))
        file_names = [f["name"] for f in self.files_information]

        if result["state"]:
            self.sub_thread.signal.connect(__get_recv)
            if not (file_name in file_names):
                self.sub_thread.load_sub_thread(2, request="createFile",
                                                data={"directory_id": self.current_dir_id,
                                                      "filename": file_name})
            elif file_name in file_names:
                file_id = self.files_information[file_names.index(file_name)]["file_id"]
                self.sub_thread.load_sub_thread(2, request="operateFile",
                                                data={"action": "write", "file_id": file_id})
            self.sub_thread.start()
        else:
            __ftp_respond({"state": False, "error": result["error"]})

    def upload_folder_function(self):
        ...

    def run(self, debug: bool = False):
        self.login_w.loginUI()
        if debug:
            self.main_w.mainUI()
        # start Qt app
        self.QtApp.exec()
