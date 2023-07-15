# -*- coding: utf-8 -*-
# @Time    : 18/6/2023 下午2:12
# @Author  : LeaVES
# @FileName: MainWindow.py
# coding: utf-8

from PyQt6.QtWidgets import *
from qfluentwidgets import NavigationInterface, FluentIcon, NavigationItemPosition

from scripts.pages import HomePage, FilePage


class MainWindow:
    """主窗口"""
    def __init__(self):
        self.hBoxLayout = QHBoxLayout(self)
        self.navigationInterface = NavigationInterface(self, showMenuButton=True)
        self.stackWidget = QStackedWidget(self)
        self.stackWidget.setStyleSheet("""QLabel{
            font: 13px 'Microsoft YaHei'
            }""")
        # 创建导航栏组件
        self.home_page = HomePage("home")
        self.file_page = FilePage("file")
        # 将导航栏目添加到hBoxLayout
        self.hBoxLayout.setSpacing(0)
        self.hBoxLayout.addWidget(self.navigationInterface)
        self.hBoxLayout.addWidget(self.stackWidget)
        self.hBoxLayout.setStretchFactor(self.stackWidget, 1)
        # 在导航栏添加组件
        self.addSubInterface(self.home_page, FluentIcon.HOME_FILL, "Home", self.stackWidget.setCurrentWidget(self.home_page))
        self.navigationInterface.addSeparator()

    def addSubInterface(self, interface, icon, text: str,function, position=NavigationItemPosition.TOP, parent=None):
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
