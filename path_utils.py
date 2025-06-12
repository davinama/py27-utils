"""
path_utils.py

This script contains some useful path-related functions.
They are verified on Windows, but not verified on Mac and Linux.

Author: Davina Ma Heming
Date: 2025.06.12
Environment: Python 2.7
"""

import os
import sys
import re
import shutil
import subprocess
from . import encode_decode_utils

import logging
logger = logging.getLogger(__name__)


CREATE_NO_WINDOW = 0x8000000
ROBOCOPY_ERROR_BOOK = {
    0: "No files were copied. No failure was met. No files were mismatched. The files already exist in the destination directory; so the copy operation was skipped.",
    1: "All files were copied successfully.",
    2: "There are some additional files in the destination directory that aren't present in the source directory. No files were copied.",
    3: "Some files were copied. Additional files were present. No failure was met.",
    4: "Some Mismatched files or directories were detected. Examine the output log. Housekeeping might be required.",
    5: "Some files were copied. Some files were mismatched. No failure was met.",
    6: "Additional files and mismatched files exist. No files were copied and no failures were met. Which means that the files already exist in the destination directory.",
    7: "Files were copied, a file mismatch was present, and additional files were present.",
    8: "Some files or directories could not be copied (copy errors occurred and the retry limit was exceeded). Check these errors further.",
    16: "Serious error. Robocopy did not copy any files. Either a usage error or an error due to insufficient access privileges on the source or destination directories."
}


def norm_path(path):
    """
    Return a normalized path containing only forward slashes.

    :type path: string / unicode
    :rtype: string / unicode
    """
    # Check and support the UNC path structure
    unc = path.startswith("//") or path.startswith("\\\\")

    path = path.replace("//", "/")
    path = path.replace("\\", "/")

    if path.endswith("/") and not path.endswith(":/"):
        path = path.rstrip("/")

    # Make sure we retain the UNC path structure
    if unc and not path.startswith("//") and path.startswith("/"):
        path = "/" + path

    return path


def rm_tree(path):
    """
    Use this function instead of shutil.rmtree,
    to avoid windows error like "PermissioError: [WinError 5] Access Denied"
    
    :type path: string / unicode
    """

    def rm_tree_on_error(func, path, exc_info):
        """
        Error handler for shutil.rmtree, in cases that shutil.rmtree raise error like:
        "PermissioError: [WinError 5] Access Denied"
        Usage: shutil.rmtree(path, onerror=rm_tree_on_error)

        :type func: function
        :type path: string / unicode
        :type exc_info: tuple(type, value, traceback)
        """
        import stat
        if not os.access(path, os.W_OK):
            os.chmod(path, stat.S_IWUSR)
            func(path)
        else:
            raise

    shutil.rmtree(path, onerror=rm_tree_on_error)


def copy_path(src, dst, force=True):
    """
    Make a copy of the given src path to the given dst path.

    :type src: utf-8 / gbk / unicode     # folder path or file path
    :type dst: utf-8 / gbk / unicode     # folder path or file path
    :type force: bool
    :rtype: string
    """
    # Convert src & dst to gbk
    if isinstance(src, str):
        try:
            src = src.decode("utf-8")
        except UnicodeDecodeError:
            src = src.decode("gbk")
    if isinstance(dst, str):
        try:
            dst = dst.decode("utf-8")
        except UnicodeDecodeError:
            dst = dst.decode("gbk")

    src = src.encode("gbk")
    dst = dst.encode("gbk")

    # If dst is only a basename, then complete dst with the directory path of src
    if "/" not in dst and "\\" not in dst:
        dst = os.path.join(os.path.dirname(src), dst)

    # Change the slashes to be forward slashes
    src = norm_path(src)
    dst = norm_path(dst)

    if src == dst:
        msg = u"The source path and destination path are the same: {0}"
        raise IOError(msg.format(src))
    
    if not force and os.path.exists(dst):
        msg = u"Cannot copy over an existing path: '{0}'"
        raise IOError(msg.format(dst))
    
    if force and os.path.exists(dst):
        try:
            if os.path.isdir(dst):
                rm_tree(dst)
            else:
                os.remove(dst)
        except:
            raise

    # Make sure the destination directory exists
    dst_dir = os.path.dirname(dst)
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)

    # If src is a file, use shutil.copy
    if os.path.isfile(src):
        shutil.copy(src, dst)
    # If src is a directory, use windows's robocopy to speed up the process
    else:
        try:
            subprocess.check_output(['robocopy', src, dst, '/E', '/MT:32'], creationflags=CREATE_NO_WINDOW)
        except subprocess.CalledProcessError as cperr:
            # For robocopy, returncode == 1 means success.
            # But for subprocess, return 1 means error.
            # So we only raise the error when returncode != 1.
            if cperr.returncode != 1:
                error_explain = ROBOCOPY_ERROR_BOOK.get(cperr.returncode, "")
                raise IOError("Robocopy copy folder error: code %d (%s)"%(cperr.returncode, error_explain))
        # For robocopy, returncode == 0 means "The files already exist in the destination directory".
        # But for subprocess, return 0 means success.
        # So we print a message to show this error (This error is not severe, so we don't raise an Exception)
        else:
            logger.info("Destination folder already exists")

    return dst


def move_path(src, dst):
    """
    Move src to dst.
    This function is to avoid the GBK encoding error.

    :type src: utf-8 / gbk / unicode
    :type dst: utf-8 / gbk / unicode
    """
    # Convert src & dst to gbk
    if isinstance(src, str):
        try:
            src = src.decode("utf-8")
        except UnicodeDecodeError:
            src = src.decode("gbk")
    if isinstance(dst, str):
        try:
            dst = dst.decode("utf-8")
        except UnicodeDecodeError:
            dst = dst.decode("gbk")

    src = src.encode("gbk")
    dst = dst.encode("gbk")

    shutil.move(src, dst)


def path_begin_with_ip(path):
    """
    Check whether the given path starts with an ip address.
    If found IP address, return the ip address (in format of "//127.0.0.1").
    Else, return an empty string

    :type path: string / unicode
    :rtype: string / unicode     # in format of "//127.0.0.1"
    """
    if not path:
        return ""
    
    path = norm_path(path)
    
    try:
        path = encode_decode_utils.coding_transition(path, "unicode")
    except:
        raise

    pattern = r"""
        ^// # 从前缀//开始
        ( # 匹配完整的 IPv4 地址
            (25[0-5] # 250-255
            | 2[0-4][0-9] # 200-249
            | 1[0-9]{2} # 100-199
            | [1-9][0-9] # 10-99
            | [0-9] # 0-9
            ) \. # 以上匹配一个数字段后跟一个点
        ){3} # 需要重复 3 次
        (25[0-5] # 255
        | 2[0-4][0-9] # 200-249
        | 1[0-9]{2} # 100-199
        | [1-9][0-9] # 10-99
        | [0-9] # 0-9
        ) # 最后一个数字段，不带点
    """
    match_obj = re.search(pattern, path, re.VERBOSE)
    return match_obj.group() if match_obj else ""