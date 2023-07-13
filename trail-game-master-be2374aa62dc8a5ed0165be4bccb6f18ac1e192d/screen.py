#!/usr/bin/python3
# coding=utf-8

# This file contains functions to help you operate the screen, such as clearing, drawing and flushing
# 	This is only for complex screens like the traveling screen, for other screens, use the print and input functions 

import ctypes
import os
import platform
import shutil
import subprocess
import sys

import pip

if platform.system() == "Windows":
    import win32_structs

try:
    import numpy
except ImportError:
    print("ERROR: Importing numpy failed, installing and restarting now..")
    pip.main(['install', 'numpy', '--user'])
    subprocess.call(['python', 'game.py'])
    quit()

stdout = None

width = 0
height = 0

# Holds "pixel" data on the currently shown screen
front_buffer = None

# Holds "pixel" data on the currently rendering and next to be shown screen
back_buffer = None

# These variables are used to optimise printing the buffer by skipping with the cursor to the start, and finishing before the end
buffer_start = {"x": None, "y": None}
buffer_end = {"x": 0, "y": 0}


def init():
    """Initialise the screen, call this before using any other functions.

    Returns:
        None

    """

    global stdout
    global front_buffer
    global back_buffer
    global width
    global height

    # Get the handle of the console's standard output (stdout)
    if platform.system() == "Windows":
        stdout = ctypes.windll.kernel32.GetStdHandle(-11)

    width = shutil.get_terminal_size()[0] - 1
    height = shutil.get_terminal_size()[1] - 1

    front_buffer = numpy.chararray((width, height))
    back_buffer = numpy.chararray((width, height))

    front_buffer.fill("")
    back_buffer.fill("")


def set_cursor_visibility(visible):
    """Change the cursor visibility status

    Args:
        visible (bool): True to show the cursor, False to hide.

    Returns:
        None

    """

    if platform.system() == "Windows":
        cursor_info = win32_structs.CONSOLE_CURSOR_INFO()

        ctypes.windll.kernel32.GetConsoleCursorInfo(stdout, ctypes.byref(cursor_info))

        cursor_info.visible = visible

        ctypes.windll.kernel32.SetConsoleCursorInfo(stdout, ctypes.byref(cursor_info))
    else:
        if visible:
            print("\e[?25h")
        else:
            print("\e[?25l")


def wait_key():
    """Wait for a key to be pressed and return that key from the function.

    Returns:
        basestring: Return a byte string with the key code.

    """

    result = None
    if platform.system() == "Windows":
        import msvcrt
        result = msvcrt.getch()
    else:
        import termios
        fd = sys.stdin.fileno()

        old_term = termios.tcgetattr(fd)
        new_attr = termios.tcgetattr(fd)
        new_attr[3] = new_attr[3] & ~termios.ICANON & ~termios.ECHO
        termios.tcsetattr(fd, termios.TCSANOW, new_attr)

        try:
            result = sys.stdin.read(1)
        except IOError:
            pass
        finally:
            termios.tcsetattr(fd, termios.TCSAFLUSH, old_term)

    return result


def clear():
    """Clear the console screen.

    Returns:
        None

    """

    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")


def get_width():
    """Get the width of the console screen.

    Returns:
        int: Width of the console screen.

    """

    return width


def get_height():
    """Get the height of the console screen.

    Returns:
        int: Height of the console screen.

    """

    return height


def draw_bordered_rect(rect_x, rect_y, rect_width, rect_height, fill_char=" "):
    """Draw a bordered rectangle to the screen.

    Args:
        rect_x (int): The x position of the rect.
        rect_y (int): The y position of the rect.
        rect_width (int): The width of the rect.
        rect_height (int): The height of the rect.
        fill_char (str): A single character string defining what the rect should be filled with (clears by default).

    Returns:
        None

    """

    for x in range(rect_x + 1, rect_x + rect_width - 1):
        draw_pixel(x, rect_y, "═")

    for x in range(rect_x + 1, rect_x + rect_width - 1):
        draw_pixel(x, rect_y + rect_height - 1, "═")

    for y in range(rect_y + 1, rect_y + rect_height - 1):
        draw_pixel(rect_x, y, "║")

    for y in range(rect_y + 1, rect_y + rect_height - 1):
        draw_pixel(rect_x + rect_width - 1, y, "║")

    draw_pixel(rect_x, rect_y, "╔")
    draw_pixel(rect_x + rect_width - 1, rect_y, "╗")
    draw_pixel(rect_x, rect_y + rect_height - 1, "╚")
    draw_pixel(rect_x + rect_width - 1, rect_y + rect_height - 1, "╝")

    if fill_char is not None:
        for x in range(rect_x + 1, rect_x + rect_width - 1):
            for y in range(rect_y + 1, rect_y + rect_height - 1):
                draw_pixel(x, y, fill_char)


