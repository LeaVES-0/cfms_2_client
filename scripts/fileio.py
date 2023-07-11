#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 9/7/2023 下午9:16
# @Author  : LeaVES
# @FileName: fileio.py
# coding: utf-8

import pathlib, json

DEFAULT_PEM_DIR = "data/saved_certs"
DEFAULT_DATA_DIR = "data"


class ClientPemFile:
    def __init__(self, fileName: str):
        pathlib.Path(f'./{DEFAULT_PEM_DIR}').mkdir(parents=True, exist_ok=True)
        self.pemfile = pathlib.Path(f"{DEFAULT_PEM_DIR}/{fileName!s}.pem")
        print('PemFile:'f"{DEFAULT_PEM_DIR}/{fileName!s}.pem .")

    def r_pemfile(self):
        """读公钥文件"""
        self.pemfile.touch(exist_ok=True)
        pemfileContent = self.pemfile.read_text(encoding="utf-8")
        return pemfileContent

    def w_pemfile(self, pemcontent: str):
        """写公钥文件"""
        self.pemfile.write_text(data=pemcontent, encoding="utf-8")

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

    