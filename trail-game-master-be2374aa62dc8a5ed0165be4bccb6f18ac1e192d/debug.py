#!/usr/bin/python3
# coding=utf-8

# This file contains some useful debug tools

import time

import screen

debug_mode = False


def dprint(message):
    if debug_mode:
        screen.set_cursor_position(0, 0)
        print("DEBUG: " + str(message))
        time.sleep(2)
