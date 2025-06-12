"""
other_utils.py

This script contains some other useful functions in python
besides path-functions (path_utils.py), image-functions (image_utils.py), and encoding-decoding-functions (encode_decode_utils.py).

Author: Davina Ma Heming
Date: 2025.06.12
Environment: Python 2.7
"""

import os
import sys
import traceback
import inspect
import pprint
import threading
from Queue import Queue

import logging
logger = logging.getLogger(__name__)


def multi_thread_run(func, thread_limit, args_list):
    """
    Run the given function multi-threadingly, with a thread limit

    :type func: function
    :type thread_limit: int     # positive integer
    :type args_list: list[(val1, val2,),(val3, val4,),...]      # (val1, val2,) is used for job1; (val3,val4,) is used for job2; etc.
    """
    if not args_list:
        return
    
    exception_list = []

    def worker_func(q):
        while not q.empty():
            args = q.get()
            try:
                func(*args)
            except Exception as err:
                error_msg = traceback.format_exc()
                exception_list.append(error_msg)
            q.task_done()

    jobs = Queue()

    for job_args in args_list:
        jobs.put(job_args)

    for t in range(thread_limit):
        worker = threading.Thread(target=worker_func, args=(jobs,))
        worker.start()

    jobs.join()
    if exception_list:
        raise Exception('\n'.join(exception_list))
    

def print_trace():
    """
    A convenient way to print function call stack,
    especially when running inside Maya script editor.

    Usage:
    Add print_trace() inside your function.
    """
    format_stack = traceback.format_stack()
    format_stack.pop()      # ignore the current print_trace() function
    # format_stack = format_stack[::-1]     # print from the most recent function to the root
    print(''.join(format_stack))


def print_args():
    """
    A convenient way to print argument values passed to a function,
    especially when running inside Maya script editor.

    Usage:
    Add print_args() inside your function.
    """
    outer_frames = inspect.getouterframes(inspect.currentframe())
    if len(outer_frames) > 1:
        args_info_tuple = inspect.getargvalues(outer_frames[1][0])
        arg_dict = args_info_tuple[len(args_info_tuple)-1]
        print(pprint.pformat(arg_dict))