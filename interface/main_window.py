# -*- coding: utf-8 -*-
# @Time    : 18/6/2023 下午2:12
# @Author  : LeaVES
# @FileName: MainWindow.py
# coding: utf-8

from PyQt6.QtWidgets import *
from qfluentwidgets import *
from qfluentwidgets import FluentIcon as FIF

from scripts.pages import HomePage


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
        self.mainInterface = HomePage()
        self.settingInterface = HomePage()
        # 将导航栏目添加到hBoxLayout
        self.hBoxLayout.setSpacing(0)
        self.hBoxLayout.addWidget(self.navigationInterface)
        self.hBoxLayout.addWidget(self.stackWidget)
        self.hBoxLayout.setStretchFactor(self.stackWidget, 1)
        # 在导航栏添加组件
        self.navigationInterface.addSeparator()
        self.addSubInterface(self.mainInterface, FIF.LAYOUT, "主界面", position=NavigationItemPosition.SCROLL)
        self.addSubInterface(self.settingInterface, FIF.SETTING, "设置", position=NavigationItemPosition.BOTTOM)

    def addSubInterface(self, interface, icon, text: str, position=NavigationItemPosition.TOP, parent=None):
        """ 添加栏目 """
        self.stackWidget.addWidget(interface)
        self.navigationInterface.addItem(
            routeKey=interface.objectName(),
            icon=icon,
            text=text,
            onClick=lambda: self.stackWidget.setCurrentWidget(interface),
            position=position,
            tooltip=text,
            parentRouteKey=parent.objectName() if parent else None
        )
