# -*- coding: utf-8 -*-
# @Time    : 30/7/2023 下午9:43
# @Author  : LeaVES
# @FileName: method.py
# coding: utf-8

from qfluentwidgets import *


def info_message_display(object_name, information_type: str = "info",
                         information: str = "",
                         title: str = "Null",
                         whereis: str = "TOP",
                         duration_time: int = 2000):
    info_type = {"info": InfoBar.success,
                 "warn": InfoBar.warning,
                 "error": InfoBar.error}
    position = {"TOP": InfoBarPosition.TOP,
                "TOP_LEFT": InfoBarPosition.TOP_LEFT,
                "TOP_RIGHT": InfoBarPosition.TOP_RIGHT,
                "BUTTON": InfoBarPosition.BOTTOM,
                "BUTTON_LEFT": InfoBarPosition.BOTTOM_LEFT,
                "BUTTON_RIGHT": InfoBarPosition.BOTTOM.BOTTOM_RIGHT}

    info_type[information_type.lower()](
        title,
        information,
        isClosable=True,
        position=position[whereis.upper()],
        duration=duration_time,
        parent=object_name
    )
