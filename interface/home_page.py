#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 18/6/2023 下午2:12
# @Author  : LeaVES
# @FileName: Homepage.py
# coding: utf-8

from PyQt6.QtWidgets import *


class HomePage(QWidget):
    def __init__(self, object_name):
        super().__init__(None)
        self.setObjectName(object_name)

    def setup_ui(self, args=None):
        self.verticalLayoutWidget = QWidget(parent=self)
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.titleLabel = QLabel()
        self.titleLabel.setText("CFMS  2")
        self.titleLabel.setStyleSheet(
            """QLabel{
            font: 45px 'Microsoft YaHei';
            }"""
        )
        self.titleLabel.setContentsMargins(30, 20, 0, 0)
        self.verticalLayout.addWidget(self.titleLabel)
        self.titleLabel_s = QLabel()
        self.titleLabel_s.setText("Classified File Management System")
        self.titleLabel_s.setStyleSheet(
            """QLabel{
            font: 12px 'Microsoft YaHei';
            }"""
        )
        self.titleLabel_s.setContentsMargins(30, 0, 0, 0)
        self.verticalLayout.addWidget(self.titleLabel_s)
