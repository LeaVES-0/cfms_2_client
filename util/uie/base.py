from PyQt6.QtCore import *
from PyQt6.QtGui import QIcon, QPixmap, QDesktopServices
from PyQt6.QtWidgets import *
from qfluentwidgets import *
from qframelesswindow import FramelessWindow
from util.uie.elements import LeaVESTitleBar, MessageDisplay

RESOURCE_IMAGES = "resource/images/"
DEFAULT_THEME_COLOUR = "#28afe9"

class CfmsUIBase(FramelessWindow):
    def __init__(self, *args, **kwargs):
        """所有窗口采用统一的样式"""
        super().__init__()
        # 主题色
        setThemeColor(f'{DEFAULT_THEME_COLOUR}')
        # 标题栏
        self.titleBarObj = LeaVESTitleBar(parent=self, functions=[self.setThemeState, ])
        self.setTitleBar(self.titleBarObj)
        # self.titleBarObj.raise_()
        self.setWindowTitle('cfms  2.0')
        self.setWindowIcon(QIcon(f"{RESOURCE_IMAGES}logo.png"))
        self.splashScreen = SplashScreen(self.windowIcon(), parent=self)
        self.splashScreen.setIconSize(QSize(106, 106))
        self.splashScreen.raise_()
        # 大小
        self.resize(1000, 650)
        self.windowEffect.setMicaEffect(self.winId())
        self.desktop = QApplication.screens()[0].availableGeometry()
        width, height = self.desktop.width(), self.desktop.height()
        self.setMinimumSize(QSize(800, 500))
        self.setMaximumSize(QSize(width, height))
        # 移动窗口的位置，让它位于屏幕正中间
        center = width // 2 - self.width() // 2, height // 2 - self.height() // 2
        self.move(center[0], center[1])

        # 默认主题模式
        setTheme(Theme.AUTO)
        self.titleBarObj.set_theme(theme())

    @staticmethod
    def themeState():
        return theme()

    def show_public_key_meg(self, info):
        title = 'The Public Key of the Server:'
        content = f"{info}"
        w = MessageDisplay(title, content, parent=self, btn_text=("OK",))
        w.exec()

    def show_diff_public_key_warn(self, info):
        """显示公钥不同时的警报，若要求更换则返回假"""
        title = 'The Public Key of the Server:'
        content = f"""服务器上的公钥与本地不同,这可能意味着服务器已被重置。
但若非如此,则意味着您可能已遭受中间人攻击。
获取的服务器公钥:
{info}"""
        w = MessageDisplay(title, content, parent=self, btn_text=("断开连接", "更换公钥"))
        if w.exec():
            return True
        else:
            return

    def setTitle(self, title_text: str):
        if title_text:
            self.setWindowTitle(self.windowTitle() + "   " + title_text)

    def setThemeState(self, th=None):
        """切换主题模式"""
        opposing = {Theme.DARK: Theme.LIGHT, Theme.LIGHT: Theme.DARK}
        if not th:
            th = opposing[theme()]
        if th == Theme.LIGHT:
            setTheme(Theme.LIGHT)
            self.titleBarObj.set_theme(Theme.LIGHT)
            self.set_widget_theme(Theme.LIGHT)

        else:
            setTheme(Theme.DARK)
            self.titleBarObj.set_theme(Theme.DARK)
            self.set_widget_theme(Theme.DARK)

    def set_widget_theme(self, interface_theme: Theme):
        if interface_theme == Theme.DARK:
            style = f"""
            QWidget#{self.objectName()}{{
            background-color: #333333;
            }}
            QLabel {{
            font: 13px 'Microsoft YaHei';
            font-weight: bold;
            background-color:transparent;
            color: white
            }}
            """
        else:
            style = f"""
            QWidget#{self.objectName()} {{background-color: white;}}
            QLabel {{
            font: 13px 'Microsoft YaHei';
            background-color: transparent;
            color: black
            }}
            """
        self.setStyleSheet(style)
