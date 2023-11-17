#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 10/7/2023 下午10:00
# @Author  : LeaVES
# @FileName: cfms_main.py
# coding: utf-8

import hashlib
import os
import sys
import time

from PyQt6.QtCore import *
from PyQt6.QtWidgets import QApplication
from qfluentwidgets import FluentTranslator, Theme

from controller.cfms_user import CfmsUserManager
from util.cfms_network import ClientSubThread, ClientFtpTask, DEFAULT_PORT
from util.cfms_fileIO import FtpFilesManager
from util.cfms_common import FILE_TYPES
from util.uie.elements import info_message_display, MessageDisplay
from util.cfms_ui import LoginUI, MainUI


class MainClient(QObject):
    """客户端主类"""

    def __init__(self):
        super().__init__()
        self.sub_thread = ClientSubThread()
        self.user_manager = CfmsUserManager()
        self.QtApp = QApplication(sys.argv)
        self.QtApp.setAttribute(Qt.ApplicationAttribute.AA_DontCreateNativeWidgetSiblings)
        self.login_w = LoginUI(thread=self.sub_thread)
        self.main_w = MainUI(thread=self.sub_thread)
        translator = FluentTranslator(QLocale())
        self.login_w.setLoginPage(0)
        self.QtApp.installTranslator(translator)

        self.public_key = None
        self._is_cancel_link = False  # 是否取消连接的内部特性
        self._force_save_user_account = False
        self.files_information = []
        self.tasks = []
        self.current_dir_id = ''

        self.__login_ui_signal_solts_connect()
        self.login_w.add_server_list([_[0] for _ in self.user_manager.saved_servers])
        self.__main_ui_signal_solts_connect()

    def close_connection(self):
        self.sub_thread.reset_sock()
        self.login_w.setLoginPage(0)
        info_message_display(self.login_w, information_type="info", whereis="TOP_RIGHT", title="断开了与服务器的连接")

    def cancel_link(self):
        self._is_cancel_link = True
        self.sub_thread.reset_sock()
        info_message_display(self.login_w, information_type="info", whereis="TOP_RIGHT", title="已取消", )

    def __login_ui_signal_solts_connect(self):
        """login_ui buttons bind"""
        self.login_w.actions_connector("link", lambda: self.link_server_function(self.login_w.getServerAddress()))
        self.login_w.actions_connector("cancel", self.close_connection)
        self.login_w.actions_connector("login", lambda: self.user_login_function(self.login_w.getUserAccount()))
        self.login_w.actions_connector("show_connected_server_info",
                                       lambda: self.login_w.show_public_key_meg(self.public_key))
        self.login_w.actions_connector("cancel", self.cancel_link)
        self.login_w.actions_connector("back", self.close_connection)

    def __main_ui_signal_solts_connect(self):
        self.main_w.actions_connector(MainUI.DELETE_FILE, self.delete_file_function)
        self.main_w.actions_connector(MainUI.RENAME_FILE, self.rename_file_function)
        self.main_w.actions_connector(MainUI.UPLOAD_FILE, self.upload_file_function)
        self.main_w.actions_connector(MainUI.GET_FILES, self.get_dir_function)
        self.main_w.actions_connector(MainUI.CREATE_NEW_FOLDER, self.create_new_dir_function)
        self.main_w.actions_connector(MainUI.DOWNLOAD_FILE, self.download_file_function)

    @pyqtSlot(object, name="SOLT:check_link_state")
    def __check_link_state(self, args: dict):
        """检测连接状态"""
        self.public_key = args.get("public_key", '')
        state = args["clientState"]
        server_address = args["address"]
        self.login_w.setLoadingState(False)
        if state:
            self.ftp_host = server_address[0]
            self.user_manager.remember_linked_server(address=server_address)  # 储存连接成功的服务器信息
            # print(f"Server state: 0. \nLink successful.")
            self.sub_thread.start_loop()
            info_message_display(self.login_w, information_type="info", whereis="TOP_RIGHT", title="连接成功!")
            if args["isFirstTimeConnection"]:
                info_message_display(self.login_w, information_type="info", whereis="TOP_RIGHT", title="注意",
                                     information="首次连接到该服务器，公钥已保存。")
            self.login_w.set_connected_server_info(f"已连接到 {server_address[0]}:{server_address[1]}")
            saved_users = self.user_manager.saved_users
            last_login_password = None
            for user in saved_users[0]:
                if user[0] == saved_users[1]:
                    last_login_password = user[1]
                    break

            def logout():
                self.user_manager.remember_logined_user((saved_users[1], None))  # 清除密码
                self.login_w.do_logout_action()
                self.login_w.setLoginPage(1)

            if saved_users[1] and last_login_password:  # 若保存有密码
                self.login_w.set_current_user_info(f"User: {saved_users[1]}")
                self.login_w.actions_connector(action_name="login", disconnect=True)
                self.login_w.actions_connector(
                    action_name="login",
                    func=lambda: self.user_login_function((saved_users[1], last_login_password), True)
                )
                # self.login_w.actions_connector("logout", disconnect=True)
                self.login_w.actions_connector("logout", logout)
                self._force_save_user_account = True
                self.login_w.setLoginPage(2)
            else:
                self.login_w.setLoginPage(1)
                if saved_users[0]:
                    self.login_w.add_user_list([u[0] for u in saved_users[0]])

        else:
            if not args["isSameKey"]:
                info_message_display(self.login_w, duration_time=1500, information_type="warn", whereis="TOP_RIGHT",
                                     title=" 公钥异常")
                if not self.login_w.show_diff_public_key_warn(self.public_key):
                    self.sub_thread.pem_file.write_pem_file(pem_content=self.public_key)
                    info_message_display(object_name=self, information_type="info", title="公钥替换成功")
                    self.close_connection()
            else:
                if not self._is_cancel_link:
                    info_message_display(self.login_w, duration_time=2000, information_type="error",
                                         whereis="TOP_RIGHT", title="错误", information=f"{args['error']}")
                self._is_cancel_link = False
        self.sub_thread.signal.disconnect(self.__check_link_state)  # 断开信号槽连接

    def check_signal_recv(self, signal: dict):
        """检测子线程执行状态码,执行成功返回服务器响应"""
        if signal["state"]:
            return signal["recv"], signal["extra"]
        else:
            error = signal["error"]
            if type(error) == OSError:
                error = error.args[1]
            info_message_display(self.login_w, information_type="error", whereis="TOP_RIGHT", title="Error",
                                 information=f"错误:{error!s}")
            info_message_display(self.main_w, information_type="error", whereis="TOP_RIGHT", title="Error",
                                 information=f"错误:{error!s}")
            return {}, None

    @pyqtSlot(object, name="SOLT:check_login_state")
    def __check_login_state(self, signal: dict):
        """检测登陆状态"""
        signal = self.check_signal_recv(signal)
        if signal[0]:
            recv_from_server, account = signal
            if recv_from_server["code"] == 0:
                # 登录成功
                self.login_w.login_finished = True
                self.ftp_port = recv_from_server["ftp_port"]  # ftp 端口
                # print("Login successful!")
                # 设置窗口
                self.login_w.close()
                # 同步主题
                if self.login_w.themeState() == Theme.DARK:
                    self.main_w.setThemeState(Theme.DARK)
                self.main_w.mainUI()
                info_message_display(self.main_w, information_type="info", whereis="TOP_RIGHT",
                                     title="登录成功!", duration_time=2000)

                username = account[0]
                hashed_password = account[1]
                self.sub_thread.set_auth(user=username, token=recv_from_server["token"])  # 获取到token
                if self.login_w.is_remember_pass_checkbox_checked() or self._force_save_user_account:
                    # 是否保存密码
                    self.user_manager.remember_logined_user((username, hashed_password))
                else:
                    self.user_manager.remember_logined_user((username, None))
                self._force_save_user_account = False

            elif recv_from_server["code"] == 401:
                # 登录失败, 密码错误
                msg = recv_from_server.get("msg", '')
                info_message_display(self.login_w, information_type="warn", whereis="TOP_RIGHT", title="登陆失败。",
                                     information=f"密码错误:{msg!s}")
        self.login_w.setLoadingState(False)
        self.sub_thread.signal.disconnect(self.__check_login_state)  # 不管登录成功与否,都断开信号槽连接

    def link_server_function(self, address: tuple|list):
        """连接服务器"""
        address = list(address)
        _P_NI = False
        if not address[1]:
            address[1] = DEFAULT_PORT
        try:
            address[1] = int(address[1])
        except Exception:
            _P_NI = True
        if not address[0]:
            info_message_display(self.login_w, information_type="warn", whereis="TOP_RIGHT", title="警告",
                                 information="地址不得为空")
            return
        elif not isinstance(address[0], str) or _P_NI:
            info_message_display(self.login_w, information_type="warn", whereis="TOP_RIGHT", title="警告",
                                 information="地址格式有误")
            return

        if address[1] > 65535:
            info_message_display(self.login_w, information_type="warn", whereis="TOP_RIGHT", title="警告",
                                 information="超出最大端口范围 0~65535")
            return

        self.login_w.setLoadingState(True)
        try:
            self.sub_thread.signal.disconnect()  # 再次确认断开
        except TypeError:
            ...
        self.sub_thread.load_sub_thread(action=ClientSubThread.CONNECT, address=address)
        self.sub_thread.signal.connect(self.__check_link_state)
        self.sub_thread.start()

    def user_login_function(self, account: tuple, n_hash: bool = False):
        """登录"""
        if not account[0] or not account[1]:
            info_message_display(self.login_w, information_type="warn", whereis="TOP_RIGHT", title="警告",
                                 information="用户名或密码不得为空")
        else:
            self.login_w.setLoadingState(True)
            password = account[1]
            if not n_hash:
                sha256_obj = hashlib.sha256()
                sha256_obj.update(password.encode())
                password = sha256_obj.hexdigest()
            self.sub_thread.load_sub_thread(action=ClientSubThread.REQUEST,
                                            request="login",
                                            data={"username": f'{account[0]}', "password": f'{password}'},
                                            extra=(account[0], password))
            self.sub_thread.signal.connect(self.__check_login_state)
            self.sub_thread.start()

    def get_dir_function(self, dir_id: str = ''):
        self.current_dir_id = dir_id
        self.main_w.file_page.loadProgressBar.start()
        try:
            self.sub_thread.signal.disconnect()
        except TypeError:
            pass
        self.files_information = []

        def transform_file_dict(data: dict) -> list:
            """转化为列表并返回"""
            files_id = list(data.keys())
            parent_dir_id = ''
            size_units = ("B", "KB", "MB", "GB", "TB", "PB")
            for index, i in enumerate(list(data.values())):
                try:
                    created_at = time.strftime(
                        "%Y-%m-%d %H:%M:%S",
                        time.localtime(i['properties']["created_time"])
                    )
                except KeyError:
                    created_at = "Unknown"
                is_folder = i.get("type", None)
                size = transformed_size = int(i["properties"].get("size", 0))
                for i_index in range(0, 6):
                    if transformed_size < 0:
                        transformed_size = "Unavailable"
                        break
                    if transformed_size >= 1024:
                        transformed_size /= 1024
                    else:
                        transformed_size = f"{transformed_size:.2f} {size_units[i_index]}"
                        break
                file_name = i.get("name", "Untitled")
                if is_folder == "file":
                    is_folder = False
                    _suffix = os.path.splitext(file_name)[-1].strip(".").lower()
                    file_type = FILE_TYPES.get(_suffix, _suffix.upper() + " File")
                elif is_folder == "dir":
                    is_folder = True
                    file_type = "File folder"
                    size = None
                    transformed_size = ""

                else:
                    file_type = "Unknown"
                file_info = {
                    "Name": file_name,
                    "isFolder": is_folder,
                    "File_type": file_type,
                    "Transformed_size": transformed_size,
                    "Size": size,
                    "Created_at": created_at,
                    "Permission": i.get("permission", "Unknown"),
                    "File_id": files_id[index]
                }
                if i.get("parent", False):
                    parent_dir_id = files_id[index]
                else:
                    self.files_information.append(file_info)
            for en, i in enumerate(self.files_information):
                i["parent_id"] = parent_dir_id
            return self.files_information

        @pyqtSlot(object, name="get_dir_function__get_recv")
        def __get_recv(signal):
            self.sub_thread.signal.disconnect(__get_recv)
            recv = self.check_signal_recv(signal)
            if recv[0]:
                recv = recv[0]
                if recv["code"] == 0:
                    result = transform_file_dict(recv["dir_data"])
                    self.main_w.file_page.set_files_list(result)
                elif recv["code"] == 404:
                    # 失败 设置当前目录为前一次所处目录
                    self.current_dir_id = self.main_w.file_page.last_dir_path[0]
                    self.main_w.file_page.current_path = self.main_w.file_page.last_dir_path
                    info_message_display(self.main_w, information_type="error", whereis="TOP_RIGHT", title="错误",
                                         information="目录不存在")
                else:
                    info_message_display(self.main_w, information_type="error", whereis="TOP_RIGHT", title="未知错误")

        self.sub_thread.signal.connect(__get_recv)
        if not dir_id:
            self.sub_thread.load_sub_thread(ClientSubThread.REQUEST, request="getRootDir")
            self.sub_thread.start()
        else:
            self.sub_thread.load_sub_thread(ClientSubThread.REQUEST, request="operateDir",
                                            data={"action": "list", "dir_id": dir_id})
            self.sub_thread.start()

    # file_index 是文件在self.files_information中的索引

    def create_new_dir_function(self, data: str = None):
        try:
            self.sub_thread.signal.disconnect()
        except TypeError:
            ...

        @pyqtSlot(object, name="create_new_dir_function__get_recv")
        def __get_recv(signal):
            self.sub_thread.signal.disconnect(__get_recv)
            recv = self.check_signal_recv(signal)[0]
            if recv:
                self.get_dir_function(self.current_dir_id)

        if not data:
            data = "New Folder " + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
        self.sub_thread.load_sub_thread(ClientSubThread.REQUEST, request="createDir",
                                        data={"parent_id": self.current_dir_id, "name": data})
        self.sub_thread.signal.connect(__get_recv)
        self.sub_thread.start()

    def rename_file_function(self, data: str, file_index: int):
        try:
            self.sub_thread.signal.disconnect()
        except TypeError:
            ...
        obj_type = self.files_information[file_index]["isFolder"]
        file_id = self.files_information[file_index]["File_id"]

        def __get_recv(signal):
            self.sub_thread.signal.disconnect(__get_recv)
            recv = self.check_signal_recv(signal)[0]
            if recv:
                ...

        if obj_type:
            self.sub_thread.load_sub_thread(ClientSubThread.REQUEST, request="operateDir",
                                            data={"dir_id": file_id, "action": 'rename', 'new_dirname': data})
        else:
            self.sub_thread.load_sub_thread(ClientSubThread.REQUEST, request="operateFile",
                                            data={"file_id": file_id, "action": 'rename', 'new_filename': data})
        self.sub_thread.signal.connect(__get_recv)
        self.sub_thread.start()

    def delete_file_function(self, file_id: str):
        try:
            self.sub_thread.signal.disconnect()
        except TypeError:
            ...
        for file in self.files_information:
            if file["File_id"] == file_id:
                obj_type = file["isFolder"]
                break
        else:
            return

        @pyqtSlot(dict, name="delete_file_function__get_recv")
        def __get_recv(signal):
            self.sub_thread.signal.disconnect(__get_recv)
            recv = self.check_signal_recv(signal)[0]
            if recv:
                self.get_dir_function(self.current_dir_id)

        if obj_type:
            self.sub_thread.load_sub_thread(request="operateDir", data={"dir_id": file_id, "action": 'delete'})
        else:
            self.sub_thread.load_sub_thread(request="operateFile", data={"file_id": file_id, "action": 'delete'})
        self.sub_thread.signal.connect(__get_recv)
        self.sub_thread.start()
        return

    def download_file_function(self, file_index: int):
        """下载文件"""
        try:
            self.sub_thread.signal.disconnect()
        except TypeError:
            pass
        file = self.files_information[file_index]

        ftp_file_io = FtpFilesManager()
        file_name = str(file['Name'])
        file_size = int(file['Size'])
        result = ftp_file_io.load_file(FtpFilesManager.WRITE, file_name, file_size)  # 载入文件

        def __ftp_respond(signal):  # 结果处理
            if not signal['state']:
                if signal["error"] == "FEE":
                    info_message_display(self.main_w, title="注意", information="文件已存在")
                else:
                    info_message_display(self.main_w, title="未知错误", information=str(signal["error"]))

        @pyqtSlot(dict, name="download_file_function__get_recv")
        def __get_recv(signal):
            self.sub_thread.signal.disconnect(__get_recv)
            recv = self.check_signal_recv(signal)[0]
            if recv:
                if recv["code"] == 0:
                    # task
                    task_id = recv["data"]["task_id"]
                    task_token = recv["data"]["task_token"]
                    ftp_file_names = recv["data"]["t_filename"]  # ftp文件名(字典)
                    ftp_file_name = list(ftp_file_names.values())[0]
                    ftp_task.load_task(task_id, task_token, ftp_file_io, ftp_file_name)
                    ftp_task.start()

        # send request
        if result["state"]:
            ftp_task = ClientFtpTask((self.ftp_host, self.ftp_port), ClientFtpTask.DOWNLOAD_FILE)  # 创建task
            ftp_task.connector(result_func=__ftp_respond)
            self.sub_thread.load_sub_thread(2, request="operateFile",
                                            data={"action": "read", "file_id": file['File_id']})
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
        result = ftp_file_io.load_file(FtpFilesManager.READ, file_path, file_size)  # 载入要上传的文件

        def __ftp_respond(signal):
            if not signal['state']:
                info_message_display(self.main_w, title="错误", information=str(signal["error"]))
            info_message_display(self.main_w, title="Success", information=f"{file_name}上传成功")
            self.get_dir_function(self.current_dir_id)

        @pyqtSlot(object, name="upload_file_function__get_recv")
        def __get_recv(signal):
            self.sub_thread.signal.disconnect(__get_recv)
            recv = self.check_signal_recv(signal)[0]
            if recv:
                if recv['code'] == 0:
                    task_id = recv["data"]["task_id"]
                    task_token = recv["data"]["task_token"]
                    ftp_file_names = recv["data"]["t_filename"]  # ftp文件名(字典)
                    ftp_file_name = list(ftp_file_names.values())[0]
                    ftp_task.load_task(task_id, task_token, ftp_file_io, ftp_file_name)
                    ftp_task.start()
                if recv['code'] == -1:
                    info_message_display(self.main_w, information_type="warn", title="注意", information="文件被占用")

        file_name = str(os.path.basename(file_path))
        file_names = [_["Name"] for _ in self.files_information]

        if result["state"]:  # 若文件加载成功
            self.sub_thread.signal.connect(__get_recv)
            ftp_task = ClientFtpTask((self.ftp_host, self.ftp_port), ClientFtpTask.UPLOAD_FILE)  # 创建upload_task
            ftp_task.connector(result_func=__ftp_respond)
            if not (file_name in file_names):
                self.sub_thread.load_sub_thread(ClientSubThread.REQUEST,
                                                request="createFile",
                                                data={"directory_id": self.current_dir_id,
                                                      "filename": file_name
                                                      }
                                                )
            elif file_name in file_names:  # 若远程文件存在，覆写
                title = 'Confirm'
                content = f"""文件{file_name}存在同名文件,是否覆盖?"""
                w = MessageDisplay(title, content, parent=self.main_w, btn_text=("取消", "覆盖"))
                if w.exec():
                    info_message_display(object_name=self.main_w, information_type="info", title="已取消该操作")
                    return
                else:
                    file_id = self.files_information[file_names.index(file_name)]["File_id"]
                    self.sub_thread.load_sub_thread(ClientSubThread.REQUEST,
                                                    request="operateFile",
                                                    data={"action": "write",
                                                          "file_id": file_id
                                                          }
                                                    )
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
