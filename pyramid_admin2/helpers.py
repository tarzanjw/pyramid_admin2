import inspect
import re
import six
from datetime import datetime

__author__ = 'tarzan'

def name_to_underscore(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def name_to_words(name):
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    words = re.split('[_\s]+', name)

    return ' '.join([w.title() for w in words])


def cell_datatype(val):
    """ Get datatype for a value
    :param val: the value
    :return: its datatype
    :rtype: string
    """
    if val is None:
        return 'none'
    if isinstance(val, (list, tuple, set)):
        return 'list'
    if isinstance(val, dict):
        return 'dict'
    if isinstance(val, bool):
        return 'bool'
    if isinstance(val, six.integer_types + (float, )):
        return 'number'
    if isinstance(val, datetime):
        return 'datetime'
    if isinstance(val, six.string_types):
        return 'longtext' if len(val) > 40 else 'text'
    if inspect.isclass(type(val)):
        return 'class'
    return 'generic'
