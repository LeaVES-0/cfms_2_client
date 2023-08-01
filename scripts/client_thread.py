#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 3/7/2023 下午12:32
# @Author  : LeaVES
# @FileName: client_thread.py
# coding: utf-8
import ftplib
import hashlib
import json
import pprint
import socket
import ssl
import time

from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
from PyQt6.QtCore import *

from scripts.fileio import ClientPemFile, FtpFilesDownloadManager

DEFAULT_PORT = 5103


class Client:
    def __init__(self):
        ftplib.FTP_TLS.ssl_version = ssl.PROTOCOL_TLSv1_2
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, True)
        self.client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
        socket.setdefaulttimeout(30)
        self._is_linked = False  # 内部连接状态特性
        self.AEC_key = None
        self.cfms_dict_to_send = {"version": 1, "request": "", "data": {}}
        self.pem_file = None
        self.ftp_port = None  # 会在主逻辑文件中重新赋值

    def cfms_AES_encrypt(self, data):
        """AES加密"""
        aes_cipher = AES.new(self.AEC_key, AES.MODE_CBC)  # 生成对称加密密钥对象CBC
        encrypted_data = aes_cipher.encrypt(pad(data.encode(), AES.block_size))
        iv = aes_cipher.iv
        return iv + encrypted_data

    def cfms_AES_decrypt(self, data):
        """AES解密"""
        iv = data[:16]
        aes_cipher = AES.new(self.AEC_key, AES.MODE_CBC, iv=iv)  # 生成对称加密密钥对象CBC
        decrypted_data = unpad(aes_cipher.decrypt(data[16:]), AES.block_size)
        return decrypted_data.decode()

    def cfms_recvall(self) -> dict:
        self.client.settimeout(40)
        primary_data = b""
        while True:
            more = self.client.recv(1024)
            primary_data += more
            if len(more) <= 1024:
                break
        recv = json.loads(self.cfms_AES_decrypt(primary_data))
        pprint.pprint(recv)
        return recv

    recv_data = property(cfms_recvall, )

    def __cfms_send(self, request):
        pprint.pprint(request)
        print()
        self.client.sendall(self.cfms_AES_encrypt(json.dumps(request)))
        return True

    def connect_cfms_server(self, host: str, port=DEFAULT_PORT) -> dict:
        """连接到服务器"""
        public_key = None
        first_time_connection = False
        self.AEC_key = get_random_bytes(32)  # 生成对称加密密钥
        try:
            self.pem_file = ClientPemFile(file_name=f"KEY_{host}_{port}")
            self.client.settimeout(40)
            self.client.connect((host, port))
            self.client.sendall("hello".encode())
            self.client.recv(1024)
            self.client.sendall("enableEncryption".encode())
            public_key = json.loads(self.client.recv(1024).decode(encoding="utf-8"))['public_key']
            local_key = self.pem_file.read_pem_file()

            if not local_key:
                self.pem_file.write_pem_file(pem_content=public_key)
                print("It's the first time for you to link this server.")
                first_time_connection = True
            if public_key == local_key:
                print(f"The public key is \n {public_key}")
            elif public_key != local_key and not first_time_connection:
                # self.retry(True)
                print(f"The public key of the server is \n {public_key}."
                      f" \n But your public key is \n {local_key}.")
                return {"clientState": False, "address": (host, port),
                        "isSameKey": False, "public_key": public_key}

            rsa_public_key = RSA.import_key(public_key)
            rsa_public_cipher = PKCS1_OAEP.new(rsa_public_key)

            encrypted_data = rsa_public_cipher.encrypt(self.AEC_key)  # 用公钥加密对称加密密钥
            self.client.sendall(encrypted_data)  # 发送加密的对称加密密钥

            server_response = json.loads(self.cfms_AES_decrypt(self.client.recv(1024)))
            if server_response['code'] == 0:
                self._is_linked = True
                self.ftp_host = host
                return {"clientState": True, "address": (host, port),
                        "isFirstTimeConnection": first_time_connection, "public_key": public_key}
        except (TypeError, ValueError, OSError, UnboundLocalError, ConnectionRefusedError, ConnectionError) as e:
            return {"clientState": False, "address": (host, port),
                    "isFirstTimeConnection": first_time_connection, "isSameKey": True, "public_key": public_key,
                    "error": e}

    def set_auth(self, user: str, token: str):
        """全局设置auth"""
        account = {"username": user, "token": token}
        self.cfms_dict_to_send.setdefault("auth", {}).update(account)

    def cfms_user_login(self, username: str, password: str):
        """用户登陆"""
        try:
            sha256_obj = hashlib.sha256()
            sha256_obj.update(password.encode())
            password = sha256_obj.hexdigest()
            to_send = self.cfms_dict_to_send.copy()
            to_send.update({"request": "login", "data": {"username": f'{username}', "password": f'{password}'}})
            self.__cfms_send(to_send)
            return {"loginState": True, "recv": self.recv_data, "account": (username, password)}
        except (TimeoutError, TypeError, ValueError, OSError, ConnectionRefusedError, ConnectionError) as e:
            print(e)
            return {"loginState": False, "error": e}

    def refresh_token(self, t: int = 3400):
        while self._is_linked:
            time.sleep(t)
            recv = self._cfms_send_request(request="refreshToken")
            if recv["state"]:
                if recv["recv"]["code"] == 0:
                    print("Token has been refreshed successfully.")
                elif recv["recv"]["code"] == 401:
                    print("Fail to refresh token. Old token is invalid.")

    def _cfms_send_request(self, request: str, data: dict = None):
        try:
            to_send = self.cfms_dict_to_send.copy()
            to_send.update({"request": request, "data": data})
            self.__cfms_send(to_send)
            return {"state": True, "recv": self.recv_data}
        except (TimeoutError, TypeError, ValueError, OSError, ConnectionRefusedError, ConnectionError) as e:
            return {"state": False, "error": e}

    def reset_sock(self):
        """重置连接"""
        self._is_linked = False
        self.close_connection()
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, True)
        self.client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
        self.client.settimeout(40)

    def close_connection(self):
        """关闭连接"""
        to_send = {"version": 1, "request": "disconnect"}
        self.client.settimeout(5)  # 若尝试安全关闭时超时，至多等待5s
        try:
            if self._is_linked:
                self._is_linked = False
                self.__cfms_send(to_send)  # 可能抛出异常的位置
                self.client.shutdown(2)
            self.client.close()  # 释放socket
        except (TypeError, OSError, TimeoutError) as e:
            self.client.close()
            print("Socket has been closed directly!", e)
        else:
            print("Socket has been closed safely.")