def draw_progress_bar(bar_x, bar_y, length, progress):
    """Draw a progress bar to the screen.

    Args:
        bar_x (int): The x position of the progress bar.
        bar_y (int): The y position of the progress bar.
        length (int): The length (width) of the progress bar.
        progress (float): A value between 0 and 1 defining how far along the progress bar should be filled.

    Returns:
        None

    """

    remaining_bars = int(max(progress * length, 1))

    draw_text(bar_x, bar_y, "[" + ("█" * remaining_bars) + (" " * (length - remaining_bars)) + "]")


def draw_ascii_image(image_x, image_y, ascii_image):
    """Draw an ascii image to the screen.

    Args:
        image_x (int): The x position of the image.
        image_y (int): The y position of the image.
        ascii_image (dict): A image dictionary returned from ascii_helper.load_image().

    Returns:
        None

    """

    image_buffer = ascii_image["image_buffer"]
    image_width = ascii_image["width"]
    image_height = ascii_image["height"]

    min_x = max(image_x, 0)
    max_x = min(image_x + image_width, width)

    min_y = max(image_y, 0)
    max_y = min(image_y + image_height, height)

    image_x = 0
    image_y = 0

    for x in range(min_x, max_x):
        for y in range(min_y, max_y):
            draw_pixel(x, y, image_buffer[image_x][image_y])

            image_y += 1

        image_y = 0
        image_x += 1


def get_decision_input(decisions, selected_index=1):
    """Wait until the user inputs a key, and adjust the selected_index accordingly.

    Args:
        decisions (list): A list of str that will be shown as the options on this screen
        selected_index (int): The currently selected option (one indexed).

    Returns:
        tuple: First the new selected_index, then a bool stating if they have selected this option as final.

    """

    decisions_count = len(decisions)

    key = wait_key()

    if key == b"\r":
        return selected_index, True
    elif key == b"\xe0":
        key = wait_key()
        key_ordinal = ord(key)

        if key_ordinal == 80:
            selected_index += 1
        elif key_ordinal == 72:
            selected_index -= 1

    if selected_index > decisions_count:
        selected_index = decisions_count
    elif selected_index < 1:
        selected_index = 1

    return selected_index, False


def draw_decision(decision_x, decision_y, decisions, selected_index=1):
    """Draw a list of options, with one selected.

    Args:
        decision_x (int): The x position of the box.
        decision_y (int): The y position of the box.
        decisions (list): A list of str that will be shown as the options on this screen
        selected_index (int): The currently selected option (one indexed).

    Returns:
        None

    """

    decisions_count = len(decisions)

    for i in range(decisions_count):
        decision = decisions[i]

        y = decision_y + (i * 2)

        text_length = len(decision)

        x = decision_x

        if decision_x is None:
            x = int((get_width() / 2) - ((text_length + 3) / 2))

        draw_text(x + 2, y, decision)

        if selected_index == i + 1:
            draw_text(x, y, ">")
            draw_text(x + text_length + 3, y, "<")


def draw_decision_box(body_text, decisions, selected_index=1, decision_x=None, decision_y=None, max_width=None,
                      max_height=None):
    """Draw a box with a set of decision options.

    Args:
        body_text (str): The text at the top of the box.
        decisions (list): A list of str that will be shown as the options on this screen
        selected_index (int): The currently selected option (one indexed).
        decision_x (int): The x position of the box, leave to None for centering.
        decision_y (int): The y position of the box, leave to None for centering.
        max_width (int): The maximum width of the box, leave to None for auto adjusting.
        max_height (int): The maximum height of the box, leave to None for auto adjusting.

    Returns:
        tuple: The chosen x and y values of the top left of the box. Useful if you used the auto centering feature.

    """

    box_width = int(get_width() - get_width() / 6)
    box_height = int(get_height() - get_height() / 6)

    if max_width is not None:
        box_width = min(box_width, max_width)

    if max_height is not None:
        box_height = min(box_height, max_height)

    if decision_x is None:
        decision_x = int((get_width() / 2) - (box_width / 2))

    if decision_y is None:
        decision_y = int((get_height() / 2) - (box_height / 2))

    draw_bordered_rect(decision_x, decision_y, box_width, box_height, " ")
    lines = draw_text_wrapped(decision_x + 6, decision_y + 3, body_text, box_width - 1, False)

    draw_decision(decision_x + 5, decision_y + lines + 6, decisions, selected_index)

    return decision_x, decision_y


