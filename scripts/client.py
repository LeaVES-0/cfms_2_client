#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 3/7/2023 下午12:32
# @Author  : LeaVES
# @FileName: client.py
# coding: utf-8

import hashlib
import json
import socket

from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

from scripts.fileio import ClientPemFile

DEFAULT_PORT = 5103


class Client:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, True)
        self.client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
        socket.setdefaulttimeout(30)
        self.AEC_key = get_random_bytes(32)  # 生成对称加密密钥
        self.cfms_dict_to_send = {"version": 1, "request": "", "data": {}, "token": ""}
        self.public_key, self.pem_file = None, None
        self.samePublicKey = True
        self.client_state = False
        self.first_time_connection = False

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
        while True:
            primary_data, more = b"", b""
            more = self.client.recv(1024)
            primary_data += more
            if len(more) < 1024:
                return json.loads(self.cfms_AES_decrypt(primary_data))

    def __cfms_send(self, request):
        self.client.sendall(self.cfms_AES_encrypt(json.dumps(request)))
        return True

    def connect_cfms_server(self, host, port=DEFAULT_PORT):
        """连接到服务器"""
        self.pem_file = ClientPemFile(file_name=f"KEY_{host}_{port}")
        self.client.settimeout(40)
        self.client.connect((host, port))
        self.client.sendall("hello".encode())
        self.client.recv(1024)
        self.client.sendall("enableEncryption".encode())
        self.public_key = json.loads(self.client.recv(1024).decode(encoding="utf-8"))['public_key']
        local_key = self.pem_file.read_pem_file()

        if not local_key:
            self.pem_file.write_pem_file(pem_content=self.public_key)
            print("It's the first time for you to link this server.")
            self.first_time_connection = True
        if self.public_key == local_key:
            print(f"The public key is \n {self.public_key}")
        elif self.public_key != local_key and not self.first_time_connection:
            print(f"The public key of the server is \n {self.public_key}. \n But your public key is \n {local_key}.")
            self.samePublicKey = False
            return

        rsa_public_key = RSA.import_key(self.public_key)
        rsa_public_cipher = PKCS1_OAEP.new(rsa_public_key)

        encrypted_data = rsa_public_cipher.encrypt(self.AEC_key)  # 用公钥加密对称加密密钥
        self.client.sendall(encrypted_data)  # 发送加密的对称加密密钥

        server_response = json.loads(self.cfms_AES_decrypt(self.client.recv(1024)))
        if server_response['code'] == 0:
            print(f"Server state: {server_response['code']}. \nLink successful.")
            self.client_state = True

    def set_token(self, token: str):
        self.cfms_dict_to_send.update({"token": f'{token}'})

    def cfms_user_login(self, username: str, password: str):
        """用户登陆"""
        sha256_obj = hashlib.sha256()
        sha256_obj.update(password.encode())
        password = sha256_obj.hexdigest()
        to_send = self.cfms_dict_to_send.copy()
        to_send.update({"request": "login", "data": {"username": f'{username}', "password": f'{password}'}})
        print(to_send)
        self.__cfms_send(to_send)
        return self.recv_data, (username, password)

    def cfms_send_request(self, request: str, data):
        to_send = self.cfms_dict_to_send
        to_send.update({"request": f"{request!s}", "data": data})
        self.__cfms_send(to_send)
        return self.recv_data

    def close_connection(self, directly: bool = False):
        """关闭连接"""
        to_send = {"version": 1, "request": "disconnect"}
        if not directly:
            self.__cfms_send(to_send)
        self.client.close()
        print("Socket has been closed.")

    recv_data = property(cfms_recvall, )
