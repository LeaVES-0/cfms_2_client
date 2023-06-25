# -*- coding: utf-8 -*-
# @Time    : 18/6/2023 下午2:12
# @Author  : LeaVES
# @FileName: LoginWindow.py
# coding: utf-8

from PyQt6 import QtCore, QtWidgets
from qfluentwidgets import CheckBox, LineEdit, PrimaryPushButton


class LoginWindow:
    def setup_ui(self, window_form):
        # 主窗口
        window_form.setObjectName("Form")
        # window_form.resize(1250, 809)
        # window_form.setMinimumSize(QtCore.QSize(700, 500))
        #
        self.horizontalLayout = QtWidgets.QHBoxLayout(window_form)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        #
        self.widget = QtWidgets.QWidget(parent=window_form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred,
                                           QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.widget.sizePolicy().hasHeightForWidth())
        self.widget.setSizePolicy(sizePolicy)
        self.widget.setMinimumSize(QtCore.QSize(360, 0))
        self.widget.setMaximumSize(QtCore.QSize(360, 16777215))
        self.widget.setStyleSheet(
            """QLabel{
            font: 13px 'Microsoft YaHei'
            }"""
        )
        self.widget.setObjectName("widget")
        # 创建一个容器(整个侧栏)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.widget)
        self.verticalLayout_2.setContentsMargins(20, 20, 20, 20)
        self.verticalLayout_2.setSpacing(9)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        #
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum,
                                           QtWidgets.QSizePolicy.Policy.Expanding)
        self.verticalLayout_2.addItem(spacerItem)
        self.label_7 = QtWidgets.QLabel(parent=self.widget)
        # font = QtGui.QFont()
        # font.setPointSize(30)
        # self.label_7.setFont(font)
        # 不能使用上述代码会被容器的StyleSheet覆盖
        # 指定一个stylesheet
        self.label_7.setStyleSheet(
            """QLabel{
            font: 33px 'Microsoft YaHei'
            }"""
        )
        self.label_7.setObjectName("label_7")
        self.verticalLayout_2.addWidget(self.label_7)
        # 没什么用的spacerItem
        spacerItem1 = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Policy.Minimum,
                                            QtWidgets.QSizePolicy.Policy.Fixed)
        self.verticalLayout_2.addItem(spacerItem1)
        # 创建一个用来放置背景图的标签
        self.label_ground = QtWidgets.QLabel(parent=self.widget)
        self.label_ground.setEnabled(True)  # 启用设置
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred,
                                           QtWidgets.QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_ground.sizePolicy().hasHeightForWidth())
        self.label_ground.setSizePolicy(sizePolicy)
        self.label_ground.setMinimumSize(QtCore.QSize(100, 100))
        self.label_ground.setMaximumSize(QtCore.QSize(100, 100))

        self.label_ground.setScaledContents(True)
        self.label_ground.setObjectName("back_ground")
        self.verticalLayout_2.addWidget(self.label_ground, 0, QtCore.Qt.AlignmentFlag.AlignHCenter)
        # 没什么用的spacerItem
        spacerItem2 = QtWidgets.QSpacerItem(20, 15, QtWidgets.QSizePolicy.Policy.Minimum,
                                            QtWidgets.QSizePolicy.Policy.Fixed)
        self.verticalLayout_2.addItem(spacerItem2)
        # 创建QGridLayout容器
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setHorizontalSpacing(4)
        self.gridLayout.setVerticalSpacing(9)
        self.gridLayout.setObjectName("gridLayout")
        # 服务器地址E
        self.lineEdit = LineEdit(parent=self.widget)
        self.lineEdit.setClearButtonEnabled(True)
        self.lineEdit.setObjectName("lineEdit")
        # 端口L
        self.gridLayout.addWidget(self.lineEdit, 1, 0, 1, 1)
        # 服务器地址L
        self.label_3 = QtWidgets.QLabel(parent=self.widget)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 0, 0, 1, 1)
        # 端口E
        self.lineEdit_2 = LineEdit(parent=self.widget)
        self.lineEdit_2.setPlaceholderText("")
        self.lineEdit_2.setClearButtonEnabled(True)
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.gridLayout.addWidget(self.lineEdit_2, 1, 1, 1, 1)
        # 端口L
        self.label_4 = QtWidgets.QLabel(parent=self.widget)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 0, 1, 1, 1)
        # 再嵌套一个容器
        self.gridLayout.setColumnStretch(0, 2)
        self.gridLayout.setColumnStretch(1, 1)
        self.verticalLayout_2.addLayout(self.gridLayout)
        # 用户名L
        self.label_5 = QtWidgets.QLabel(parent=self.widget)
        self.label_5.setObjectName("label_5")
        self.verticalLayout_2.addWidget(self.label_5)
        # 用户名E
        self.lineEdit_3 = LineEdit(parent=self.widget)
        self.lineEdit_3.setClearButtonEnabled(True)
        self.lineEdit_3.setObjectName("lineEdit_3")
        self.verticalLayout_2.addWidget(self.lineEdit_3)
        # 密码L
        self.label_6 = QtWidgets.QLabel(parent=self.widget)
        self.label_6.setObjectName("label_6")
        self.verticalLayout_2.addWidget(self.label_6)
        # 密码
        self.lineEdit_4 = LineEdit(parent=self.widget)
        self.lineEdit_4.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.lineEdit_4.setClearButtonEnabled(True)
        self.lineEdit_4.setObjectName("lineEdit_4")
        self.verticalLayout_2.addWidget(self.lineEdit_4)
        #
        # 没什么用的spacerItem
        spacerItem3 = QtWidgets.QSpacerItem(20, 5, QtWidgets.QSizePolicy.Policy.Minimum,
                                            QtWidgets.QSizePolicy.Policy.Fixed)
        self.verticalLayout_2.addItem(spacerItem3)
        # 1111(复选框)
        self.checkBox = CheckBox(parent=self.widget)
        self.checkBox.setChecked(True)
        self.checkBox.setObjectName("checkBox")
        self.verticalLayout_2.addWidget(self.checkBox, 0, QtCore.Qt.AlignmentFlag.AlignHCenter)
        # 没什么用的spacerItem
        spacerItem4 = QtWidgets.QSpacerItem(20, 5, QtWidgets.QSizePolicy.Policy.Minimum,
                                            QtWidgets.QSizePolicy.Policy.Fixed)
        self.verticalLayout_2.addItem(spacerItem4)
        # 登入按键
        self.pushButton = PrimaryPushButton(parent=self.widget)
        self.pushButton.setObjectName("pushButton")
        self.verticalLayout_2.addWidget(self.pushButton)
        # 没什么用的spacerItem
        spacerItem5 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum,
                                            QtWidgets.QSizePolicy.Policy.Expanding)
        self.verticalLayout_2.addItem(spacerItem5)
        # 背景图
        self.horizontalLayout.addWidget(self.widget)
        self.label = QtWidgets.QLabel(parent=window_form)
        self.label.setText("")
        # self.label.setPixmap(QtGui.QPixmap("resource/images/login_b.jpg"))
        # self.label.setScaledContents(True)
        self.label.setObjectName("label")
        # backGroundPicture = QtGui.QPixmap("resource/images/login_b.jpg").scaled(
        #     self.label.size(),
        #     QtCore.Qt.AspectRatioMode.KeepAspectRatioByExpanding,
        #     QtCore.Qt.TransformationMode.SmoothTransformation
        # )
        self.horizontalLayout.addWidget(self.label)
        # self.label.setPixmap(backGroundPicture)
        #
        self.re_translate_ui(window_form)
        QtCore.QMetaObject.connectSlotsByName(window_form)

    def re_translate_ui(self, Form):
        """登入部分
        统一设置组件的内容"""
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label_7.setText(_translate("Form", "Login", ))
        self.lineEdit.setPlaceholderText(_translate("Form", "example.com"))
        self.label_3.setText(_translate("Form", "服务器地址："))
        self.lineEdit_2.setText(_translate("Form", "1145"))
        self.label_4.setText(_translate("Form", "端口："))
        self.label_5.setText(_translate("Form", "用户名："))
        self.lineEdit_3.setPlaceholderText(_translate("Form", "User"))
        self.label_6.setText(_translate("Form", "密码："))
        self.lineEdit_4.setPlaceholderText(_translate("Form", "••••••••••••"))
        self.checkBox.setText(_translate("Form", "记住密码"))
        self.pushButton.setText(_translate("Form", "登录"))
        self.pushButton.setToolTip("登入到服务器")
