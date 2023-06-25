#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 18/6/2023 下午2:12
# @Author  : LeaVES
# @FileName: LoginWindow.py
# coding: utf-8

import sys

from PyQt6.QtCore import Qt, QLocale, QSize
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import QApplication
from qfluentwidgets import setThemeColor, FluentTranslator
from qframelesswindow import StandardTitleBar, AcrylicWindow, FramelessWindow

from Windows.LoginWindow import LoginWindow
from Windows.MainWindow import MainWindow

RESOURCE_IMAGES = "resource/images/"


class ShowWindows (AcrylicWindow, MainWindow, LoginWindow):
    def __init__(self):
        super().__init__()


    def winSet(self):
        """所有窗口采用统一的样式,
        统一设置,避免重复"""
        # 主题色
        setThemeColor('#28afe9')
        # 标题栏
        self.setTitleBar(StandardTitleBar(parent=self))
        self.titleBar.raise_()
        self.setWindowTitle('sfms__2.0')
        self.setWindowIcon(QIcon(f"{RESOURCE_IMAGES}logo.png"))
        # 大小
        self.resize(1000, 650)
        self.windowEffect.setMicaEffect(self.winId())
        self.setMinimumSize(QSize(700, 500))
        # 标题栏风格设置
        style = """QLabel{
            background: transparent;
            font: 13px 'Segoe UI';
            color: black;padding: 0 4px
        }
        """
        self.titleBar.titleLabel.setStyleSheet(style)
        # 移动窗口的位置，让它位于屏幕正中间
        desktop = QApplication.screens()[0].availableGeometry()
        width, height = desktop.width(), desktop.height()
        center = width // 2 - self.width() // 2, height // 2 - self.height() // 2
        self.move(center[0], center[1])


    def login_ui(self):
        super().setup_login_ui()
        self.winSet()
        self.label.setScaledContents(False)
        # super().resizeEvent()
        pixmap = QPixmap(f"{RESOURCE_IMAGES}login_b.jpg")
        
        self.label.setPixmap(pixmap)
        self.label_ground.setPixmap(QPixmap(f"{RESOURCE_IMAGES}logo.png"))
        self.show()

    def main_ui(self):
        super().setup_main_ui()
        self.winSet()
        """初始化父类"""
        # windows_init(self)
        # 防止导航栏挡住标题栏
        # 因为titleBar不在MainWindows.py,所以在此处设置hBoxLayout的边距
        self.hBoxLayout.setContentsMargins(0, self.titleBar.height(), 0, 0)
        self.show()

# class RunLoginWindow(AcrylicWindow, LoginWindow):
#     """运行登陆窗口
#     与素材有关的设置再次统一配置，
#     方便管理"""

#     def __init__(self):
#         """初始化父类"""
#         super().__init__()
#         # windows_init(self)

#     def resizeEvent(self, e):
#         self.label.setScaledContents(False)
#         super().resizeEvent(e)
#         pixmap = QPixmap(f"{RESOURCE_IMAGES}login_b.jpg").scaled(
#             self.label.size(),
#             Qt.AspectRatioMode.KeepAspectRatioByExpanding,
#             Qt.TransformationMode.SmoothTransformation
#         )
#         self.label.setPixmap(pixmap)
#         self.label_ground.setPixmap(QPixmap(f"{RESOURCE_IMAGES}logo.png"))


# class RunMainWindow(AcrylicWindow, FramelessWindow, MainWindow):
#     """运行主窗口"""
#     def __init__(self):
#         """初始化父类"""
#         # windows_init(self)
#         # 防止导航栏挡住标题栏
#         # 因为titleBar不在MainWindows.py,所以在此处设置hBoxLayout的边距
#         self.hBoxLayout.setContentsMargins(0, self.titleBar.height(), 0, 0)


def main():
    """创建Qt应用程序实例"""
    app = QApplication(sys.argv)
    # Internationalization
    translator = FluentTranslator(QLocale())
    app.installTranslator(translator)
    # 创建登入窗口实例
    login_w = ShowWindows()
    login_w.login_ui()
    # 创建主窗口实例
    main_w = ShowWindows()
    main_w.main_ui()
    # 启动Qt应用程序
    app.exec()


if __name__ == '__main__':
    main()
