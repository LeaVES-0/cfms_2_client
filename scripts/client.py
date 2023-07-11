#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 3/7/2023 下午12:32
# @Author  : LeaVES
# @FileName: client.py
# coding: utf-8

import socket
from typing import Any
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import hashlib, json

from scripts.fileio import ClientPemFile

DEFAULT_PORT = 5103


class Client:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, True)
        self.client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
        socket.setdefaulttimeout(7)

    def cfms_AES_encrypt(self, data):
        """AES加密"""
        AES_cipher = AES.new(self.AEC_key, AES.MODE_CBC)  # 生成对称加密密钥对象CBC
        encrypted_data = AES_cipher.encrypt(pad(data.encode(), AES.block_size))
        iv = AES_cipher.iv
        return iv + encrypted_data

    def cfms_AES_decrypt(self, data):
        """AES解密"""
        iv = data[:16]
        AES_cipher = AES.new(self.AEC_key, AES.MODE_CBC, iv=iv)  # 生成对称加密密钥对象CBC
        decrypted_data = unpad(AES_cipher.decrypt(data[16:]), AES.block_size)
        return decrypted_data.decode()

    def cfms_recvall(self):
        self.client.settimeout(7)
        while True:
            primaryData, more = b"", b""
            more = self.client.recv(1024)
            primaryData += more
            if len(more) < 1024:
                return json.loads(self.cfms_AES_decrypt(primaryData))

    def connect_cfms_server(self, host, port=DEFAULT_PORT):
        """连接到服务器"""
        self.pemfile = ClientPemFile(fileName=f"KEY_{host}_{port}")
        self.samePublicKey = True
        self.clientstate = False
        self.client.settimeout(7)
        self.client.connect((host, port))

        self.client.sendall("hello".encode())
        self.client.recv(1024)
        self.client.sendall("enableEncryption".encode())
        self.public_key = json.loads(self.client.recv(1024).decode(encoding="utf-8"))['public_key']
        localkey = self.pemfile.r_pemfile()
        
        if self.public_key == localkey:
            print(f"The public key is \n {self.public_key}")
        elif not localkey:
            self.pemfile.w_pemfile(pemcontent=self.public_key)
        else:
            print(f"The public key of the server is \n {self.public_key}. \n But your public key is \n {localkey}.")
            self.samePublicKey = False
            return

        RSA_public_key = RSA.import_key(self.public_key)
        RSA_public_cipher = PKCS1_OAEP.new(RSA_public_key)

        self.AEC_key = get_random_bytes(32)  # 生成对称加密密钥

        encrypted_data = RSA_public_cipher.encrypt(self.AEC_key)  # 用公钥加密对称加密密钥
        self.client.sendall(encrypted_data)  # 发送加密的对称加密密钥

        serverResponse = json.loads(self.cfms_AES_decrypt(self.client.recv(1024)))
        if serverResponse['code'] == 0:
            print(f"Server state: {serverResponse['code']}. \nLink successful.")
            self.clientstate = True

    def cfms_user_login(self, username, password):
        """用户登陆"""
        sha256_obj = hashlib.sha256()
        sha256_obj.update(password.encode())
        request_data = {
            "version": 1,
            "request": "login",
            "data": {
                "username": f"{username}",
                "password": f"{sha256_obj.hexdigest()}"
            },
            "token": ""
        }
        self.client.send(self.cfms_AES_encrypt(json.dumps(request_data)))
        self.recv_token = self.recv_data

    def close(self):
        self.client.close()

    recv_data = property(cfms_recvall, )
