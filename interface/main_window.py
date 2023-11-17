# -*- coding: utf-8 -*-
# @Time    : 18/6/2023 下午2:12
# @Author  : LeaVES
# @FileName: MainWindow.py
# coding: utf-8

from PyQt6.QtCore import QMetaObject
from PyQt6.QtWidgets import *
from qfluentwidgets import NavigationInterface, NavigationItemPosition

from util.uie.base import CfmsUIBase
from interface.file_page import FilePage
from interface.home_page import HomePage
from interface.task_page import TaskPage


class MainWindow(CfmsUIBase):
    GET_FILES = "get_files_function"
    RENAME_FILE = "rename_file_function"
    DOWNLOAD_FILE = "download_file_function"
    DELETE_FILE = "delete_file_function"
    UPLOAD_FILE = "upload_file_function"
    CREATE_NEW_FOLDER = "create_new_dir_function"

    def __init__(self, *args, **kwargs):
        """主窗口"""
        super().__init__()
        QMetaObject.connectSlotsByName(self)
        self.setObjectName("CFMS_Main_Window")
        # 创建导航栏组件
        self.navigationInterface = NavigationInterface(self, showMenuButton=True)
        self.home_page = HomePage(name="home")
        self.file_page = FilePage(name="file")
        self.task_page = TaskPage(name="task")
        self.pages = [self.home_page, self.file_page, self.task_page]
        self.setup_ui()

    def setup_ui(self):
        self.hBoxLayout = QHBoxLayout(self)
        self.stackWidget = QStackedWidget(self)
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
