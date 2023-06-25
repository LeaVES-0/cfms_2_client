# -*- coding: utf-8 -*-
# @Time    : 18/6/2023 下午2:12
# @Author  : LeaVES
# @FileName: LoginWindow.py
# coding: utf-8

from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from qfluentwidgets import *
from qfluentwidgets import FluentIcon as FIF


class Widget(QFrame):
    # example
    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.label = QLabel(text, self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.addWidget(self.label, 1, Qt.AlignmentFlag.AlignCenter)
        self.setObjectName(text.replace(' ', '-'))


# class MainWindow(FramelessWindow):
class MainWindow:
    """主窗口"""
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

    def setup_ui(self, window_form):
        """window_form是供ui.py统一设置使用的实参"""
        window_form.setObjectName("Form")
        self.hBoxLayout = QHBoxLayout(window_form)
        self.navigationInterface = NavigationInterface(self, showMenuButton=True)
        self.stackWidget = QStackedWidget(window_form)
        # 创建导航栏组件
        self.mainInterface = Widget("精致的界面")
        self.settingInterface = Widget("设置")
        # 将导航栏目添加到hBoxLayout
        self.hBoxLayout.setSpacing(0)
        self.hBoxLayout.addWidget(self.navigationInterface)
        self.hBoxLayout.addWidget(self.stackWidget)
        self.hBoxLayout.setStretchFactor(self.stackWidget, 1)
        # 在导航栏添加组件
        self.navigationInterface.addSeparator()
        self.addSubInterface(self.mainInterface, FIF.LAYOUT, "主界面", position=NavigationItemPosition.SCROLL)
        self.addSubInterface(self.settingInterface, FIF.SETTING, "设置", position=NavigationItemPosition.BOTTOM)


