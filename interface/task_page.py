# -*- coding: utf-8 -*-
# @Time    : 2/8/2023 下午9:11
# @Author  : LeaVES
# @FileName: file_page.py
# coding: utf-8

from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from qfluentwidgets import *


class TaskTabelView(QWidget):
    def __init__(self, obj_name):
        super().__init__()
        self.main_layout = QVBoxLayout(self)
        self.table_view = TableWidget()  # 创建表格
        self.table_view.setWordWrap(True)
        self.table_view.setHorizontalHeaderLabels(['TaskName', 'Progress'])  # 行标题
        # self.table_view.cellDoubleClicked.connect()
        # self.table_view.cellChanged.connect()
        self.table_view.clear()
        self.table_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table_view.verticalHeader().hide()
        self.table_view.verticalHeader().setDefaultSectionSize(60)
        self.table_view.customContextMenuRequested.connect(self.file_list_button)
        self.table_view.setContentsMargins(10, 100, 0, 0)
        self.table_view.setColumnCount(2)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_view.setHorizontalHeaderLabels(['Task', 'Progress'])
        self.setObjectName(obj_name)
        self.main_layout.addWidget(self.table_view)

    def __call__(self):
        return self

    def file_list_button(self, pos):
        """文件右键"""
        row = 0
        for i in self.table_view.selectionModel().selection().indexes():
            row = i.row()

    @staticmethod
    def __create_list_item(info, obj_type: str = "download"):
        """设置单元格"""
        item = QTableWidgetItem(info)
        item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
        if obj_type == "download":
            item.setIcon(FluentIcon.DOWNLOAD.icon())
        elif obj_type == "upload":
            item.setIcon(FluentIcon.UPDATE.icon())
        return item

    def __set_tasks_list(self, files: list):
        """设置文件列表"""
        self.table_view.clear()
        self.table_view.setRowCount(len(files))
        self.file_information = files
        # 批量设置表格项
        if not files:
            self.table_view.setColumnCount(1)
            self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            self.table_view.setHorizontalHeaderLabels(["No Task"])  # 行标题
        elif files:
            self.table_view.setColumnCount(2)
            self.table_view.verticalHeader().setDefaultSectionSize(60)
            self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            self.table_view.setHorizontalHeaderLabels(['Task', 'Create Time', 'Progress', 'Action'])
            for row, file_info in enumerate(self.file_information):
                for column in range(0, 2):
                    self.table_view.setItem(row, column, self.__create_list_item(column))


class TaskPage(QWidget):
    """任务管理目录"""

    def __init__(self, object_name):
        super().__init__(None)
        self.setObjectName(object_name)

    def setup_ui(self, functions=None):
        super().__init__(self)
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
