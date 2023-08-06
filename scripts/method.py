# -*- coding: utf-8 -*-
# @Time    : 30/7/2023 下午9:43
# @Author  : LeaVES
# @FileName: method.py
# coding: utf-8

from qfluentwidgets import *

FILE_TYPES = {"txt": "Text document",
              "rar": "Roshal Archive ",
              "zip": "Compressed(zipped) folder",
              "iso": "Disc image File",
              "img": "Disc image File",
              "exe": "Windows executable program file",
              "py": "Python",
              "jar": "Java",
              "html": "Hypertext Markup Language page",
              "htm": "Hypertext Markup Language page",
              "gitignore": "Git ignore",
              "rdp": "Remote Desktop Connection",
              "db": "Data Base File",
              "dll": "Application extension",
              "json": "JSON",
              "yml": "Yaml",
              "ini": "Configuration setting",
              "bat": "Windows Batch File",
              "fon": "Font File",
              "ttf": "TrueType font file",
              "mp4": "MPEG 4 video file",
              "mp3": "MPEG Layer-3 audio file",
              "m4a": "MPEG 4 audio file",
              "mid": "Instrument digital interface file",
              "midi": "Instrument digital interface file",
              "psd": "Adobe Photoshop file",
              "swf": "Shockwave Flash",
              "msi": "Microsoft installer file",
              "accdb": "Microsoft Access database file",
              "doc": "Word document",
              "xlsx": "Excel document"
              }


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
