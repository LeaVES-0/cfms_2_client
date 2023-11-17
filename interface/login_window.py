# -*- coding: utf-8 -*-
# @Time    : 18/6/2023 下午2:12
# @Author  : LeaVES
# @FileName: LoginWindow.py
# coding: utf-8

from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from qfluentwidgets import *

from util.cfms_network import DEFAULT_PORT
from util.uie.base import CfmsUIBase


class LoginWindow(CfmsUIBase):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.setObjectName("CFMS_Login_Window")

        self.setup_ui()
        self.re_set_text()

    def setup_ui(self):
        # 主窗口
        self.horizontalLayout = QHBoxLayout(self)  # 全局布局
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(0)

        # 放置侧栏
        self.__init_verticalLayout_2()

        # 背景图
        self.label = QLabel()
        self.label.setText("")
        self.label.setObjectName("label")
        self.label.lower()
        self.horizontalLayout.addWidget(self.label)

    def do_logout_action(self):
        self.user_info_bar.page00.checkBox_remember_user.setChecked(False)

    def is_remember_pass_checkbox_checked(self):
        return self.user_info_bar.page00.checkBox_remember_user.isChecked()

    def set_current_user_info(self, info):
        self.user_info_bar.page01.show_user_info.setText(info)

    def add_server_list(self, s_list):
        self.server_info_bar.serverAdLE.addItems(s_list)
        self.server_info_bar.serverAdLE.setCurrentIndex(0)

    def add_user_list(self, u_list):
        self.user_info_bar.page00.userNameLE.addItems(u_list)
        self.user_info_bar.page00.userNameLE.setCurrentIndex(0)

    def set_connected_server_info(self, info):
        self.user_info_bar.connected_server_info.setText(info)

    def __init_verticalLayout_2(self):
        # 创建一个容器(整个侧栏)
        self.side_bar = QWidget(self)
        self.verticalLayout_2 = QVBoxLayout(self.side_bar)
        self.verticalLayout_2.setContentsMargins(20, 20, 20, 20)
        self.verticalLayout_2.setSpacing(9)
        #
        spacer_item = QSpacerItem(20, 45, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.verticalLayout_2.addItem(spacer_item)

        self.label_title = QLabel()
        # 指定一个stylesheet
        self.label_title.setStyleSheet(
            """QLabel{
            font: 33px 'Microsoft YaHei'
            }"""
        )

        self.label_title.setObjectName("label_title")
        self.verticalLayout_2.addWidget(self.label_title)
        # spacerItem
        spacer_item1 = QSpacerItem(20, 23, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.verticalLayout_2.addItem(spacer_item1)

        # 创建一个用来放置头像的标签
        self.label_head_icon = QLabel()
        size_policy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(self.label_head_icon.sizePolicy().hasHeightForWidth())
        self.label_head_icon.setSizePolicy(size_policy)
        self.label_head_icon.setMinimumSize(QSize(100, 100))
        self.label_head_icon.setMaximumSize(QSize(100, 100))
        self.label_head_icon.setScaledContents(True)
        self.label_head_icon.setObjectName("label_head_icon")
        self.verticalLayout_2.addWidget(self.label_head_icon, 0, Qt.AlignmentFlag.AlignHCenter)

        # # spacerItem
        spacer_item2 = QSpacerItem(self.width(), 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.verticalLayout_2.addItem(spacer_item2)

        self.loadProgressBar = IndeterminateProgressBar(start=False)
        self.verticalLayout_2.addWidget(self.loadProgressBar)

        self.server_info_bar = ServerInfoBar(self)
        self.user_info_bar = UserInfoBar(self)

        self.stackWidget = QStackedWidget(self)
        self.stackWidget.addWidget(self.server_info_bar)
        self.stackWidget.addWidget(self.user_info_bar)
        self.stackWidget.setCurrentWidget(self.server_info_bar)
        self.verticalLayout_2.addWidget(self.stackWidget)

        # spacerItem

        spacer_item3 = QSpacerItem(self.width(), 45, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.verticalLayout_2.addItem(spacer_item3)

        self.horizontalLayout.addWidget(self.side_bar)
        self.side_bar.setMinimumWidth(330)
        self.side_bar.lower()

    def re_set_text(self):
        """登入部分
        统一设置组件的内容"""
        self.server_info_bar.serverAdLE.setPlaceholderText("example.com")
        self.server_info_bar.label_3.setText(self.tr("Address"))
        self.server_info_bar.serverPortLE.setText(f"{DEFAULT_PORT}")
        self.server_info_bar.label_4.setText(self.tr("Port"))
        self.server_info_bar.link_server_button.setText(self.tr("Link"))
        self.server_info_bar.link_cancel_button.setText(self.tr("Cancel"))

        self.user_info_bar.page00.label_5.setText(self.tr("User"))
        self.user_info_bar.page00.userNameLE.setPlaceholderText("User")
        self.user_info_bar.page00.label_6.setText(self.tr("Password"))
        self.user_info_bar.page00.userPasswordLE.setPlaceholderText("••••••••••••")
        self.user_info_bar.page00.checkBox_remember_user.setText(self.tr("Remember Password"))

        self.user_info_bar.login_Button.setText(self.tr("Login"))
        self.user_info_bar.login_Button.setToolTip(self.tr("Login to the server."))

        self.user_info_bar.page01.login_out_Button.setText(self.tr("Logout"))
        self.user_info_bar.back_Button.setText(self.tr("Disconnect"))


class ServerInfoBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        # 设置服务器连接部分UI
        # 创建QGridLayout容器
        self.main_layout = QGridLayout(self)
        self.main_layout.setHorizontalSpacing(2)
        self.main_layout.setVerticalSpacing(10)
        # self.main_layout.setColumnStretch(0, 1)
        # self.main_layout.setColumnStretch(1, 1)

        spacer_item = QSpacerItem(self.width(), 40, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.main_layout.addItem(spacer_item)

        # 服务器地址L
        self.label_3 = QLabel()
        self.main_layout.addWidget(self.label_3, 0, 0, 1, 3)
        # 端口L
        self.label_4 = QLabel()
        self.main_layout.addWidget(self.label_4, 0, 3, 1, 2)

        # 服务器地址E
        self.serverAdLE = EditableComboBox()
        # self.serverAdLE.setClearButtonEnabled(True)
        self.main_layout.addWidget(self.serverAdLE, 1, 0, 1, 3)

        # 端口E
        self.serverPortLE = LineEdit()
        self.serverPortLE.setPlaceholderText("")
        # self.serverPortLE.setClearButtonEnabled(True)
        self.main_layout.addWidget(self.serverPortLE, 1, 3, 1, 2)

        spacer_item2 = QSpacerItem(self.width(), 90, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.main_layout.addItem(spacer_item2, 2, 0)

        # 登陆到服务器按键
        self.link_server_button = PrimaryPushButton()
        self.main_layout.addWidget(self.link_server_button, 3, 0, 1, 5)
        self.link_server_button.setShortcut("enter")
        self.link_server_button.setShortcutEnabled(True)

        self.link_cancel_button = PrimaryPushButton()
        self.main_layout.addWidget(self.link_cancel_button, 4, 0, 1, 5)
        self.link_cancel_button.setEnabled(False)

        spacer_item1 = QSpacerItem(self.width(), 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self.main_layout.addItem(spacer_item1)


class UserInfoBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        self.page00 = self.Page00(self)
        self.page01 = self.Page01(self)
        self.main_layout = QVBoxLayout(self)

        self.connected_server_info = PushButton()
        self.main_layout.addWidget(self.connected_server_info)
        # self.connected_server_info.setVisible(False)
        self.connected_server_info.setText("")

        self.stackWidget = QStackedWidget(self)
        self.stackWidget.addWidget(self.page00)
        self.stackWidget.addWidget(self.page01)
        self.stackWidget.setCurrentWidget(self.page00)
        self.main_layout.addWidget(self.stackWidget)

        # 登入按键
        self.login_Button = PrimaryPushButton()
        self.main_layout.addWidget(self.login_Button)
        self.login_Button.setShortcut(Qt.Key.Key_Enter)

        self.back_Button = PushButton(self)
        self.main_layout.addWidget(self.back_Button)

    class Page00(QWidget):
        def __init__(self, parent):
            super().__init__(parent)
            spacer_item = QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

            self.main_layout = QVBoxLayout(self)
            self.main_layout.setSpacing(10)
            # 用户名L
            self.label_5 = QLabel()
            self.main_layout.addWidget(self.label_5)

            # 用户名E
            self.userNameLE = EditableComboBox()
            self.userNameLE.setClearButtonEnabled(True)
            self.main_layout.addWidget(self.userNameLE)

            self.main_layout.addItem(spacer_item)

            # 密码L
            self.label_6 = QLabel()
            self.main_layout.addWidget(self.label_6)

            # 密码E
            self.userPasswordLE = LineEdit()
            self.userPasswordLE.setEchoMode(QLineEdit.EchoMode.Password)
            self.main_layout.addWidget(self.userPasswordLE)

            self.main_layout.addItem(spacer_item)

            # 1111(复选框)
            self.checkBox_remember_user = CheckBox()
            self.checkBox_remember_user.setChecked(False)
            self.main_layout.addWidget(self.checkBox_remember_user, 0, Qt.AlignmentFlag.AlignHCenter)

    class Page01(QWidget):
        def __init__(self, parent):
            super().__init__(parent)
            self.main_layout = QVBoxLayout(self)

            self.show_user_info = PushButton()
            self.show_user_info.setText("")
            self.main_layout.addWidget(self.show_user_info)

            spacer_item0 = QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
            self.main_layout.addItem(spacer_item0)

            self.login_out_Button = PrimaryPushButton()
            self.main_layout.addWidget(self.login_out_Button)

            spacer_item1 = QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
            self.main_layout.addItem(spacer_item1)
