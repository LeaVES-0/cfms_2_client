#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 9/7/2023 下午9:16
# @Author  : LeaVES
# @FileName: fileio.py
# coding: utf-8

import json
import pathlib
import sys

DEFAULT_PEM_DIR = "data/saved_certs"
DEFAULT_DATA_DIR = "data"
DEFAULT_DOWNLOAD_PATH = "download"


class ClientPemFile:
    """程序所有文件操作"""

    def __init__(self, file_name: str):
        pathlib.Path(f'./{DEFAULT_PEM_DIR}').mkdir(parents=True, exist_ok=True)
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
        pathlib.Path(f'./{DEFAULT_DATA_DIR}').mkdir(parents=True, exist_ok=True)
        self.data = pathlib.Path(f"{DEFAULT_DATA_DIR}/data.dat")

    def r_datafile(self):
        self.data.touch(exist_ok=True)
        data = self.data.read_text()
        if not data:
            return False
        return json.loads(data)

    def w_datafile(self, data):
        self.data.write_text(json.dumps(obj=data, indent=4))


class FtpFilesDownloadManager:
    def __init__(self, down_path: str = DEFAULT_DOWNLOAD_PATH):
        pathlib.Path(down_path).mkdir(parents=True, exist_ok=True)
        self.path = down_path

    def write_file(self, file_name: str, sock, size: int):
        n_bytes = 0
        if pathlib.Path(f'{self.path}/{file_name}').exists():
            file = pathlib.Path(f'{DEFAULT_DOWNLOAD_PATH}/{file_name!s}.cfms_download')
            o_file = file.open(mode='wb')
            while True:
                data = sock.recv(1024)
                if not data:
                    break
                o_file.write(data)
                n_bytes += len(data)
                print("Received", n_bytes, end='')
                if size:
                    print(f"of {size} total bytes ({(100*n_bytes/float(size)):1f}%)")
                else:
                    print("bytes", end='')
                sys.stdout.flush()
        else:
            return {'state': False, 'error': "FEE"}
        print()
        sock.shutdown(2)
        sock.close()
        o_file.close()
        file.rename(f'{self.path}/{file_name}')
        return {'state': True}

    @staticmethod
    def read_file(file_path: str, sock):
        file_obj = pathlib.Path(file_path)
        if file_obj.exists():
            data = file_obj.read_bytes()
        else:
            return {'state': False, 'error': "FNE"}
        sock.sendall(data)
        sock.shutdown(2)
        sock.close()
