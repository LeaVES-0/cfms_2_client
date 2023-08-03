#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 10/7/2023 下午10:028
# @Author  : LeaVES
# @FileName: cfms_user.py
# coding: utf-8

from scripts.fileio import ClientDataFile


class CfmsUserManager:
    def __init__(self):
        self.server_address = []
        self.client_config, self.client_memory = None, None
        self.data_file = ClientDataFile()
        if not self.data_file.r_datafile():
            # 若为空,初始化data_mod,写入data
            self.data_mod = {'client_memory': {'servers': []},
                             'client_config': {}}
            self.data_file.w_datafile(data=self.data_mod)
        else:
            self.__refresh_data()

    def __refresh_data(self):
        """读取/刷新储存"""
        self.data_mod = self.data_file.r_datafile()
        self.client_memory = self.data_mod.setdefault("client_memory", {})
        self.client_config = self.data_mod.setdefault('client_config', {})

    def remember_linked_server(self, address: list):
        """记住登录成功的服务器"""
        self.__refresh_data()
        already_saved = False
        self.server_address = address  # 当前服务器地址
        servers = [i for i in self.client_memory.setdefault("servers", [])]
        if self.client_memory["servers"]:
            for index, server in enumerate(servers):
                if address == server["server_address"]:
                    already_saved = True
                    break
            if not already_saved:
                self.client_memory["servers"].append({"server_address": address, "users": []})
        else:  # 若没有储存的服务器, 跳过检查
            self.client_memory['servers'].append({"server_address": address, "users": []})
        self.data_file.w_datafile(self.data_mod)

    def remember_logined_user(self, account: list):
        """记住登录成功的用户"""
        self.__refresh_data()
        changed = False
        for server in self.client_memory["servers"]:
            if server["server_address"] == self.server_address:
                server["last_login"] = account[0]
                if server.setdefault('users', []):
                    users = [i for i in server['users']]
                    for index, saved_account in enumerate(users):
                        if saved_account[0] == account[0]:
                            server["users"][index][1] = account[1]
                            changed = True
                            break
                    if not changed:
                        server["users"].append(account)
                else:  # 若没有储存的用户, 跳过检查
                    server["users"].append(account)
        self.data_file.w_datafile(self.data_mod)

    def get_saved_servers(self):
        self.__refresh_data()
        server_addresses = [s["server_address"] for s in self.client_memory["servers"]]
        return server_addresses

    def get_saved_users(self):
        # 连接成功后可用
        self.__refresh_data()
        users = []
        last_login = None
        for server in [s for s in self.client_memory["servers"]]:
            if server["server_address"] == self.server_address:
                last_login = server.get("last_login", None)
                users = [user for user in server["users"]]
                break
        return users, last_login

    saved_servers = property(get_saved_servers)
    saved_users = property(get_saved_users)