def draw_pixel(pixel_x, pixel_y, pixel_char):
    """Draw a pixel at x and y, it will clip to the size of the screen.

    Args:
        pixel_x (int): The x position of the pixel.
        pixel_y (int): The y position of the pixel.
        pixel_char (str): A single character string that you want to fill the pixel with

    Returns:
        None

    """

    if pixel_char != "" and pixel_char != " ":
        if buffer_start["y"] is None or pixel_y < buffer_start["y"]:
            buffer_start["y"] = pixel_y

        if buffer_end["y"] is None or pixel_y > buffer_end["y"]:
            buffer_end["y"] = pixel_y

    if pixel_x >= width or pixel_x < 0 or pixel_y >= height or pixel_y < 0:
        return

    try:
        back_buffer[pixel_x][pixel_y] = pixel_char
    except UnicodeEncodeError:
        back_buffer[pixel_x][pixel_y] = str(pixel_char).encode(sys.stdout.encoding)


def draw_text_wrapped(text_x, text_y, text, max_length, indent=False):
    """Draw some text, and wrap it to the next line if it goes over max_length.

    Args:
        text_x (int): The x position of the text.
        text_y (int): The y position of the text.
        text (str): The text you want to print, may include "\n" to force newlines.
        max_length (int): The maximum length the text should print until it wraps to the next line.
        indent (bool): If the wrapped lines should be indented from the first line or not, by default it's False.

    Returns:
        int: The amount of vertical lines used.

    """

    words = text.split(" ")

    x = text_x
    y = text_y

    for word in words:
        word_length = len(word)

        if x + word_length > max_length:
            x = text_x

            if indent:
                x += 2

            y += 1

        for i in range(word_length):
            char = word[i]

            if char is "\n":
                y += 1
                x = text_x

                if indent:
                    x += 2

                continue
            else:
                draw_pixel(x, y, char)

            if x > max_length:
                x = text_x

                if indent:
                    x += 2

                y += 1

            x += 1

        x += 1

    return y - text_y


def draw_text(text_x, text_y, text):
    """Draw some text.

    Args:
        text_x (int): The x position of the text.
        text_y (int): The y position of the text.
        text (str): The text you want to print.

    Returns:
        None

    """

    text = text
    text_length = len(text)

    for x in range(text_length):
        draw_pixel(x + text_x, text_y, text[x])


def draw_ascii_font_text(text_x, text_y, text, font):
    """Draw some text in an ascii font.

    Args:
        text_x (int): The x position of the text.
        text_y (int): The y position of the text.
        text (str): The text you want to print.
        font (dict): A font dictionary returned from figlet_helper.load_font().

    Returns:
        None

    """

    last_width = 0

    for char in text:
        text_x += last_width
        char_code = ord(char)
        char_start = ((char_code - 32) * font["height"])

        last_width = 0

        for i in range(font["height"]):
            line = font["font_data"][char_start + i + 1]
            line_length = len(line)

            if line_length > last_width:
                last_width = line_length - 2

            char_x = text_x

            for x in line:
                if x != "@":
                    if x == font["hardblank_character"]:
                        draw_pixel(char_x, text_y + i, " ")
                    else:
                        draw_pixel(char_x, text_y + i, x)
                else:
                    if i + 1 >= font["height"]:
                        break
                char_x += 1


