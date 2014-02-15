#-----------------------------------------------------------------------------------------------------------------------
# Name:        Utils
# Purpose:     Util methods;
#
# Author:      Rafael Vasco
#
# Created:     24/03/13
# Copyright:   (c) Rafael 2013
# Licence:     <your licence>
#-----------------------------------------------------------------------------------------------------------------------

import os
import math
import random
import errno

from PyQt5.QtCore import Qt, QDir, QByteArray, QBuffer, QIODevice, QPoint
from PyQt5.QtGui import QImage, QTransform, QPainter, QPixmap, QColor
from PyQt5.QtWidgets import QFileDialog, QMessageBox


def clamp(value, minimum, maximum):

    return max(minimum, min(value, maximum))


def enum(*sequential, **named):

    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)


def sign(v):

    return cmp(v, 0)


def cmp(a, b):

    return (a > b) - (a < b)


def snap(value, increment):

    return int(math.floor(value // increment) * increment)


def snap_point(point, increment):

    return QPoint(round(math.floor(point.x() / increment) * increment),
                  round(math.floor(point.y() / increment) * increment))


def create_image(width, height):

    new_image = QImage(width, height, QImage.Format_ARGB32_Premultiplied)
    new_image.fill(Qt.transparent)
    return new_image


def load_image(file):

    new_image = QImage(file)
    return new_image.convertToFormat(QImage.Format_ARGB32_Premultiplied)


def get_file_extension(file_path):

    return os.path.splitext(file_path)[1].lower()


def show_openfile_dialog(label, name_filter):

    return QFileDialog.getOpenFileName(caption=label,
                                       directory=QDir.currentPath(),
                                       filter=name_filter)[0]


def show_open_files_dialog(label, name_filter):

    return QFileDialog.getOpenFileNames(caption=label,
                                        directory=QDir.currentPath(),
                                        filter=name_filter)[0]


def show_savefile_dialog(label, name_filter):
    return QFileDialog.getSaveFileName(caption=label,
                                       directory=QDir.currentPath(),
                                       filter=name_filter)[0]


def show_save_to_folder_dialog(label):
    return QFileDialog.getExistingDirectory(caption=label, directory=QDir.currentPath())


def show_info_message(parent, title, msg):

    QMessageBox.information(parent, title, msg)


def image_to_bytearray(image):

    byte_array = QByteArray()
    buffer = QBuffer(byte_array)
    buffer.open(QIODevice.WriteOnly)
    image.save(buffer, 'png')
    buffer.close()
    return byte_array


def byte_array_to_image(byteArray):

    image = QImage()
    image.loadFromData(byteArray, 'png')
    return image


# -----------------------------------------------------------------------------

# def multiply_matrix(m1, m2):
#
#     m1_11 = m1.m11()
#     m1_12 = m1.m12()
#     m1_21 = m1.m21()
#     m1_22 = m1.m22()
#     m1_dx = m1.dx()
#     m1_dy = m1.dy()
#
#     m2_11 = m2.m11()
#     m2_12 = m2.m12()
#     m2_21 = m2.m21()
#     m2_22 = m2.m22()
#     m2_dx = m2.dx()
#     m2_dy = m2.dy()
#
#     return QMatrix(m1_11 * m2_11 + m1_21 * m2_12,
#                    m1_12 * m2_11 + m1_22 * m2_12,
#                    m1_11 * m2_21 + m1_21 * m2_22,
#                    m1_12 * m2_21 + m1_22 * m2_22,
#                    round(m1_dx * m2_11 + m1_dy * m2_12 + m2_dx),
#                    round(m1_dx * m2_21 + m1_dy * m2_22 + m2_dy))


# -----------------------------------------------------------------------------

def generate_checker_tile(size, color1, color2):
    tile_size = size * 2

    tile = QImage(tile_size, tile_size, QImage.Format_ARGB32_Premultiplied)

    painter = QPainter()

    painter.begin(tile)

    painter.fillRect(0, 0, tile_size, tile_size, color1)
    painter.fillRect(0, 0, size, size, color2)
    painter.fillRect(size, size, size, size, color2)

    painter.end()

    tile_pixmap = QPixmap.fromImage(tile)

    return tile_pixmap


# ------------------------------------------------------------------------------

def random_color(hue=None, sat=None, val=None):
    hue = random.randint(0, 255) if hue is None else hue
    sat = random.randint(0, 255) if sat is None else sat
    val = random.randint(0, 255) if val is None else val

    color = QColor()
    color.setHsv(hue, sat, val)

    return color


# --------------------------------------------------------

def make_dir(root_folder, dir_name):

    path = os.path.join(root_folder, dir_name)

    try:
        os.makedirs(path)

    except OSError as exception:
        if exception.errno == errno.EEXIST:
            print('Already exists')
            return path
        else:
            raise exception

    return path
        
        


