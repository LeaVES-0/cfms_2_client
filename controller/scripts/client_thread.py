#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 3/7/2023 下午12:32
# @Author  : LeaVES
# @FileName: client_thread.py
# coding: utf-8
import ftplib
import json
import pprint
import socket
import ssl
import threading
import time
import uuid

from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
from PyQt6.QtCore import *

from scripts.fileio import ClientPemFile, FtpFilesManager

DEFAULT_PORT = 5103


class Client:
    def __init__(self):
        ftplib.FTP_TLS.ssl_version = ssl.PROTOCOL_TLSv1_2
        socket.setdefaulttimeout(15)
        self._is_linked = False  # 内部连接状态特性
        self.AEC_key = None
        self.pem_file = None
        self.cfms_dict_to_send = {"version": 1, "request": "", "data": {}}
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, True)
        self.client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)

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

    def cfms_recvall(self, crypt: bool = True):
        try:
            primary_data = [self.client.recv(1024)]
        except Exception:
            return
        
        if primary_data[0] in (0,-1):  # 返回0,-1代表出错
            return
        if not bool(primary_data[0]):
            return
        self.client.setblocking(False)
        while True:
            try:
                more = self.client.recv(1024)
                primary_data.append(more)
            except :
                break
        self.client.setblocking(True)
        primary_data = b"".join(primary_data)
        if crypt:
            recv = json.loads(self.cfms_AES_decrypt(primary_data))
        else:
            recv = json.loads(primary_data)
        pprint.pprint(recv)
        return recv

    def __cfms_send(self, request, crypt: bool = True):
        pprint.pprint(request)
        print()
        if crypt:
            self.client.sendall(self.cfms_AES_encrypt(json.dumps(request)))
        return True

    def connect_cfms_server(self, host: str, port=DEFAULT_PORT) -> dict:
        """连接到服务器"""
        public_key = None
        first_time_connection = False
        self.AEC_key = get_random_bytes(32)  # 生成对称加密密钥
        try:
            self.pem_file = ClientPemFile(file_name=f"KEY_{host}_{port}")
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
                print(f"The public key of the server is \n {public_key}."
                      f" \n But your public key is \n {local_key}.")
                return {"clientState": False,
                        "address": (host, port),
                        "isSameKey": False,
                        "public_key": public_key}

            rsa_public_key = RSA.import_key(public_key)
            rsa_public_cipher = PKCS1_OAEP.new(rsa_public_key)

            encrypted_data = rsa_public_cipher.encrypt(self.AEC_key)  # 用公钥加密对称加密密钥
            self.client.sendall(encrypted_data)  # 发送加密的对称加密密钥

            server_response = json.loads(self.cfms_AES_decrypt(self.client.recv(1024)))
            if server_response['code'] == 0:
                self._is_linked = True
                self.ftp_host = host
                return {"clientState": True,
                        "address": (host, port),
                        "isFirstTimeConnection": first_time_connection,
                        "public_key": public_key}
        except (TimeoutError, TypeError, ValueError, OSError, ConnectionRefusedError, ConnectionError) as e:
            self.reset_sock()
            return {"clientState": False,
                    "address": (host, port),
                    "isFirstTimeConnection": first_time_connection,
                    "isSameKey": True,
                    "public_key": public_key,
                    "error": e}

    def set_auth(self, user: str, token: str):
        """全局设置auth"""
        account = {"username": user, "token": token}
        self.cfms_dict_to_send.setdefault("auth", {}).update(account)

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
            recv = self.cfms_recvall()
            if recv:
                return {"state": True, "recv": recv}
            else:
                raise ConnectionError
        except (TimeoutError, TypeError, ValueError, OSError, ConnectionRefusedError, ConnectionError) as e:
            return {"state": False, "error": e}

    def reset_sock(self):
        """重置连接"""
        self._is_linked = False
        self.close_connection()
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, True)
        self.client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)

    def close_connection(self):
        """关闭连接"""
        to_send = {"version": 1, "request": "disconnect"}
        try:
            if self._is_linked:
                self._is_linked = False
                self.client.settimeout(5)  # 若尝试安全关闭时超时，至多等待5s
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

    REQUEST = 2
    CONNECT = 0

    def __init__(self):
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

            elif self.sub_thread_action == 2:
                data_2 = self._cfms_send_request(request=self.sub_thread_kwargs["request"],
                                                 data=self.sub_thread_kwargs.setdefault("data", {}))
                data_2["extra"] = self.sub_thread_kwargs.get("extra", None)
                self.signal.emit(data_2)

            elif self.sub_thread_action == 3:
                self.refresh_token()

        else:
            raise ValueError
        self.loaded = False


