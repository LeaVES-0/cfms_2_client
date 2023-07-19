# -*- coding: utf-8 -*-
# @Time    : 13/7/2023 下午1:19
# @Author  : LeaVES
# @FileName: file_page.py
# coding: utf-8

from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
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
        self.verticalLayout = QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.titleLabel = QLabel()
        self.titleLabel.setText("文件管理")
        self.titleLabel.setStyleSheet(
            """QLabel{
            font: 45px 'Microsoft YaHei';
            }"""
        )
        self.titleLabel.setContentsMargins(30, 20, 0, 0)
        self.verticalLayout.addWidget(self.titleLabel)
        self.file_tree = TreeWidget(self)
        self.__file_tree()
        self.table_view = TableWidget(self)  # 创建表格
        self.table_view.setObjectName("table_view")

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
        item1 = QTreeWidgetItem()
        # item1.addChildren([QtWidgets.QTreeWidgetItem('file_1')])

        self.file_tree.addTopLevelItem(item1)
        item1.setText(0, "/")
        # item2 = QtWidgets.QTreeWidgetItem(['folder_2'])
        # item21 = QtWidgets.QTreeWidgetItem(['file_2'])
        # item21.addChildren([])
        # item2.addChild(item21)
        # self.file_tree.addTopLevelItem(item2)

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
        self.table_view.setWordWrap(True)
        self.table_view.setRowCount(len(file_information))
        self.table_view.setColumnCount(5)
        self.table_view.cellDoubleClicked.connect(self.file_list_button)  # Qt右键打开在此处实现过于复杂
        # 批量设置表格项
        for row, file_info in enumerate(file_information):
            for column in range(5):
                self.table_view.setItem(row, column, self.__create_list_item(file_info[column]))
        self.table_view.verticalHeader().hide()  # 表头
        self.table_view.setHorizontalHeaderLabels(['FileName', 'Type', 'Size', 'Create Date', 'Permission'])  # 行标题
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
