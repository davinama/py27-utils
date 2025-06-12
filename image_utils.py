"""
image_utils.py

This script contains some useful functions for image editing.
They are verified on Windows, but not verified on Mac and Linux.

Author: Davina Ma Heming
Date: 2025.06.12
Environment: Python 2.7
"""

import os
import sys
import math
from natsort import natsorted, ns
from PIL import Image
from . import path_utils, other_utils

import logging
logger = logging.getLogger(__name__)


def rename_images_to_format(folder_path, suffix, delete_non_img=False):
    """
    Rename images in folder_path to the format of suffix.xxxx.ext        # e.g. thumbnail.0000.jpg

    :type folder_path: string / unicode
    :type suffix: string
    :type delete_non_img: bool
    """
    if not folder_path or not os.path.exists(folder_path):
        return
    
    # Sort the files in folder_path as the default windows sorting method
    file_list = natsorted(os.listdir(folder_path), alg=ns.PATH | ns.IGNORECASE)
    if not file_list:
        return
    
    index = 0
    exception_list  =[]
    for file in file_list:
        if file.lower().endswith((".png", ".jpg", ".jpeg", ".tif", ".tiff", ".tga", ".bmp", ".dds")):
            ori_file_basename, file_extension = os.path.splitext(file)
            new_file_name = suffix + "." + str("%04d" % index) + file_extension
            index += 1
            try:
                os.rename(os.path.join(folder_path, file), os.path.join(folder_path, new_file_name))
            except Exception as err:
                exception_list.append("%s: %s"%(file, str(err)))
                continue
        elif delete_non_img:
            try:
                os.remove(os.path.join(folder_path, file))
            except:
                continue

    if exception_list:
        raise Exception("Error while Renaming files: \n"+'\n'.join(exception_list))
    

def try_reduce_image_size(input_path, size_threshold):
    """
    Try reducing images size in input_path (if input_path is folder),
    or reduce input_path's image size (if input_path is image path)
    to be smaller than or equal to size_threshold

    :type input_path: string / unicode      # folder path or image path
    :type size_threshold: int / float
    :rtype: bool        # True for edited, False for not edited
    """

    def reduce_single_img_size(img_path):
        """
        Reduce the image size of img_path

        :type img_path: string / unicode
        """
        try:
            img = Image.open(img_path)
        except:
            logger.warning("PIL cannot open image: %s"%img_path)
            return
        
        try:
            img.save(img_path, optimize=True)
        except Exception as err:
            logger.error("Error while saving image %s: %s"%(img_path, str(err)))

        return
    
    # if input_path is a directory
    if os.path.isdir(input_path):
        img_path_list = []

        # Check if any image needs to be reduced in input_path,
        # and prepare argument tuple for these images
        for f in os.listdir(input_path):
            if f.lower().endswith((".png", ".jpg", ".jpeg", ".tif", ".tiff", ".tga", ".bmp", ".dds")):
                img_path = os.path.join(input_path, f)
                img_size = int(math.floor(os.path.getsize(img_path) / 1024 ** 2))
                if img_size >= size_threshold:
                    img_path_list.append((img_path,))

        if img_path_list:
            other_utils.multi_thread_run(reduce_single_img_size, img_path_list)
            return True
        
    # if input_path is file
    else:
        if not input_path.lower().endswith((".png", ".jpg", ".jpeg", ".tif", ".tiff", ".tga", ".bmp", ".dds")):
            return False
        img_size = int(math.floor(os.path.getsize(input_path) / 1024 ** 2))
        if img_size >= size_threshold:
            reduce_single_img_size(input_path)
            return True
        
    return False


def image_count(folder_path):
    """
    Count image file number in folder_path, and get first image path

    :type folder_path: string / unicode
    :rtype: int, string/unicode     # image file number, first image path
    """
    if not folder_path or not os.path.exists(folder_path):
        return 0, ""
    
    # Sort the files in folder_path as the default windows sorting method
    file_list = natsorted(os.listdir(folder_path), alg=ns.PATH | ns.IGNORECASE)
    if not file_list:
        return 0, ""
    
    first_img_path = ""
    img_count = 0
    for f in file_list:
        if f.lower().endswith((".png", ".jpg", ".jpeg", ".tif", ".tiff", ".tga", ".bmp", ".dds")):
            img_count += 1
            if not first_img_path:
                first_img_path = path_utils.norm_path(os.path.join(folder_path, f))

    return img_count, first_img_path