class ClientFtpTask(QThread):
    """Signal 'ftp_signal' return the result of ftp transport."""
    __ftp_signal = pyqtSignal(dict, name="FTP_SubThread_signal")
    __ftp_progress_signal = pyqtSignal(tuple, name="ftp_progress_signal")

    UPLOAD_FILE = "UPLOAD_FILE"
    DOWNLOAD_FILE = "DOWNLOAD_FILE"

    def __init__(self, address: tuple, mode, task_uuid: str = uuid.uuid1()):
        super().__init__(None)
        self._loaded = False
        self._thread_run = True
        self._ftp_address = address
        self.task_mode = mode
        self.task_uuid = task_uuid
        self.state = 1
        self.setObjectName(f"FtpTask-'{self.task_uuid}'")
        self.ftp_obj = ftplib.FTP_TLS()
        self.ftp_obj.debug(0)

    def __str__(self):
        return self.task_info

    def __call__(self, *args, **kwargs):
        return self

    @property
    def task_info(self):
        return {"mode": self.task_mode, "uuid": self.task_uuid, "state": self.state}

    def load_task(self, _task_id, _task_token, task_fileio: FtpFilesManager, file_name=None):
        self._loaded = True
        self.task_id = _task_id
        self.task_token = _task_token
        self.task_fileio = task_fileio
        self.ftp_fake_file_name = file_name
        self._progress_thread = threading.Thread(target=lambda: self.get_transport_progress(self.task_fileio))

    def connect(self, _result_signal=None, _progress_signal=None):
        for i in range(2):
            try:
                self.__ftp_signal.connect(_result_signal)
                self.__ftp_progress_signal.connect(_progress_signal)
            except TypeError:
                continue

    def task_transform(self):
        try:
            self.ftp_obj.debug(2)
            self.ftp_obj.connect(*self._ftp_address)
            self.ftp_obj.login(user=self.task_id, passwd=self.task_token)
            self.ftp_obj.prot_p()
            self._progress_thread.start()
            if self.task_mode == "DOWNLOAD_FILE":
                sock = self.ftp_obj.transfercmd(cmd=f"RETR {self.ftp_fake_file_name}", rest=None)
                self.task_fileio.write_file(sock)

            elif self.task_mode == "UPLOAD_FILE":
                sock = self.ftp_obj.transfercmd(cmd=f"STOR {self.ftp_fake_file_name}", rest=None)
                self.task_fileio.read_file(sock)
            self._thread_run = False
            self.ftp_obj.voidresp()
            self.ftp_obj.quit()
            self.state = 0
            return {"state": True}
        except ftplib.all_errors as e:
            self.state = -1
            print(e)
            return {"state": False, "error": e}
        finally:
            self._thread_run = False

    def get_transport_progress(self, file_io: FtpFilesManager):
        size_units = ["B/s", "KB/s", "MB/s", "GB/s", "TB/s", "PB/s"]
        last_bytes = 0
        tar2 = tar1 = 0
        speed = "0B/s"
        while self._thread_run:
            tar0 = time.perf_counter()
            current_bytes = file_io.transport_bytes
            try:
                speed = (current_bytes - last_bytes) / (tar1 - tar2)
                for i_index in range(0, 6):
                    if speed >= 1024:
                        speed /= 1024
                    else:
                        speed = f"{speed:.1f}{size_units[i_index]}"
                        break
            except ZeroDivisionError:
                pass
            last_bytes = current_bytes
            progress = round(100 * current_bytes / file_io.file_size, 2)
            self.__ftp_progress_signal.emit((progress, speed))
            print(speed)

            tar2 = tar0
            time.sleep(0.1)
            tar1 = time.perf_counter()
        try:
            self.__ftp_progress_signal.disconnect()
        except TypeError:
            ...

    def run(self):
        if not self._loaded:
            raise ValueError
        recv = self.task_transform()
        self.__ftp_signal.emit(recv)
        try:
            self.__ftp_signal.disconnect()
        except TypeError:
            ...
