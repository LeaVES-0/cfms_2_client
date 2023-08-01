# -*- coding: utf-8 -*-
# @Time    : 18/6/2023 下午2:12
# @Author  : LeaVES
# @FileName: MainWindow.py
# coding: utf-8

from PyQt6.QtCore import QMetaObject, QObject
from PyQt6.QtWidgets import *
from qfluentwidgets import NavigationInterface, NavigationItemPosition

from interface.file_page import FilePage
from interface.home_page import HomePage


class MainWindow(QObject):
    def __init__(self, *args, **kwargs):
        """主窗口"""
        super().__init__()
        QMetaObject.connectSlotsByName(self)
        # 创建导航栏组件
        self.stackWidget = None
        self.hBoxLayout = None
        self.navigationInterface = NavigationInterface(self, showMenuButton=True)
        self.home_page = HomePage("home")
        self.file_page = FilePage("file")
        self.task_page = QWidget()
        self.task_page.setObjectName("task")

    def setup_ui(self, form):
        self.hBoxLayout = QHBoxLayout(form)
        self.stackWidget = QStackedWidget(form)
        self.stackWidget.setStyleSheet("""QLabel{
            font: 13px 'Microsoft YaHei'
            }""")
        # 将导航栏目添加到hBoxLayout
        self.hBoxLayout.setSpacing(0)
        self.hBoxLayout.addWidget(self.navigationInterface)
        self.hBoxLayout.addWidget(self.stackWidget)
        self.hBoxLayout.setStretchFactor(self.stackWidget, 1)

    def addSubInterface(self, interface, icon, function, text: str, position=NavigationItemPosition.TOP, parent=None):
        """ 添加栏目 """
        self.stackWidget.addWidget(interface)
        self.navigationInterface.addItem(
            routeKey=interface.objectName(),
            icon=icon,
            text=text,
            onClick=function,
            position=position,
            tooltip=text,
            parentRouteKey=parent.objectName() if parent else None
        )
