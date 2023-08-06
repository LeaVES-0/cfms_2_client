# -*- coding: utf-8 -*-
# @Time    : 13/7/2023 下午1:19
# @Author  : LeaVES
# @FileName: file_page.py
# coding: utf-8

import os.path

from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from qfluentwidgets import *

from scripts.method import info_message_display, FILE_TYPES


# noinspection PyTypeChecker
class FilePage(QWidget):
    """文件管理目录"""

    def __init__(self, object_name):
        super().__init__(None)
        self.setObjectName(object_name)
        self.file_information = []
        self.path = [('', '<ROOT>'), ]
        self.current_path = ('', '<ROOT>')
        self.rename_arg = False
        self.loadProgressBar = IndeterminateProgressBar(self, start=False)

    def setup_ui(self, functions=None):
        self.get_files_function = functions["get_files_function"]
        self.file_rename_function = functions["rename_file_function"]
        self.download_file_function = functions["download_file_function"]
        self.delete_file_function = functions["delete_file_function"]
        self.upload_new_file_function = functions["upload_file_function"]
        self.create_new_dir_function = functions["create_new_dir_function"]
        size_policy = QSizePolicy()
        size_policy.Policy(QSizePolicy.Policy.Preferred)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        self.setSizePolicy(size_policy)

        self.verticalLayout = QVBoxLayout()  # 全局布局
        self.setLayout(self.verticalLayout)
        # self.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout.addWidget(self.loadProgressBar)

        self.verticalLayout_0_widget = QWidget(self)  # 这个控件和布局用来装标题和一些其他东西
        self.verticalLayout_0 = QGridLayout(None)
        self.verticalLayout_0_widget.setLayout(self.verticalLayout_0)
        # self.verticalLayout_0.setHorizontalSpacing(10)
        self.verticalLayout_0.setObjectName("verticalLayout_0")

        self.titleLabel = QLabel()  # 页面标题
        self.titleLabel.setText("Files")
        self.titleLabel.setStyleSheet(
            """QLabel{
            font: 45px 'Microsoft YaHei';
            }"""
        )
        self.titleLabel.setContentsMargins(30, 20, 0, 0)
        self.verticalLayout_0.addWidget(self.titleLabel, 1, 0, 1, 4)

        self.back_dir_button = ToolButton(FluentIcon.CARE_LEFT_SOLID, self)  # 上一级,下一级
        self.next_dir_button = ToolButton(FluentIcon.CARE_RIGHT_SOLID, self)
        layout_0 = QHBoxLayout()  #
        layout_0_widget = QWidget(self)
        layout_0.addWidget(self.back_dir_button, 1)
        self.back_dir_button.clicked.connect(lambda: self.change_dir_level(True))
        layout_0.addWidget(self.next_dir_button, 1)
        layout_0_widget.setLayout(layout_0)
        self.verticalLayout_0.addWidget(layout_0_widget, 2, 0, Qt.AlignmentFlag.AlignRight)

        # 创建新文件Button
        self.create_new_button = PrimaryDropDownPushButton(text='New', icon=FluentIcon.ADD)
        create_new_menu = RoundMenu(self)
        create_file_action = Action(FluentIcon.DOCUMENT, text='Create file')
        create_folder_action = Action(FluentIcon.FOLDER_ADD, text='Create folder')
        create_folder_action.triggered.connect(self.create_new_dir_function)
        create_new_menu.addActions([create_file_action, create_folder_action])
        self.create_new_button.setMenu(create_new_menu)
        # 上传Button
        self.upload_button = PrimaryDropDownPushButton(text='Upload', icon=FluentIcon.UP)
        upload_menu = RoundMenu(self)
        upload_file_action = Action(FluentIcon.DOCUMENT, text='Upload file')
        upload_file_action.triggered.connect(self.choose_file)
        upload_folder_action = Action(FluentIcon.FOLDER_ADD, text='Upload folder')
        upload_menu.addActions([upload_file_action, upload_folder_action])
        self.upload_button.setMenu(upload_menu)

        layout_1 = QHBoxLayout()  #
        layout_1_widget = QWidget(self)
        layout_1.addWidget(self.create_new_button, 1)
        layout_1.addWidget(self.upload_button, 1)
        layout_1_widget.setLayout(layout_1)
        self.verticalLayout_0.addWidget(layout_1_widget, 2, 5, Qt.AlignmentFlag.AlignRight)

        # 这个控件和布局用来装文件树和文件目录
        self.verticalLayout_2_widget = QWidget(self)
        self.verticalLayout_2 = QHBoxLayout()
        self.verticalLayout_2_widget.setLayout(self.verticalLayout_2)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        # 文件列表
        self.table_view = TableWidget()
        self.table_view.setObjectName("table_file_view")
        self.table_view.setWordWrap(True)
        self.table_view.setHorizontalHeaderLabels(['', 'FileName', 'Type', 'Size', 'Create Date', 'Permission'])  # 行标题
        self.table_view.cellDoubleClicked.connect(self.cellDoubleClicked_action)
        self.table_view.cellChanged.connect(self.rename_action)
        self.table_view.clear()
        # 允许打开上下文菜单
        self.table_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        # 表头
        self.table_view.verticalHeader().hide()
        self.table_view.verticalHeader().setDefaultSectionSize(60)
        self.table_view.customContextMenuRequested.connect(self.file_list_button)
        self.table_view.setContentsMargins(10, 100, 0, 0)
        self.table_view.setColumnCount(5)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_view.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.verticalLayout_2.addWidget(self.table_view, 5)

        # 在全局布局里嵌套布局
        self.verticalLayout.addWidget(self.verticalLayout_0_widget)
        self.verticalLayout.addWidget(self.verticalLayout_2_widget)

    def choose_file(self):
        get_filename_path, ok = QFileDialog.getOpenFileName(self, "选取单个文件", "C:/", "All Files (*);")
        if ok:
            self.upload_new_file_function(get_filename_path)
        else:
            info_message_display(self, information_type="info", whereis="TOP_LEFT", title="已取消", )

    def file_list_button(self, pos):
        """文件右键"""
        row = 0
        for i in self.table_view.selectionModel().selection().indexes():
            row = i.row()
        if self.file_information:
            if self.file_information[row]:
                file_type = self.file_information[row]["type"]
                screen_pos = self.table_view.mapToGlobal(pos)  # 转换坐标系
                self.list_item_menu = RoundMenu(self)
                copy_action = Action(FluentIcon.COPY, text='Copy')
                cut_action = Action(FluentIcon.CUT, text='Cut')
                delete_action = Action(FluentIcon.REMOVE_FROM, text="Delete")
                self.list_item_menu.addActions([copy_action, cut_action, delete_action])
                self.list_item_menu.addSeparator()
                download_file_action = Action(FluentIcon.DOWNLOAD, text="Download")
                download_folder_action = Action(FluentIcon.DOWNLOAD, text="Download")
                if file_type == "file":
                    self.list_item_menu.addAction(download_file_action)
                elif file_type == "dir":
                    self.list_item_menu.addAction(download_folder_action)
                download_file_action.triggered.connect(lambda: self.download_file_function(file_index=row))
                delete_action.triggered.connect(lambda: self.delete_file_function(file_index=row))
                self.list_item_menu.exec(screen_pos, ani=True)

    def set_file_tree_list(self, files):
        self.rename_arg = False
        self.__set_files_list(files)

    def __set_files_tree(self, dirs):
        """文件树"""
        ...

    @staticmethod
    def __create_list_item(info, column, obj_type: str = "file"):
        """设置单元格"""
        item = QTableWidgetItem(info)
        if column != 0:
            item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
        else:
            if obj_type == "dir":
                item.setIcon(FluentIcon.FOLDER.icon())
            elif obj_type == "file":
                item.setIcon(FluentIcon.DOCUMENT.icon())
            item.setToolTip(info)
        return item

    # @signal_blocker
    def __set_files_list(self, files: list):
        """设置文件列表"""
        self.table_view.blockSignals(True)
        self.loadProgressBar.stop()
        self.table_view.verticalHeader().setDefaultSectionSize(60)
        if files == self.file_information:
            self.table_view.blockSignals(False)
            return
        self.file_information = files
        self.table_view.clear()
        # 批量设置表格项
        if not files:
            self.table_view.setColumnCount(1)
            self.table_view.setRowCount(0)
            self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            self.table_view.setHorizontalHeaderLabels(["This folder is empty."])  # 行标题
        elif files:
            self.table_view.setColumnCount(5)
            self.table_view.setRowCount(len(files))
            self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            self.table_view.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
            self.table_view.setHorizontalHeaderLabels(['Name', 'Date created', 'Type', 'Size', 'Permission'])
            for row, file_info in enumerate(self.file_information):
                for column in range(5):
                    file_info_list = [file_info["name"], file_info["time_created"],
                                      file_info["specific_type"], file_info["size_transformed"],
                                      file_info["permission"]]
                    self.table_view.setItem(row, column,
                                            self.__create_list_item(file_info_list[column], column, file_info["type"]))
        self.table_view.blockSignals(False)

    def change_dir_level(self, action: bool):
        if action:
            if len(self.path) > 1:
                self.current_path = self.path[-2]
                del self.path[-1]
                self.get_files_function(self.current_path[0])
            else:
                self.current_path = ('', '<ROOT>')
                self.get_files_function()

    def cellDoubleClicked_action(self, row, column):
        """双击事件处理"""
        if not column == 0:
            if self.file_information[row]["type"] == "dir":
                dir_id = self.file_information[row].get("file_id", "")
                dir_name = self.file_information[row].get("name", "")
                self.get_files_function(dir_id)
                self.current_path = (dir_id, dir_name)
                self.path.append(self.current_path)

    # @signal_blocker
    def rename_action(self, row, column):
        """rename"""
        self.table_view.blockSignals(True)
        data = str(self.table_view.item(row, column).text())
        self.file_information[row]["name"] = data
        self.file_rename_function(data=data, file_index=row)
        if self.file_information[row]["type"] == "file":
            _type = os.path.splitext(data)[-1].strip(".").lower()
            file_type = self.file_information[row]["specific_type"] = FILE_TYPES.get(_type, _type + " File")
            self.table_view.item(row, 2).setText(file_type)
        self.table_view.blockSignals(False)

    def create_new_file_action(self, file_type: str = "folder"):
        """新建文件夹"""
        self.create_new_arg = True
        self.file_information.insert(0, {})
        self.table_view.insertRow(0)
        for column in range(5):
            self.table_view.setItem(0, column, self.__create_list_item('', column, file_type))