class ClientSubThread(QThread, Client):
    """子线程"""
    # 信号必须在此定义
    signal = pyqtSignal(dict, name="ClientSubThread")

    def __init__(self):
        """action
        0:link server
        1:login
        2:send message"""
        super(ClientSubThread, self).__init__()
        self.sub_thread_args = None
        self.sub_thread_action = None
        self.loaded = False

    def load_sub_thread(self, action: int = 2, *args, **kwargs):
        self.sub_thread_action = action
        self.sub_thread_kwargs = kwargs
        self.sub_thread_args = args
        self.loaded = True

    def run(self):
        if self.loaded:
            if self.sub_thread_action == 0:
                address = self.sub_thread_kwargs["address"]
                tran_address = (str(address[0]), int(address[1]))
                data_0 = self.connect_cfms_server(*tran_address)
                self.signal.emit(data_0)

            elif self.sub_thread_action == 1:
                data_1 = self.cfms_user_login(username=self.sub_thread_kwargs["name"],
                                              password=self.sub_thread_kwargs["password"])
                self.signal.emit(data_1)

            elif self.sub_thread_action == 2:
                data_2 = self._cfms_send_request(request=self.sub_thread_kwargs["request"],
                                                 data=self.sub_thread_kwargs.setdefault("data", {}))
                self.signal.emit(data_2)

            elif self.sub_thread_action == 3:
                self.refresh_token()

        else:
            raise ValueError
        self.loaded = False


class ClientFtpThread(QThread):
    ftp_signal = pyqtSignal(object, name="FTP_SubThread")

    def __init__(self, address: tuple):
        super().__init__(None)
        self.ftp_address = address
        self.ftp_obj = ftplib.FTP_TLS()
        self.ftp_obj.debug(0)

    def download_file(self, ftp_file_io: FtpFilesDownloadManager, task_id: str, task_token: str, ftp_file_names: dict,
                      file_size, is_dir: bool = False):
        try:
            if not is_dir:
                ftp_file_name = list(ftp_file_names.values())[0]
                self.ftp_obj.connect(*self.ftp_address)
                self.ftp_obj.login(user=task_id, passwd=task_token)
                self.ftp_obj.prot_p()
                sock, size = self.ftp_obj.ntransfercmd(cmd=f"RETR {ftp_file_name}", rest=None)
                ftp_file_io.write_file(sock=sock, size=file_size)
                self.ftp_obj.voidresp()
                self.ftp_obj.quit()

            elif is_dir:
                ...
        except ftplib.all_errors as e:
            return {"state": False, "error": e}

    def upload_file(self, ftp_file_io: FtpFilesDownloadManager, task_id: str, task_token: str,
                    ftp_file_names: dict, is_dir: bool = False):
        try:
            if not is_dir:
                ftp_file_name = list(ftp_file_names.values())[0]
                self.ftp_obj.connect(*self.ftp_address)
                self.ftp_obj.login(user=task_id, passwd=task_token)
                self.ftp_obj.prot_p()
                sock = self.ftp_obj.transfercmd(cmd=f"STOR {ftp_file_name}", rest=None)
                ftp_file_io.read_file(sock)
                self.ftp_obj.voidresp()
                self.ftp_obj.quit()
                return {"state": True}
        except ftplib.all_errors as e:
            return {"state": False, "error": e}

    def load_ftp_obj(self, action: str, args):
        self.ftp_obj_action = action
        self.ftp_obj_args = args

    def run(self):
        recv = None
        if self.ftp_obj_action == "download_file":
            recv = self.download_file(*self.ftp_obj_args)

        elif self.ftp_obj_action == "upload_file":
            recv = self.upload_file(*self.ftp_obj_args)
        self.ftp_signal.emit(recv)
