#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 18/6/2023 下午10:18
# @Author  : LeaVES
# @FileName: pages.py
# coding: utf-8

from PyQt6.QtCore import QMetaObject
from PyQt6.QtWidgets import *
from qfluentwidgets import *

from interface.home_page import PrimaryHomePage
from interface.file_page import PrimaryFilePage

RESOURCE_IMAGES = "interface/resource/images/"


class ShowPages(QWidget):
    def __init__(self):
        super().__init__()
        QMetaObject.connectSlotsByName(self)
        self.loadProgressBar = IndeterminateProgressBar(self)

    def resizeEvent(self, e):
        self.loadProgressBar.setGeometry(0, 0, self.width(), 10)


class HomePage(ShowPages, PrimaryHomePage):
    def __init__(self, object_name):
        super(HomePage, self).__init__()
        self.setObjectName(object_name)


class FilePage(ShowPages, PrimaryFilePage):
    def __init__(self, object_name):
        super(FilePage, self).__init__()
        self.setObjectName(object_name)

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self.file_tree.setGeometry(0, 170, 250, self.height())
        self.table_view.setGeometry(275, 180, self.width()-275, 5000)

