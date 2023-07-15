#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 10/7/2023 下午10:028
# @Author  : LeaVES
# @FileName: cfms_user.py
# coding: utf-8

from scripts.fileio import ClientDataFile


class CfmsUserManager:
    def __init__(self):
        self.server_address = None
        self.client_config, self.client_memory = None, None
        self.data_file = ClientDataFile()
        if not self.data_file.r_datafile():
            # 若为空 初始化data_mod
            self.data_mod = {'client_memory': {'servers': []},
                             'client_config': {}}
            self.data_file.w_datafile(data=self.data_mod)
        else:
            self.refresh_data()

    def refresh_data(self):
        """刷新储存"""
        self.data_mod = self.data_file.r_datafile()
        self.client_memory = self.data_mod.setdefault("client_memory", {})
        self.client_config = self.data_mod.setdefault('client_config', {})

    def remember_linked_server(self, address: list):
        """记住登录成功的服务器"""
        self.refresh_data()
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
        else:
            self.client_memory['servers'].append({"server_address": address, "users": []})
        self.data_file.w_datafile(self.data_mod)

    def remember_logined_user(self, account: list):
        """记住登录成功的用户"""
        self.refresh_data()
        changed = False
        for server in self.client_memory["servers"]:
            if server["server_address"] == self.server_address:
                if server.setdefault('users', []):
                    users = [i for i in server['users']]
                    for index, saved_account in enumerate(users):
                        if saved_account[0] == account[0]:
                            server["users"][index][1] = account[1]
                            changed = True
                            break
                    if not changed:
                        server["users"].append(account)
                else:
                    server["users"].append(account)
        self.data_file.w_datafile(self.data_mod)

    def show_linked_server(self):
        pass
