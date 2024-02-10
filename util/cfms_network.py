#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 3/7/2023 下午12:32
# @Author  : LeaVES
# @FileName: cfms_network.py
# coding: utf-8
import ftplib
import json
import pprint
import secrets
import socket
import ssl
import threading
import time
import uuid
import logging

from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
from PyQt6.QtCore import *

from util.cfms_fileIO import ClientPemFile, FtpFilesManager

DEFAULT_PORT = 5103


class CfmsClientSocket:
    ftplib.FTP_TLS.ssl_version = ssl.PROTOCOL_TLSv1_2
    socket.setdefaulttimeout(15)

    def __init__(self, logger: logging.Logger = None):
        self.is_linked = False  # 内部连接状态特性
        self.AEC_key = None
        self.pem_file = None
        self._server_response = None
        self.cfms_dict_to_send = {"version": 1, "request": "", "data": {}}
        self.main_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.main_sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, True)
        self.main_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
        self.logger = logger
        self.logging(logger)
        self.main_sock.setblocking(False)

        self.requests = []
        self.responses = []

    def logging(self, logger):
        if not logger:
            self.logger = logging.getLogger("CfmsClient")
            logging.basicConfig(filename=f'log.txt',
                                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s-%(funcName)s',
                                level=logging.DEBUG)

    def cfms_aes_encrypt(self, data):
        """AES加密"""
        aes_cipher = AES.new(self.AEC_key, AES.MODE_CBC)  # 生成对称加密密钥对象CBC
        encrypted_data = aes_cipher.encrypt(pad(data.encode(), AES.block_size))
        iv = aes_cipher.iv
        return iv + encrypted_data

    def cfms_aes_decrypt(self, data):
        """AES解密"""
        iv = data[:16]
        aes_cipher = AES.new(self.AEC_key, AES.MODE_CBC, iv=iv)  # 生成对称加密密钥对象CBC
        decrypted_data = unpad(aes_cipher.decrypt(data[16:]), AES.block_size)
        return decrypted_data.decode()

    def cfms_recvall(self, crypt: bool = True):
        """
        接收来自cfms服务器的数据并自动解密,
        crypt 为假时不解密。
        此函数自带1ms阻塞"""
        primary_data = []
        try:
            self.main_sock.setblocking(True)
            self.main_sock.settimeout(0.001)
            primary_data.append(self.main_sock.recv(1024))
        except TimeoutError:
            return None
        except OSError as e:
            if e.errno == 10038:
                return None
            else:
                raise e

        if primary_data[0] in (0,-1):  # 返回0,-1代表出错
            return None

        self.main_sock.setblocking(False)
        # if not bool(primary_data[0]):
        #     return
        while primary_data:
            try:
                more = self.main_sock.recv(1024)
                primary_data.append(more)
            except BlockingIOError:
                break
        primary_data = b"".join(primary_data)
        if primary_data:
            if crypt:
                recv = json.loads(self.cfms_aes_decrypt(primary_data))
            else:
                recv = json.loads(primary_data)
            self.logger.debug(f"{'DEBUG:server response':*^50}" + '\n' + pprint.pformat(recv))
            return {"state": True, "recv": recv}
        else:
            return None

    def __cfms_send(self, request, crypt: bool = True):
        request["X-Ca-Timestamp"] = time.time()
        request["trace_id"] = secrets.token_hex(16)
        json_obj = json.dumps(request)
        self.logger.debug(f"{'DEBUG:main_sock request':*^50}" + '\n' + pprint.pformat(request))
        if crypt:
            self.main_sock.sendall(self.cfms_aes_encrypt(json_obj))
        else:
            self.main_sock.send(json_obj)
        return True

    def connect_cfms_server(self, host: str, port: int =DEFAULT_PORT) -> dict:
        """连接到服务器"""
        public_key = None
        first_time_connection = False
        self.AEC_key = get_random_bytes(32)  # 生成对称加密密钥
        self.main_sock.setblocking(True)
        try:
            self.pem_file = ClientPemFile(file_name=f"KEY_{host}_{port}")
            self.main_sock.connect((host, port))
            self.main_sock.sendall("hello".encode())
            self.main_sock.recv(1024)
            self.main_sock.sendall("enableEncryption".encode())
            public_key = json.loads(self.main_sock.recv(1024).decode(encoding="utf-8"))['public_key']
            local_key = self.pem_file.read_pem_file()

            if not local_key:
                self.pem_file.write_pem_file(pem_content=public_key)
                self.logger.info("It's the first time to link this server.")
                first_time_connection = True
            if public_key == local_key:
                self.logger.info(f"The public key is \n {public_key}")
            elif public_key != local_key and not first_time_connection:
                self.logger.warning(f"The public key of the server is \n {public_key}."
                                    f" \n But your public key is \n {local_key}.")
                return {"state": False,
                        "isSameKey": False,
                        "public_key": public_key}

            rsa_public_key = RSA.import_key(public_key)
            rsa_public_cipher = PKCS1_OAEP.new(rsa_public_key)

            encrypted_data = rsa_public_cipher.encrypt(self.AEC_key)  # 用公钥加密对称加密密钥
            self.main_sock.sendall(encrypted_data)  # 发送加密的对称加密密钥

            server_response = json.loads(self.cfms_aes_decrypt(self.main_sock.recv(1024)))
            if server_response['code'] == 0:
                self.is_linked = True
                return {"clientState": True,
                        "address": (host, port),
                        "isFirstTimeConnection": first_time_connection,
                        "public_key": public_key}
        except (TimeoutError, OSError, ConnectionRefusedError, ConnectionError, ConnectionAbortedError) as e:
            self.reset_sock()
            if isinstance(e, OSError):
                e = e.args[1]
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

    # def refresh_token(self, t: int = 3400):
    #     while self._is_linked:
    #         time.sleep(t)
    #         self.cfms_send_request(request="refreshToken")
    #         if recv["state"]:
    #             if recv["recv"]["code"] == 0:
    #                 self.logger.info("Token has been refreshed successfully.")
    #             elif recv["recv"]["code"] == 401:
    #                 self.logger.error("Fail to refresh token. Old token is invalid.")

    def cfms_send_request(self, request: str, data: dict = None):
        try:
            to_send = self.cfms_dict_to_send.copy()
            to_send.update({"request": request, "data": data})
            self.__cfms_send(to_send)
            return {"state": True}
        except (TimeoutError, TypeError, ValueError, OSError, ConnectionRefusedError, ConnectionError) as e:
            print(e)
            return {"state": False, "error": e}

    def reset_sock(self):
        """重置连接"""
        self.is_linked = False
        self.close_connection()
        self.main_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.main_sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, True)
        self.main_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
        return

    def close_connection(self):
        """关闭连接"""
        to_send = {"version": 1, "request": "disconnect"}
        try:
            self.main_sock.setblocking(True)
            if self.is_linked:
                self.is_linked = False
                self.main_sock.settimeout(5)  # 若尝试安全关闭时超时，至多等待5s
                self.__cfms_send(to_send)  # 可能抛出异常的位置
                self.main_sock.shutdown(2)
            self.main_sock.close()  # 释放socket
        except (TypeError, OSError, TimeoutError) as e:
            self.main_sock.close()
            self.logger.warning("Socket has been closed directly!", e)
        else:
            self.logger.info("Socket has been closed safely.")
        return