def print_notification(message, redraw_on_exit=True):
    """Draws a notification and waits for a key, doesn't use the back buffer to keep it intact.

    Args:
        message (str): Some text to notify the player with.
        redraw_on_exit (bool): If the function should redraw the previous screen or not.

    Returns:
        None

    """

    set_cursor_visibility(False)
    message_length = len(message)

    x_start = (width / 2) - (message_length / 2)
    y_start = (height / 2)

    set_cursor_position(x_start - 3, y_start - 2)

    stdout_write_flush("╔" + "═" * (message_length + 4) + "╗")

    set_cursor_position(x_start - 2, y_start - 1)

    stdout_write_flush(" " * (message_length + 4))

    set_cursor_position(x_start, y_start)

    stdout_write_flush(message)

    set_cursor_position(x_start - 2, y_start + 1)

    stdout_write_flush(" " * (message_length + 4))

    for j in range(-1, 2):
        set_cursor_position(x_start - 3, y_start + j)
        stdout_write_flush("║")

    for j in range(-1, 2):
        set_cursor_position(x_start + message_length + 2, y_start + j)
        stdout_write_flush("║")

    set_cursor_position(x_start - 2, y_start)
    stdout_write_flush(" " * 2)

    set_cursor_position(x_start + message_length, y_start)
    stdout_write_flush(" " * 2)

    set_cursor_position(x_start - 3, y_start + 2)

    stdout_write_flush("╚" + "═" * (message_length + 4) + "╝")

    set_cursor_position(0, 0)

    wait_key()

    if redraw_on_exit:
        refresh()

    set_cursor_visibility(True)


def stdout_write_flush(message):
    """Write a message to stdout and flush (display) it to the screen.

    Args:
        message (str): The message you want to show.

    Returns:
        None

    """

    sys.stdout.write(message)
    sys.stdout.flush()


def set_cursor_position(cursor_x, cursor_y):
    """Sets the x and y position of the console cursor, where [0,0] is the top left of the screen.

    Args:
        cursor_x (int): The x position of the cursor.
        cursor_y (int): The y position of the cursor.

    Returns:
        None

    """

    if platform.system() == "Windows":
        adjusted_position = win32_structs.COORD(int(cursor_x), int(cursor_y))

        ctypes.windll.kernel32.SetConsoleCursorPosition(stdout, adjusted_position)
    else:
        stdout_write_flush("\033[" + str(int(cursor_y) + 1) + ";" + str(int(cursor_x) + 1) + "H")


def refresh():
    """Re-renders the front buffer (current buffer) to the screen.

    Returns:
        None

    """

    render_buffer(front_buffer)


def flush():
    """Clear the back buffer and draw it's contents to the screen.

    Returns:
        None

    """

    render_buffer(back_buffer)

    numpy.copyto(front_buffer, back_buffer)

    back_buffer.fill("")


def render_buffer(buffer_to_render):
    """Render a numpy character array to the screen.

    Args:
        buffer_to_render (chararray): A character array from numpy for which you want to render.

    Returns:
        None

    """

    if platform.system() == "Windows":
        buf = (win32_structs.CHAR_INFO * (width * height))()

        x = 0
        y = 0

        for c in buf:
            pixel = buffer_to_render[x][y]

            if pixel == "":
                pixel = b" "

            c.ascii = pixel
            c.attr = 7

            x += 1

            if x >= width:
                x = 0
                y += 1

        console_handle = ctypes.windll.kernel32.CreateFileA(
            ctypes.create_string_buffer(b"CONOUT$"),
            0x40000000 | 0x80000000,  # Generic read and write permissions
            1 | 2,  # We want read and write permissions
            0,
            3,  # Open the "file" only if it exists
            0,
            0)

        if console_handle == 0:
            raise ctypes.WinError()

        if ctypes.windll.kernel32.WriteConsoleOutputA(console_handle, ctypes.byref(buf),
                                                      win32_structs.COORD(width, height),
                                                      win32_structs.COORD(0, 0),
                                                      ctypes.byref(win32_structs.SMALL_RECT(0, 0, width, height))) == 0:
            raise ctypes.WinError()

        # NOTE: Always remember to close your handles!
        ctypes.windll.kernel32.CloseHandle(console_handle)
    else:
        clear()

        start_x = buffer_start["x"]
        start_y = buffer_start["y"]

        end_y = buffer_end["y"]

        if start_x is None:
            start_x = 1

        if start_y is None:
            start_y = 1

        if end_y is None:
            end_y = 1

        set_cursor_position(start_x, start_y)

        y = 0
        for col in buffer_to_render.T:
            y += 1

            if y < start_y:
                continue

            content = ""
            for cell in col:
                cell_string = str(cell)[2:3]
                if cell_string != "":
                    content += cell_string
                else:
                    content += " "

            print(content)

            if y > end_y:
                break
