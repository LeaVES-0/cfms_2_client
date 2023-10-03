#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 18/6/2023 下午5:24
# @Author  : LeaVES
# @FileName: main.py
# coding: utf-8
from controller.cfms_main import MainClient
from PyQt6.QtWidgets import QMessageBox

def main():
    client = MainClient()
    client.run()

if __name__ == '__main__':
    # try:
    main()
    # except Exception as e:
    #     msg_box = QMessageBox(QMessageBox.Icon.Warning, 'ERROR', 'cfms意外退出', QMessageBox.StandardButton.Yes)
    #     msg_box.exec()