class ClientMainLoopThread(QThread):
    def __init__(self, target: CfmsClientSocket):
        self.parent = target
        super().__init__()

    def refresh_token(self):
        ...

    def main_loop(self):
        p = self.parent
        while self.parent.is_linked:
            try:
                if self.parent.requests:
                    for index, request in enumerate(self.parent.requests):
                        self.parent.cfms_send_request(request[0], request[1])
                        del self.parent.requests[index]
            except Exception as e:
                print(e)
            data = p.cfms_recvall() # cfms_recvall 带0.001阻塞
            if data:
                self.parent.responses.append(data)

    def run(self):
        self.main_loop()


class ClientSubThread(QThread, CfmsClientSocket):
    """子线程"""
    # 信号必须在此定义
    signal = pyqtSignal(dict, name="ClientSubThread")

    REQUEST = 2
    CONNECT = 0

    def __init__(self, *args, **kwargs):
        super(ClientSubThread, self).__init__()
        self._sub_thread_args = args
        self._sub_thread_kwargs = kwargs
        self.sub_thread_action = None
        self.loaded = False
        self.__mainloop = ClientMainLoopThread(target=self)

    def load_sub_thread(self, action: int = 2, *args, **kwargs):
        self.sub_thread_action = action
        self._sub_thread_kwargs = kwargs
        self._sub_thread_args = args
        self.loaded = True

    def start_loop(self):
        # print("start listening...")
        self.__mainloop.start()

    def run(self):
        if self.loaded:
            if self.sub_thread_action == 0:
                address = self._sub_thread_kwargs["address"]
                tran_address = (str(address[0]), int(address[1]))
                data = self.connect_cfms_server(*tran_address)
                self.signal.emit(data)

            elif self.sub_thread_action == 2:
                # data = self._cfms_send_request(request=self.sub_thread_kwargs["request"],
                #                                  data=self.sub_thread_kwargs.setdefault("data", {}))
                self.requests.append(
                    (self._sub_thread_kwargs["request"], self._sub_thread_kwargs.setdefault("data", {}))
                )
                t = 0
                while t <= 1000:
                    t += 1
                    if self.responses:
                        if data := self.responses.pop(0):
                            break
                    else:
                        time.sleep(0.01)
                else:
                    data = {"state": False, "error": "time out"}
                    self.signal.emit(data)
                    return
                data["extra"] = self._sub_thread_kwargs.get("extra", None)
                self.logger.debug(pprint.pformat(data))
                self.signal.emit(data)

            # elif self.sub_thread_action == 3:
            #     self.refresh_token()

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
        self.setObjectName(f"FtpTask-'{self.task_uuid}'")

        self.state = 1

        self.ftp_obj = ftplib.FTP_TLS()
        self.ftp_obj.debug(0)

        self._progress_thread = threading.Thread(target=lambda: self.get_transport_progress(self._task_fileio))

    def __str__(self):
        return self.task_info

    def __call__(self, *args, **kwargs):
        return self

    @property
    def task_info(self):
        return {"mode": self.task_mode, "uuid": self.task_uuid, "state": self.state}

    def load_task(self, _task_id, _task_token, task_fileio: FtpFilesManager, file_name=None):
        self._loaded = True
        self._task_id = _task_id
        self._task_token = _task_token
        self._task_fileio = task_fileio
        self._ftp_fake_file_name = file_name

    def connector(self, result_func=None, progress_func=None):
        try:
            self.__ftp_signal.connect(result_func)
        except TypeError:
            pass
        try:
            self.__ftp_progress_signal.connect(progress_func)
        except TypeError:
            pass

    def task_transform(self):
        try:
            self.ftp_obj.connect(*self._ftp_address)
            self.ftp_obj.login(user=self._task_id, passwd=self._task_token)
            self.ftp_obj.prot_p()
            self._progress_thread.start()
            if self.task_mode == "DOWNLOAD_FILE":
                sock = self.ftp_obj.transfercmd(cmd=f"RETR {self._ftp_fake_file_name}", rest=None)
                self._task_fileio.write_file(sock)

            elif self.task_mode == "UPLOAD_FILE":
                sock = self.ftp_obj.transfercmd(cmd=f"STOR {self._ftp_fake_file_name}", rest=None)
                self._task_fileio.read_file(sock)
            self._thread_run = False
            self.ftp_obj.voidresp()
            self.ftp_obj.quit()
            self.state = 0
            return {"state": True}
        except ftplib.all_errors as e:
            self.state = -1
            return {"state": False, "error": e}
        finally:
            self._thread_run = False

    def get_transport_progress(self, file_io: FtpFilesManager):
        size_units = ("B/s", "KB/s", "MB/s", "GB/s", "TB/s", "PB/s")
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
            # self.ftp_progress_signal.emit((progress, speed))

            tar2 = tar0
            time.sleep(0.1)
            tar1 = time.perf_counter()
        # try:
            # self.ftp_progress_signal.disconnect()
        # except TypeError:
        #     pass

    def run(self):
        if not self._loaded:
            raise ValueError
        recv = self.task_transform()
        self.__ftp_signal.emit(recv)
        return
