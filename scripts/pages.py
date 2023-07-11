#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 18/6/2023 下午10:18
# @Author  : LeaVES
# @FileName: pages.py
# coding: utf-8

from PyQt6.QtCore import QMetaObject
from PyQt6.QtWidgets import *
from qfluentwidgets import *
from qfluentwidgets.components.widgets.acrylic_label import AcrylicLabel

from interface.homepage import PrimeryHomePage

RESOURCE_IMAGES = "interface/resource/images/"


class ShowPages(QWidget):
    def __init__(self):
        super().__init__()
        self.pageBackground = AcrylicLabel(blurRadius=10, tintColor=QColor(105, 114, 168, 102), parent=self)
        self.pageBackground.setImage(f"{RESOURCE_IMAGES}login_b.jpg")
        self.pageBackground.setObjectName("background")
        self.pageBackground.setFixedHeight(200)
        QMetaObject.connectSlotsByName(self)


class HomePage(ShowPages, PrimeryHomePage):
    def __init__(self):
        super(HomePage, self).__init__()
        self.pageBackground.lower()
