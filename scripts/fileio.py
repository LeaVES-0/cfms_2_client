#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 9/7/2023 下午9:16
# @Author  : LeaVES
# @FileName: fileio.py
# coding: utf-8

import json
import pathlib

DEFAULT_PEM_DIR = "data/saved_certs"
DEFAULT_DATA_DIR = "data"


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
