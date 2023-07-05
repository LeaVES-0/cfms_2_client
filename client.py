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
import hashlib, json, time, os, sys, pathlib

DEFAULT_PORT = 5103
DEFAULT_PEM_DIR = "saved_certs"

class Client():
    def __init__(self, host, port=DEFAULT_PORT):
        pathlib.Path(f'./{DEFAULT_PEM_DIR}').mkdir(parents=True, exist_ok=True)
        self.host, self.port = host, port
        self.clientstate = {"errorcode":0}
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, True)
        self.client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
        socket.setdefaulttimeout(7)

    def r_pemfile(self, dir:str=DEFAULT_PEM_DIR):
        """读公钥文件"""
        pemfile = pathlib.Path(f"{dir}/{self.host}:{self.port!s}.pem")
        pemfile.touch(exist_ok=True)
        pemfileContent = pemfile.read_text(encoding="utf-8")
        return pemfileContent

    def w_pemfile(self, pem:str, dir:str=DEFAULT_PEM_DIR):
        """写公钥文件"""
        pemfile = pathlib.Path(f"{dir}/{self.host}:{self.port!s}.pem")
        pemfile.write_text(data=pem, encoding="utf-8")

    def AES_encrypt(self, data):
        """AES加密"""
        AES_cipher = AES.new(self.AEC_key, AES.MODE_CBC) # 生成对称加密密钥对象CBC
        encrypted_data = AES_cipher.encrypt(pad(data.encode(), AES.block_size))
        iv = AES_cipher.iv
        return iv + encrypted_data
    
    def AES_decrypt(self, data):
        """AES解密"""  
        iv = data[:16]  
        AES_cipher = AES.new(self.AEC_key, AES.MODE_CBC, iv=iv) # 生成对称加密密钥对象CBC
        decrypted_data = unpad(AES_cipher.decrypt(data[16:]), AES.block_size)
        return decrypted_data.decode()

    def recvall(self):
        self.client.settimeout(7)
        while True:
            try:
                primaryData, more = b"", b""
                more = self.client.recv(1024)
                primaryData += more
                if len(more) < 1024:
                    return json.loads(self.AES_decrypt(primaryData))
            except TimeoutError as e:
                self.clientstate =  {'errorcode': 102, 'error': e}

    def connectServer(self):
        """连接到服务器"""
        try:
            self.client.connect((self.host, self.port))
        except ConnectionRefusedError as e:
            self.clientstate =  {'errorcode': 100, 'error': e}
        except ConnectionError as e:
            self.clientstate =  {'errorcode': 100, 'error': e}
        self.client.sendall("hello".encode())
        self.client.recv(1024)
        self.client.sendall("enableEncryption".encode())
        public_key = json.loads(self.client.recv(1024).decode(encoding="utf-8"))['public_key']
        self.r_pemfile()
        if public_key == (localkey:=self.r_pemfile()): 
            print(f"The public key is \n {public_key}")
        else:
            print(f"The public key of the server is \n {public_key}. \n But your public key is \n {localkey}.")
            self.w_pemfile(pem = public_key)

        RSA_public_key = RSA.import_key(public_key)
        RSA_public_cipher = PKCS1_OAEP.new(RSA_public_key)

        self.AEC_key = get_random_bytes(32) # 生成对称加密密钥

        encrypted_data = RSA_public_cipher.encrypt(self.AEC_key) # 用公钥加密对称加密密钥
        self.client.sendall(encrypted_data) # 发送加密的对称加密密钥

        serverResponse = json.loads(self.AES_decrypt(self.client.recv(1024)))
        if serverResponse['code'] == 0:
            print(f"Server state: {serverResponse['code']}. \nLink successful.")
            self.clientstate = {'errorcode': 300}
        
    def userLogin(self, username, password):
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
        
        self.client.send(self.AES_encrypt(json.dumps(request_data)))

    def clientClose(self):
        self.client.close()
    
    recv_data = property(recvall,)

if __name__ == "__main__":
    cli = Client('127.0.0.1')
    cli.connectServer()
    cli.userLogin("admin", password="123456")
    print(cli.recv_data)