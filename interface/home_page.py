#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 18/6/2023 下午2:12
# @Author  : LeaVES
# @FileName: Homepage.py
# coding: utf-8

from PyQt6.QtWidgets import *
from scripts.uie import CardView
from qfluentwidgets import FluentIcon


class HomePage(QWidget):
    def __init__(self, object_name):
        super().__init__(None)
        self.setObjectName(object_name)

    def setup_ui(self, args=None):
        self.verticalLayoutWidget = QWidget(parent=self)
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.main_layout = QVBoxLayout(self.verticalLayoutWidget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setObjectName("verticalLayout")
        self.titleLabel = QLabel()
        self.titleLabel.setText("CFMS  2")
        self.titleLabel.setStyleSheet(
            """QLabel{
            font: 45px 'Microsoft YaHei';
            }"""
        )
        self.titleLabel.setContentsMargins(30, 20, 0, 0)
        self.main_layout.addWidget(self.titleLabel)
        self.titleLabel_s = QLabel()
        self.titleLabel_s.setText("Classified File Management System")
        self.titleLabel_s.setStyleSheet(
            """QLabel{
            font: 12px 'Microsoft YaHei';
            }"""
        )
        self.titleLabel_s.setContentsMargins(30, 0, 0, 0)
        self.main_layout.addWidget(self.titleLabel_s)

        self.CardView = CardView(self)

        self.main_layout.addWidget(self.CardView)

        self.CardView.addCard(
            FluentIcon.GITHUB,
            self.tr('GitHub (Server)'),
            self.tr('在Github获取服务端最新版本'),
            "https://github.com/Creeper19472/cfms_2"
        )

        self.CardView.addCard(
            FluentIcon.GITHUB,
            self.tr('GitHub (Client)'),
            self.tr('在Github获取客户端最新版本'),
            "https://github.com/LeaVES-0/cfms_2_client"
        )

        self.CardView.addCard(
            FluentIcon.CODE,
            self.tr('Code'),
            self.tr('开发指南'),
            "https://cfms-server-doc.readthedocs.io/zh_CN/latest"
        )