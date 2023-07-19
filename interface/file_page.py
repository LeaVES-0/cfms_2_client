# -*- coding: utf-8 -*-
# @Time    : 13/7/2023 下午1:19
# @Author  : LeaVES
# @FileName: file_page.py
# coding: utf-8

from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from qfluentwidgets import *


# noinspection PyTypeChecker
class PrimaryFilePage:
    """文件管理目录"""

    def __init__(self):
        self.verticalLayoutWidget = QWidget(self)
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        size_policy = QSizePolicy()
        size_policy.Policy(QSizePolicy.Policy.Preferred)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        self.verticalLayoutWidget.setSizePolicy(size_policy)

        self.verticalLayout = QVBoxLayout(self.verticalLayoutWidget)  # 全局布局
        self.verticalLayoutWidget.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")

        self.verticalLayout_0_widget = QWidget(self)  # 这个控件和布局用来装标题和一些其他东西
        self.verticalLayout_0 = QGridLayout(self.verticalLayout_0_widget)
        self.verticalLayout_0.setObjectName("verticalLayout_0")

        self.titleLabel = QLabel()  # 页面标题
        self.titleLabel.setText("Files")
        self.titleLabel.setStyleSheet(
            """QLabel{
            font: 45px 'Microsoft YaHei';
            }"""
        )
        self.titleLabel.setContentsMargins(30, 20, 0, 0)
        self.verticalLayout_0.addWidget(self.titleLabel)

        self.verticalLayout_2_widget = QWidget(self)  # 这个控件和布局用来装文件树和文件目录
        self.verticalLayout_2 = QHBoxLayout(self.verticalLayout_2_widget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")

        self.file_tree = TreeWidget() # 文件树
        self.__file_tree()
        self.verticalLayout_2.addWidget(self.file_tree, 2)

        self.table_view = TableWidget()  # 创建表格
        self.table_view.setObjectName("table_file_view")
        self.table_view.setWordWrap(True)
        self.table_view.setColumnCount(5)
        self.table_view.cellDoubleClicked.connect(self.file_list_button)  # Qt右键打开在此处实现过于复杂
        self.table_view.verticalHeader().hide()  # 表头
        self.table_view.setHorizontalHeaderLabels(['FileName', 'Type', 'Size', 'Create Date', 'Permission'])  # 行标题
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.verticalLayout_2.addWidget(self.table_view, 5)

        self.verticalLayout.addWidget(self.verticalLayout_0_widget)
        self.verticalLayout.addWidget(self.verticalLayout_2_widget)

    def file_list_button(self, row, column):
        """文件按键"""
        list_item_menu = RoundMenu(self)
        # add actions
        copy_action = Action(FluentIcon.COPY, text='Copy')
        cut_action = Action(FluentIcon.CUT, text='Cut')
        list_item_menu.addActions([copy_action, cut_action])
        list_item_menu.addSeparator()
        list_item_menu.exec(QCursor.pos(None), ani=True)

    def __file_tree(self):
        """文件树"""
        root_item = QTreeWidgetItem()

        self.file_tree.addTopLevelItem(root_item)
        root_item.setText(0, "/")

        self.file_tree.expandAll()
        self.file_tree.setHeaderHidden(True)

    @staticmethod
    def __create_list_item(info):
        """设置单元格"""
        item = QTableWidgetItem(info)
        item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
        return item

    def list_files(self, file_information: list):
        """设置文件列表"""
        self.table_view.setRowCount(len(file_information))
        # 批量设置表格项
        for row, file_info in enumerate(file_information):
            for column in range(5):
                self.table_view.setItem(row, column, self.__create_list_item(file_info[column]))
