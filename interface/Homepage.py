#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 18/6/2023 下午2:12
# @Author  : LeaVES
# @FileName: Homepage.py
# coding: utf-8

from PyQt6 import QtCore, QtGui, QtWidgets
from qfluentwidgets import *
from qfluentwidgets.components.widgets.acrylic_label import AcrylicLabel
import sys

class PrimeryHomePage:
    def __init__(self):
        self.verticalLayoutWidget = QtWidgets.QWidget(parent=self)
        # self.verticalLayoutWidget.setGeometry(QtCore.QRect(0, 0, 1500, 1000))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.titltLabel = QtWidgets.QLabel()
        self.titltLabel.setText("CFMS  2")
        self.titltLabel.setContentsMargins(40, 30, 0, 0)
        self.titltLabel.setStyleSheet(
            """QLabel{
            font: 45px 'Microsoft YaHei';
            color: black
            }"""
        )
        # self.titltLabel.setContentsMargins(50, 40, 0, 0)
        self.verticalLayout.addWidget(self.titltLabel)