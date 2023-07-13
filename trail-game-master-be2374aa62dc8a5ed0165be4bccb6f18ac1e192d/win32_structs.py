#!/usr/bin/python3
# coding=utf-8

import ctypes

from ctypes import wintypes


# This file contains classes for all the c style structs needed for win32api calls

class SMALL_RECT(ctypes.Structure):
    _fields_ = ('left', ctypes.c_short), ('top', ctypes.c_short), ('right', ctypes.c_short), (
        'bottom', ctypes.c_short)


class COORD(ctypes.Structure):
    _fields_ = ('x', ctypes.c_short), ('y', ctypes.c_short)


class CHAR_INFO(ctypes.Structure):
    _fields_ = ('ascii', ctypes.c_char), ('attr', ctypes.c_uint16)


class CONSOLE_CURSOR_INFO(ctypes.Structure):
    _fields_ = [("size", ctypes.c_int),
                ("visible", ctypes.c_bool)]


class CONSOLE_SCREEN_BUFFER_INFO(ctypes.Structure):
    _fields_ = [
        ("dwSize", COORD),
        ("dwCursorPosition", COORD),
        ("wAttributes", wintypes.WORD),
        ("srWindow", wintypes.SMALL_RECT),
        ("dwMaximumWindowSize", COORD),
    ]

    def __str__(self):
        return '(%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d)' % (
            self.dwSize.y, self.dwSize.x
            , self.dwCursorPosition.y, self.dwCursorPosition.x
            , self.wAttributes
            , self.srWindow.Top, self.srWindow.Left, self.srWindow.Bottom, self.srWindow.Right
            , self.dwMaximumWindowSize.y, self.dwMaximumWindowSize.y
        )
