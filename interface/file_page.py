# -*- coding: utf-8 -*-
# @Time    : 13/7/2023 下午1:19
# @Author  : LeaVES
# @FileName: file_page.py
# coding: utf-8

import os.path

from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from qfluentwidgets import *

from util.cfms_common import *
from util.uie.elements import info_message_display, MessageDisplay


# noinspection PyTypeChecker
class FilePage(QWidget):
    """文件管理目录"""

    def __init__(self, *args, **kwargs):
        super().__init__(None)
        self.functions = {}
        try:
            self.functions.update(kwargs["functions"])
        except KeyError:
            pass
        self.setObjectName(kwargs["name"])
        self.file_information = []
        self.path = [('', '<ROOT>'), ]
        self.current_path = ('', '<ROOT>')
        self.loadProgressBar = IndeterminateProgressBar(self, start=False)

        self.verticalLayout = QVBoxLayout(self)  # 全局布局

    def connect_signal_solt(self, functions: dict):
        "闭包发送函数|方法体"
        # 这些方法不应该被直接连接, 最好在当前作用域重写一个方法
        self.functions.update(functions)
        self.__get_files_function = self.functions.get("get_files_function", None)
        self.__file_rename_function = self.functions.get("rename_file_function", None)
        self.__download_file_function = self.functions.get("download_file_function", None)
        self.__delete_file_function = self.functions.get("delete_file_function", None)
        self.__upload_new_file_function = self.functions.get("upload_file_function", None)
        self.__create_new_dir_function = self.functions.get("create_new_dir_function", None)

    def setup_ui(self, *args, **kwargs):
        try:
            self.functions.update(kwargs["functions"])
        except KeyError:
            pass

        self.connect_signal_solt(self.functions)

        # size_policy = QSizePolicy()
        # size_policy.Policy(QSizePolicy.Policy.Preferred)
        # size_policy.setHorizontalStretch(0)
        # size_policy.setVerticalStretch(0)
        # self.setSizePolicy(size_policy)

        self.setLayout(self.verticalLayout)
        # self.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout.addWidget(self.loadProgressBar)

        self.verticalLayout_0_widget = QWidget(self)  # 这个控件和布局用来装标题和一些其他东西
        self.verticalLayout_0 = QHBoxLayout(self.verticalLayout_0_widget)
        self.verticalLayout_0_widget.setLayout(self.verticalLayout_0)
        # self.verticalLayout_0.setHorizontalSpacing(10)
        self.verticalLayout_0.setObjectName("verticalLayout_0")

        # self.titleLabel = QLabel()  # 页面标题
        # self.titleLabel.setText("Files")
        # self.titleLabel.setStyleSheet(
        #     """QLabel{
        #     font: 45px 'Microsoft YaHei';
        #     }"""
        # )
        # self.titleLabel.setContentsMargins(30, 20, 0, 0)
        # self.verticalLayout_0.addWidget(self.titleLabel, 1, 0, 1, 4)

        self.back_dir_button = ToolButton(FluentIcon.CARE_LEFT_SOLID, self)  # 上一级,下一级
        self.next_dir_button = ToolButton(FluentIcon.CARE_RIGHT_SOLID, self)
        layout_0 = QHBoxLayout()  #
        layout_0.setSpacing(2)
        layout_0_widget = QWidget(self)
        layout_0.addWidget(self.back_dir_button)
        self.back_dir_button.clicked.connect(lambda: self.__change_dir_level(True))
        layout_0.addWidget(self.next_dir_button)
        layout_0_widget.setLayout(layout_0)
        self.verticalLayout_0.addWidget(layout_0_widget)

        # 创建新文件Button
        self.create_new_button = PrimaryDropDownPushButton(text='New', icon=FluentIcon.ADD)
        create_new_menu = RoundMenu(self)
        create_file_action = Action(FluentIcon.DOCUMENT, text='Create file')
        create_folder_action = Action(FluentIcon.FOLDER_ADD, text='Create folder')
        create_folder_action.triggered.connect(self.__create_new_dir)
        create_new_menu.addActions([create_file_action, create_folder_action])
        self.create_new_button.setMenu(create_new_menu)
        # 上传Button
        self.upload_button = PrimaryDropDownPushButton(text='Upload', icon=FluentIcon.UP)
        upload_menu = RoundMenu(self)
        upload_file_action = Action(FluentIcon.DOCUMENT, text='Upload file')
        upload_file_action.triggered.connect(self.__choose_file)
        upload_folder_action = Action(FluentIcon.FOLDER_ADD, text='Upload folder')
        upload_menu.addActions([upload_file_action, upload_folder_action])
        self.upload_button.setMenu(upload_menu)

        layout_1 = QHBoxLayout()  #
        layout_1.setSpacing(2)
        layout_1_widget = QWidget(self)
        layout_1.addWidget(self.create_new_button, 1)
        layout_1.addWidget(self.upload_button, 1)
        layout_1_widget.setLayout(layout_1)

        self.verticalLayout_0.addWidget(layout_1_widget)

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
        self.table_view.cellDoubleClicked.connect(self.__table_item_double_clicked)
        self.table_view.cellChanged.connect(self.__rename_action)
        self.table_view.clear()
        # 允许打开上下文菜单
        self.table_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        # 表头
        self.table_view.verticalHeader().hide()
        self.table_view.verticalHeader().setDefaultSectionSize(60)
        self.table_view.customContextMenuRequested.connect(self.__table_item_right_clicked)
        self.table_view.setContentsMargins(10, 100, 0, 0)
        self.table_view.setColumnCount(5)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.verticalLayout_2.addWidget(self.table_view, 5)

        # 在全局布局里嵌套布局
        self.verticalLayout.addWidget(self.verticalLayout_0_widget)
        self.verticalLayout.addWidget(self.verticalLayout_2_widget)

    def __choose_file(self):
        get_filename_path, ok = QFileDialog.getOpenFileName(self, "选取单个文件", "C:/", "All Files (*);")
        if ok:
            self.__upload_file(get_filename_path)
        else:
            info_message_display(self, information_type="info", whereis="TOP_LEFT", title="已取消", )

    def __table_item_right_clicked(self, pos):
        """文件右键"""
        row = 0
        for i in self.table_view.selectionModel().selection().indexes():
            row = i.row()
        if self.file_information:
            if self.file_information[row]:
                file_type = self.file_information[row]["isFolder"]
                screen_pos = self.table_view.mapToGlobal(pos)  # 转换坐标系
                self.list_item_menu = RoundMenu(self)
                copy_action = Action(FluentIcon.COPY, text='Copy')
                cut_action = Action(FluentIcon.CUT, text='Cut')
                delete_action = Action(FluentIcon.REMOVE_FROM, text="Delete")
                self.list_item_menu.addActions([copy_action, cut_action, delete_action])
                self.list_item_menu.addSeparator()
                download_file_action = Action(FluentIcon.DOWNLOAD, text="Download")
                download_folder_action = Action(FluentIcon.DOWNLOAD, text="Download")
                if not file_type:
                    self.list_item_menu.addAction(download_file_action)
                elif file_type:
                    self.list_item_menu.addAction(download_folder_action)
                download_file_action.triggered.connect(lambda: self.__download_file(file_index=row))
                delete_action.triggered.connect(lambda: self.__delete_file(file_id=self.file_information[row]["File_id"]))
                self.list_item_menu.exec(screen_pos, ani=True)

    def __set_files_tree(self, dirs):
        """文件树"""
        ...

    def __get_dir(self, *args, **kwargs):
        self.__get_files_function(*args, **kwargs)

    @pyqtSlot()
    def __create_new_dir(self, *args, **kwargs):
        self.__create_new_dir_function(*args, **kwargs)

    def __delete_file(self, *args, **kwargs):
        self.__delete_file_function(*args, **kwargs)

    def __download_file(self, *args, **kwargs):
        self.__download_file_function(*args, **kwargs)

    def __upload_file(self, *args, **kwargs):
        self.__upload_new_file_function(*args, **kwargs)

    @staticmethod
    def __sort_file_list(file_list: list, reverse: bool = False):
        sorted_list = []
        for _ in range(2):
            for info in file_list:
                if info["isFolder"]:
                    sorted_list.append(info)
            for info in file_list:
                if not info["isFolder"]:
                    sorted_list.append(info)
            if reverse:
                sorted_list.reverse()

        return sorted_list

    # @signal_blocker
    def set_files_list(self, files: list, force: bool = False):
        """设置文件列表"""
        def create_list_item(info, column, is_folder: bool = False):
            """设置单元格"""
            item = QTableWidgetItem()
            item.setText(info)
            if column != 0:
                item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            else:
                if is_folder:
                    item.setIcon(FluentIcon.FOLDER.icon())
                elif not is_folder:
                    item.setIcon(FluentIcon.DOCUMENT.icon())
                    if column == 4:
                        item.setText("")

                item.setToolTip(info)
            return item

        self.table_view.blockSignals(True)
        self.loadProgressBar.stop()
        self.table_view.verticalHeader().setDefaultSectionSize(60)
        if files == self.file_information and not force:
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
            self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
            self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            self.table_view.setHorizontalHeaderLabels(['Name', 'Created at', 'Type', 'Size', 'Permission'])
            sorted_list = self.file_information
            for row, file_info in enumerate(sorted_list):
                for column in range(5):
                    file_info_list = [
                        file_info["Name"],
                        file_info["Created_at"],
                        file_info["File_type"],
                        file_info["Transformed_size"],
                        file_info["Permission"]
                    ]
                    self.table_view.setItem(
                        row,
                        column,
                        create_list_item(
                            info=file_info_list[column],
                            column=column,
                            is_folder=file_info["isFolder"]
                        )
                    )
        self.table_view.blockSignals(False)

    def __change_dir_level(self, action: bool):
        if action:
            if len(self.path) > 1:
                self.current_path = self.path[-2]
                del self.path[-1]
                self.__get_dir(self.current_path[0])
            else:
                self.current_path = ('', '<ROOT>')
                self.__get_dir()

    @pyqtSlot(int, int)
    def __table_item_double_clicked(self, row, column):
        """双击事件处理"""
        if not column == 0:
            if self.file_information[row]["isFolder"]:
                dir_id = self.file_information[row].get("File_id", "")
                dir_name = self.file_information[row].get("Name", "")
                self.__get_dir(dir_id)
                self.current_path = (dir_id, dir_name)
                self.path.append(self.current_path)

    # @signal_blocker
    @pyqtSlot(int, int)
    def __rename_action(self, row, column):
        """rename"""
        self.table_view.blockSignals(True)
        data = str(self.table_view.item(row, column).text())
        if data in [f["Name"] for f in self.file_information]:
            title = 'ERROR'
            content = f"""此目标已包含名为 '{data}' 的文件"""
            w = MessageDisplay(title, content, parent=self, btn_text=("取消",))
            w.exec()
            self.table_view.item(row, column).setText(self.file_information[row]["Name"])
            info_message_display(object_name=self, information_type="info", title="已取消该操作")
            self.table_view.blockSignals(False)
            return
        elif data.isspace() or not data:
            title = 'ERROR'
            content = f"""文件名不得为空"""
            w = MessageDisplay(title, content, parent=self, btn_text=("取消",))
            w.exec()
            self.table_view.item(row, column).setText(self.file_information[row]["Name"])
            info_message_display(object_name=self, information_type="info", title="已取消该操作")
            self.table_view.blockSignals(False)
        else:
            self.file_information[row]["Name"] = data
            self.__file_rename_function(data=data, file_index=row)
            if not self.file_information[row]["isFolder"]:
                _type = os.path.splitext(data)[-1].strip(".").lower()
                _type = self.file_information[row]["File_type"] = FILE_TYPES.get(_type, _type.upper() + " File")
                self.table_view.item(row, 2).setText(_type)
            self.table_view.blockSignals(False)
