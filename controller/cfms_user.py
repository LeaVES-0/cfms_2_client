#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 10/7/2023 下午10:028
# @Author  : LeaVES
# @FileName: cfms_user.py
# coding: utf-8

from scripts.fileio import ClientDataFile

class CfmsUserManager:
    def __init__(self):
        self.data_file = ClientDataFile()
        if not (content:=self.data_file.r_datafile()):
            self.data_mod = {'client_memory':
                            {'servers':[],'users':[]},
                            'client_config':{}
                            }
        else:
            self.data_mod = content
        self.client_memomry = self.data_mod.setdefault("client_memory", {})
    def remember_linked_server(self, address:tuple):
        if address in (servers:=self.client_memomry.setdefault('servers', [])):
            pass
        else: servers.append(address)

    def remember_logined_user(self, account:tuple):
        self.client_memomry.setdefault('users', []).append((account))

    def save_memory(self):
        self.data_file.w_datafile(self.data_mod)