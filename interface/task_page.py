# -*- coding: utf-8 -*-
# @Time    : 2/8/2023 下午9:11
# @Author  : LeaVES
# @FileName: file_page.py
# coding: utf-8

from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from qfluentwidgets import *

class TaskBarObj(QWidget):
    ...

class TaskTabelView(QWidget):
    def __init__(self, obj_name):
        super().__init__()
        self.task_information = []
        self.main_layout = QVBoxLayout(self)

        self.setObjectName(obj_name)
    
    def addTaskObj(self):
        task_obj = TaskBarObj()
        self.main_layout.addWidget()



class TaskPage(QWidget):
    """任务管理目录"""

    def __init__(self, *args, **kwargs):
        super().__init__(None)
        try:
            self.functions = kwargs["functions"]
        except KeyError:
            self.functions = {}
        self.setObjectName(kwargs["name"])

    def connect_signal_solt(self, functions: dict):
        self.functions.update(functions)

    def setup_ui(self, *args, **kwargs):
        super().__init__(self)

        self.connect_signal_solt(self.functions)

        size_policy = QSizePolicy()
        size_policy.Policy(QSizePolicy.Policy.Preferred)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        self.setSizePolicy(size_policy)

        self.verticalLayout = QVBoxLayout()  # 全局布局
        self.setLayout(self.verticalLayout)
        self.verticalLayout.setObjectName("verticalLayout")

        self.verticalLayout_0_widget = QWidget(self)  # 这个控件和布局用来装标题和一些其他东西
        self.verticalLayout_0 = QGridLayout(None)
        self.verticalLayout_0_widget.setLayout(self.verticalLayout_0)
        self.verticalLayout_0.setObjectName("verticalLayout_0")

        self.titleLabel = QLabel()  # 页面标题
        self.titleLabel.setText("Tasks")
        self.titleLabel.setStyleSheet(
            """QLabel{
            font: 45px 'Microsoft YaHei';
            }"""
        )
        self.titleLabel.setContentsMargins(30, 20, 0, 0)
        self.verticalLayout_0.addWidget(self.titleLabel, 1, 0, 1, 2)

        self.pivot = Pivot(self)
        self.stackedWidget = QStackedWidget(self)

        # add items to pivot
        self.download_page = TaskTabelView("Download_p")
        self.upload_page = TaskTabelView("Upload_p")
        self.addSubInterface(self.download_page, 'Download_p', 'Download')
        self.addSubInterface(self.upload_page, 'Upload_p', 'Upload')
        self.stackedWidget.currentChanged.connect(self.onCurrentIndexChanged)
        self.stackedWidget.setCurrentWidget(self.download_page)

        self.pivot.setCurrentItem(self.download_page.objectName())
        self.verticalLayout_0.addWidget(self.pivot, 1, 3, Qt.AlignmentFlag.AlignRight)

        self.verticalLayout.addWidget(self.verticalLayout_0_widget)
        self.verticalLayout.addWidget(self.stackedWidget)

    def addSubInterface(self, widget, object_name, text):
        # widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.stackedWidget.addWidget(widget)
        self.pivot.addItem(
            routeKey=object_name,
            text=text,
            onClick=lambda: self.stackedWidget.setCurrentWidget(widget)
        )

    def onCurrentIndexChanged(self, index):
        widget = self.stackedWidget.widget(index)
        self.pivot.setCurrentItem(widget.objectName())
