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
        self.path = [None, ]
        self.current_path = None
        self.rename_arg = False

    def setup_ui(self, args):
        self.get_files_function = args["functions"]["get_files_function"]
        self.file_rename_function = args["functions"]["file_rename_function"]
        self.operate_file_function = args["functions"]["operate_file_function"]
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

        self.verticalLayout_0_widget = QWidget()  # 这个控件和布局用来装标题和一些其他东西
        self.verticalLayout_0 = QGridLayout()
        self.verticalLayout_0_widget.setLayout(self.verticalLayout_0)
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

        self.create_new_button = PrimaryDropDownPushButton(text='新建', icon=FluentIcon.ADD)

        self.upload_button = PrimaryDropDownPushButton(text='上传', icon=FluentIcon.UP)
        upload_menu = RoundMenu(self)
        upload_file_action = Action(FluentIcon.DOCUMENT, text='Upload file')
        upload_file_action.triggered.connect(self.choose_file)
        upload_folder_action = Action(FluentIcon.FOLDER_ADD, text='Upload folder')
        upload_menu.addActions([upload_file_action, upload_folder_action])
        self.upload_button.setMenu(upload_menu)

        space_0 = QSpacerItem(200, 5)
        self.back_dir_button = ToolButton(FluentIcon.CARE_LEFT_SOLID, self)  # 上一级,下一级
        self.next_dir_button = ToolButton(FluentIcon.CARE_RIGHT_SOLID, self)
        self.verticalLayout_0.addWidget(self.create_new_button, 2, 0, 1, 1)
        self.verticalLayout_0.addWidget(self.upload_button, 2, 1, 1, 1)
        self.verticalLayout_0.addItem(space_0, 2, 2, 1, 4)
        self.verticalLayout_0.addWidget(self.back_dir_button, 2, 6, 1, 1)
        self.verticalLayout_0.addWidget(self.next_dir_button, 2, 7, 1, 1)
        self.back_dir_button.clicked.connect(lambda: self.change_dir_level(True))

        self.verticalLayout_2_widget = QWidget()  # 这个控件和布局用来装文件树和文件目录
        self.verticalLayout_2 = QHBoxLayout()
        self.verticalLayout_2_widget.setLayout(self.verticalLayout_2)
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
        self.table_view.setHorizontalHeaderLabels(['FileName', 'Type', 'Size', 'Create Date', 'Permission'])  # 行标题
        self.table_view.cellDoubleClicked.connect(self.into_dir_action)
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

    def choose_file(self):
        get_filename_path, ok = QFileDialog.getOpenFileName(self, "选取单个文件", "C:/", "All Files (*);")
        if ok:
            print(get_filename_path)

    def file_list_button(self, pos):
        """文件按键"""
        row = 0
        for i in self.table_view.selectionModel().selection().indexes():
            row = i.row()
        file_id = self.file_information[row]["file_id"]
        screen_pos = self.table_view.mapToGlobal(pos)  # 转换坐标系
        list_item_menu = RoundMenu(self)
        copy_action = Action(FluentIcon.COPY, text='Copy')
        cut_action = Action(FluentIcon.CUT, text='Cut')
        remove_action = Action(FluentIcon.REMOVE_FROM, text="Remove")
        list_item_menu.addActions([copy_action, cut_action, remove_action])
        list_item_menu.addSeparator()
        download_action = Action(FluentIcon.DOWNLOAD, text="Download")
        if self.file_information[row]["type"] == "file":
            list_item_menu.addAction(download_action)
        download_action.triggered.connect(lambda: self.operate_file_function("read", row, file_id))
        list_item_menu.exec(screen_pos, ani=True)

    def set_file_tree_list(self, files):
        self.rename_arg = False
        self.__set_files_list(files[0])
        # self.__set_files_tree(files[1])

    def __set_files_tree(self, dirs):
        """文件树"""
        ...

    @staticmethod
    def __create_list_item(info, column: int = 0, obj_type: str = "file"):
        """设置单元格"""
        item = QTableWidgetItem(info)
        if column != 0:
            item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
        else:
            if obj_type == "dir":
                item.setIcon(FluentIcon.FOLDER.icon())
            elif obj_type == "file":
                item.setIcon(FluentIcon.DOCUMENT.icon())
        return item

    def __set_files_list(self, files: list):
        """设置文件列表"""
        self.file_information = files
        self.table_view.clear()
        self.table_view.setRowCount(len(self.file_information))
        self.table_view.verticalHeader().setDefaultSectionSize(60)
        # 批量设置表格项
        for row, file_info in enumerate(self.file_information):
            file_type = file_info["type"]
            for column in range(5):
                file_info_list = [file_info["name"], file_info["type"], file_info["transformed_size"],
                                  file_info["create_time"], file_info["permission"]]
                self.table_view.setItem(row, column, self.__create_list_item(file_info_list[column], column, file_type))
        self.table_view.setHorizontalHeaderLabels(['FileName', 'Type', 'Size', 'Create Date', 'Permission'])  # 行标题

    def change_dir_level(self, action: bool):
        if action:
            if len(self.path) > 1:
                self.current_path = self.path[-2]
                del self.path[-1]
                if not self.current_path:
                    self.get_files_function()
                else:
                    self.get_files_function(self.current_path[0])
            else:
                self.get_files_function()

    def into_dir_action(self, row, column):
        self.rename_arg = True
        dir_id = self.file_information[row]["file_id"]
        dir_name = self.file_information[row]["name"]
        print("clicked:", dir_id)
        if not column == 0:
            if self.file_information[row]["type"] == "dir":
                self.get_files_function(dir_id)
                self.current_path = dir_id, dir_name
                self.path.append(self.file_information[row]["name"])

    def rename_action(self, row, column):
        if self.rename_arg:
            file_obj = self.file_information[row]
            data = str(self.table_view.item(row, column).text())
            self.file_rename_function(data, file_obj["file_id"], file_obj["name"])
            self.rename_arg = False
