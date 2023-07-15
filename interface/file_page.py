# -*- coding: utf-8 -*-
# @Time    : 13/7/2023 下午1:19
# @Author  : LeaVES
# @FileName: file_page.py
# coding: utf-8

from PyQt6 import QtCore, QtGui, QtWidgets
from qfluentwidgets import *


# noinspection PyTypeChecker
class PrimaryFilePage:
    """文件管理目录"""

    def __init__(self):
        self.verticalLayoutWidget = QtWidgets.QWidget(self)
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QGridLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.titleLabel = QtWidgets.QLabel()
        self.titleLabel.setText("文件管理")
        self.titleLabel.setStyleSheet(
            """QLabel{
            font: 45px 'Microsoft YaHei';
            }"""
        )
        self.titleLabel.setContentsMargins(30, 20, 0, 0)
        self.verticalLayout.addWidget(self.titleLabel)
        file_information = [
            ['1', 'leaf', 'leaf', '2004', '5:04'],
            ['1', 'leaf', 'leaf', '2004', '3:39'],
            ['1', 'leaf', 'leaf/leaf', '2007', '5:30'],
            ['1', 'leaf', 'leaf/leaf', '2007', '5:06'],
            ['1', 'leaf', 'leaf', '2008', '6:27'],
        ]
        self.file_tree = TreeWidget(self)
        self.__file_tree()
        self.table_view = TableWidget(self)  # 创建表格
        self.table_view.setObjectName("table_view")

    def file_list_button(self, row, column):
        list_item_menu = RoundMenu(self)
        # add actions
        list_item_menu.addAction(copy := (Action(FluentIcon.COPY, text='Copy')))
        list_item_menu.addAction(cut := (Action(FluentIcon.CUT, text='Cut')))

        # add sub menu
        list_item_menu.addSeparator()
        # add actions
        list_item_menu.addActions([
            paste := (Action(FluentIcon.PASTE, text='Paste')),
            rename := (Action(FluentIcon.ALIGNMENT, text='Rename'))
        ])

        # add separator
        list_item_menu.addSeparator()
        list_item_menu.exec(QtGui.QCursor.pos(), ani=True)

    def __file_tree(self):
        item1 = QtWidgets.QTreeWidgetItem()
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
        item = QtWidgets.QTableWidgetItem(info)
        item.setFlags(QtCore.Qt.ItemFlag.ItemIsSelectable | QtCore.Qt.ItemFlag.ItemIsEnabled)
        return item

    def __list_files(self, file_information: list):
        self.table_view.setWordWrap(True)
        self.table_view.setRowCount(len(file_information))
        self.table_view.setColumnCount(5)
        self.table_view.cellDoubleClicked.connect(self.file_list_button)  # Qt右键打开在此处实现过于复杂
        # 批量设置表格项
        for row, file_info in enumerate(file_information):
            for column in range(5):
                self.table_view.setItem(row, column, self.__create_list_item(file_info[column]))
        self.table_view.verticalHeader().hide()  # 表头
        self.table_view.setHorizontalHeaderLabels(['FileName', '类型', '大小', '修改日期', '权限'])  # 行标题
        self.table_view.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)



