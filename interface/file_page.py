# -*- coding: utf-8 -*-
# @Time    : 13/7/2023 下午1:19
# @Author  : LeaVES
# @FileName: file_page.py
# coding: utf-8

from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from qfluentwidgets import *


# noinspection PyTypeChecker
class PrimaryFilePage:
    """文件管理目录"""

    def __init__(self):
        self.dir_path = ["/"]
        self.rename_arg = False

    def setup_ui(self, args):
        self.get_file_function = args["functions"]["get_file_function"]
        self.file_rename_function = args["functions"]["file_rename_function"]
        self.verticalLayoutWidget = QWidget(self)
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        size_policy = QSizePolicy()
        size_policy.Policy(QSizePolicy.Policy.Preferred)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        self.verticalLayoutWidget.setSizePolicy(size_policy)

        self.verticalLayout = QVBoxLayout(self)  # 全局布局
        self.verticalLayoutWidget.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        # self.verticalLayout.addWidget(self.verticalLayoutWidget)

        self.verticalLayout_0_widget = QWidget(self)  # 这个控件和布局用来装标题和一些其他东西
        self.verticalLayout_0 = QGridLayout(self.verticalLayout_0_widget)
        self.verticalLayout_0.setObjectName("verticalLayout_0")
        # self.verticalLayout_0.addWidget(self.verticalLayout_0_widget)

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
        # self.verticalLayout_2.addWidget(self.verticalLayout_2_widget)

        # self.file_tree = TreeWidget()  # 文件树 #TODO
        # root_item = QTreeWidgetItem()
        # self.file_tree.addTopLevelItem(root_item)
        # root_item.setText(0, "/")
        # self.file_tree.expandAll()
        # self.file_tree.setHeaderHidden(True)
        # self.verticalLayout_2.addWidget(self.file_tree, 2)

        self.table_view = TableWidget()  # 创建表格
        self.table_view.setObjectName("table_file_view")
        self.table_view.setWordWrap(True)
        self.table_view.setColumnCount(5)
        self.table_view.cellDoubleClicked.connect(self.file_action)
        self.table_view.cellChanged.connect(self.rename_action)
        self.table_view.clear()

        # 允许打开上下文菜单
        self.table_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        # 绑定事件
        self.table_view.customContextMenuRequested.connect(self.file_list_button)
        self.table_view.verticalHeader().hide()  # 表头
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_view.verticalHeader().setDefaultSectionSize(60)
        self.verticalLayout_2.addWidget(self.table_view, 5)
        self.table_view.setContentsMargins(10, 100, 0, 0)

        self.verticalLayout.addWidget(self.verticalLayout_0_widget)
        self.verticalLayout.addWidget(self.verticalLayout_2_widget)

    def file_list_button(self, pos):
        """文件按键"""
        selected_item = 0
        for i in self.table_view.selectionModel().selection().indexes():
            selected_item = i.row()
        screen_pos = self.table_view.mapToGlobal(pos)  # 转换坐标系
        list_item_menu = RoundMenu(self)
        copy_action = Action(FluentIcon.COPY, text='Copy')
        cut_action = Action(FluentIcon.CUT, text='Cut')
        list_item_menu.addActions([copy_action, cut_action])
        list_item_menu.exec(screen_pos, ani=True)

    def set_file_tree_list(self, files):
        self.rename_arg = False
        self.__set_files_list(files[0])
        # self.__set_files_tree(files[1])

    def __set_files_tree(self, dirs):
        """文件树"""
        ...

    @staticmethod
    def __create_list_item(info, variable: bool = False):
        """设置单元格"""
        item = QTableWidgetItem(info)
        if not variable:
            item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
        return item

    def __set_files_list(self, files: list):
        """设置文件列表"""
        self.file_information = files
        self.table_view.clear()
        self.table_view.setRowCount(len(self.file_information))
        self.table_view.verticalHeader().setDefaultSectionSize(60)
        # 批量设置表格项
        for row, file_info in enumerate(self.file_information):
            for column in range(5):
                if column == 0:
                    self.table_view.setItem(row, column, self.__create_list_item(file_info[column], True))
                else:
                    self.table_view.setItem(row, column, self.__create_list_item(file_info[column]))
        self.table_view.setHorizontalHeaderLabels(['FileName', 'Type', 'Size', 'Create Date', 'Permission'])  # 行标题

    def file_action(self, row, column):
        self.rename_arg = True
        file_obj = self.file_information[row]
        print("clicked:", file_obj)
        if not column == 0:
            if file_obj[1] == "dir":
                self.get_file_function(False, file_obj[5])

    def rename_action(self, row, column):
        if self.rename_arg:
            file_obj = self.file_information[row]
            data = str(self.table_view.item(row, column).text())
            self.file_rename_function(data, file_obj[5], file_obj[1])
            self.rename_arg = False
