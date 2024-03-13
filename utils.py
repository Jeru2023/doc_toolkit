import time
import os
from collections.abc import Sequence
import pkg_resources

from loguru import logger


def timer(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        class_name = args[0].__class__.__name__
        end_time = time.time()
        execution_time = end_time - start_time
        logger.debug(f"{class_name}.{func.__name__} executed in {execution_time:.4f} seconds.")
        return result

    return wrapper


def load_text(*file_paths, by_lines=False):
    with open(f_join(*file_paths), "r", encoding="utf-8") as fp:
        if by_lines:
            return fp.readlines()
        else:
            return fp.read()


def f_join(*file_paths):
    """
    join file paths and expand special symbols like `~` for home dir
    """
    file_paths = pack_varargs(file_paths)
    fpath = f_expand(os.path.join(*file_paths))
    if isinstance(fpath, str):
        fpath = fpath.strip()
    return fpath


def f_expand(fpath):
    return os.path.expandvars(os.path.expanduser(fpath))


def pack_varargs(args):
    """
    Pack *args or a single list arg as list

    def f(*args):
        arg_list = pack_varargs(args)
        # arg_list is now packed as a list
    """
    assert isinstance(args, tuple), "please input the tuple `args` as in *args"
    if len(args) == 1 and is_sequence(args[0]):
        return args[0]
    else:
        return args


def is_sequence(obj):
    """
    Returns:
      True if the sequence is a collections.Sequence and not a string.
    """
    return isinstance(obj, Sequence) and not isinstance(obj, str)


def get_root_path():
    package_path = pkg_resources.resource_filename(__name__, "")
    parent_path = os.path.dirname(package_path)
    return parent_path
