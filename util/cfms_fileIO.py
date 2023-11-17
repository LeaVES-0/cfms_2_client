#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 9/7/2023 下午9:16
# @Author  : LeaVES
# @FileName: fileio.py
# coding: utf-8

import json
import pathlib

DEFAULT_PEM_DIR = "./data/saved_certs"
DEFAULT_DATA_DIR = "./data"
DEFAULT_DOWNLOAD_PATH = "./download"


class ClientPemFile:
    """程序所有文件操作"""

    def __init__(self, file_name: str):
        pathlib.Path(f'{DEFAULT_PEM_DIR}').mkdir(parents=True, exist_ok=True)
        self.pem_file = pathlib.Path(f"{DEFAULT_PEM_DIR}/{file_name!s}.pem")
        print('PemFile:'f"{DEFAULT_PEM_DIR}/{file_name!s}.pem .")

    def read_pem_file(self):
        """读公钥文件"""
        self.pem_file.touch(exist_ok=True)
        return self.pem_file.read_text(encoding="utf-8")

    def write_pem_file(self, pem_content: str):
        """写公钥文件"""
        self.pem_file.write_text(data=pem_content, encoding="utf-8")


class ClientDataFile:
    def __init__(self):
        pathlib.Path(f'{DEFAULT_DATA_DIR}').mkdir(parents=True, exist_ok=True)
        self.data = pathlib.Path(f"{DEFAULT_DATA_DIR}/data.dat")

    def r_datafile(self):
        self.data.touch(exist_ok=True)
        data = self.data.read_text()
        if not data:
            return False
        return json.loads(data)

    def w_datafile(self, data):
        self.data.write_text(json.dumps(obj=data, indent=4))


class FtpFilesManager:
    WRITE = "write"
    READ = "read"

    def __init__(self, down_path: str = DEFAULT_DOWNLOAD_PATH):
        pathlib.Path(down_path).mkdir(parents=True, exist_ok=True)
        self.down_path = down_path
        self.action = None
        self.transport_bytes = 0

    def load_file(self, action: str, file: str, file_size=None):
        """载入
        file形参 可以是要上传文件的路径,或是要下载文件的名称."""
        self.action = action
        self.file_size = file_size
        if action == "write":
            self.filename = file
            if not pathlib.Path(f'{self.down_path}/{self.filename}').exists():
                self.file = pathlib.Path(f'{DEFAULT_DOWNLOAD_PATH}/{self.filename!s}.cfms_download')
                return {'state': True}
            else:
                return {'state': False, 'error': "FEE"}

        elif action == "read":
            file_path = pathlib.Path(file)
            if file_path.exists():
                self.file = file_path
                return {'state': True}
            else:
                return {'state': False, 'error': "FNE"}

    def write_file(self, sock):
        """写入本地文件"""
        if not self.action == "write":
            raise TypeError
        o_file = self.file.open(mode='wb')
        while True:
            data = sock.recv(1024)
            if not data:
                break
            o_file.write(data)
            self.transport_bytes += len(data)
        sock.shutdown(2)
        sock.close()
        o_file.close()
        self.file.rename(f'{self.down_path}/{self.filename}')

    def read_file(self, sock):
        """读取本地文件"""
        if not self.action == "read":
            raise TypeError
        o_file = open(self.file, "rb")
        while True:
            chunk_data = o_file.read(1024)
            if not chunk_data:
                break
            sock.sendall(chunk_data)
            self.transport_bytes += len(chunk_data)
        sock.shutdown(2)
        sock.close()
