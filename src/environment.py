# forked, adapted and merged from
# https://github.com/theskumar/python-dotenv
# https://github.com/mattseymour/python-env

import codecs
import os
import re
import sys
import warnings
from collections import OrderedDict

__escape_decoder = codecs.getdecoder('unicode_escape')
__posix_variable = re.compile(r'\$\{[^\}]*\}')


def decode_escaped(escaped):
    return __escape_decoder(escaped)[0]


def load_dotenv(dotenv_path, verbose=False):
    """
    Read a .env file and load into os.environ.

    :param dotenv_path:
    :type dotenv_path: str
    :param verbose: verbosity flag, raise warning if path does not exist
    :return: success flag
    """
    if not os.path.exists(dotenv_path):
        if verbose:
            warnings.warn(f"Not loading {dotenv_path}, it doesn't exist.")
        return None
    for k, v in dotenv_values(dotenv_path).items():
        os.environ.setdefault(k, v)
    return True


def get_key(dotenv_path, key_to_get, verbose=False):
    """
    Gets the value of a given key from the given .env

    If the .env path given doesn't exist, fails
    :param dotenv_path: path
    :param key_to_get: key
    :param verbose: verbosity flag, raise warning if path does not exist
    :return: value of variable from environment file or None
    """
    key_to_get = str(key_to_get)
    if not os.path.exists(dotenv_path):
        if verbose:
            warnings.warn(f"Can't read {dotenv_path}, it doesn't exist.")
        return None
    dotenv_as_dict = dotenv_values(dotenv_path)
    if key_to_get in dotenv_as_dict:
        return dotenv_as_dict[key_to_get]
    else:
        if verbose:
            warnings.warn(f"key {key_to_get} not found in {dotenv_path}.")
        return None


def set_key(dotenv_path, key_to_set, value_to_set, quote_mode='always', verbose=False):
    """
    Adds or Updates a key/value to the given .env

    If the .env path given doesn't exist, fails instead of risking creating
    an orphan .env somewhere in the file-system

    :param dotenv_path: env path
    :param key_to_set: key
    :param value_to_set: value
    :param quote_mode: quote value in .env file
    :param verbose: verbosity flag, raise warning if path does not exist
    :return: tuple (fail/win, key, value)
    """
    key_to_set = str(key_to_set)
    value_to_set = str(value_to_set).strip("'").strip('"')
    if not os.path.exists(dotenv_path):
        if verbose:
            warnings.warn(f"Can't write to {dotenv_path}, it doesn't exist.")
        return None, key_to_set, value_to_set

    dotenv_as_dict = OrderedDict(parse_dotenv(dotenv_path))
    dotenv_as_dict[key_to_set] = value_to_set
    success = flatten_and_write(dotenv_path, dotenv_as_dict, quote_mode)

    return success, key_to_set, value_to_set


def unset_key(dotenv_path, key_to_unset, quote_mode='always', verbose=False):
    """
    Removes a given key from the given .env

    If the .env path given doesn't exist, fails
    If the given key doesn't exist in the .env, fails

    :param dotenv_path: env path
    :param key_to_unset: value
    :param quote_mode: quote value in .env file
    :param verbose: verbosity flag, raise warning if path does not exist
    :return: tuple (fail/win, key)
    """
    key_to_unset = str(key_to_unset)
    if not os.path.exists(dotenv_path):
        if verbose:
            warnings.warn(f"Can't delete from {dotenv_path}, it doesn't exist.")
        return None, key_to_unset
    dotenv_as_dict = dotenv_values(dotenv_path)
    if key_to_unset in dotenv_as_dict:
        dotenv_as_dict.pop(key_to_unset, None)
    else:
        if verbose:
            warnings.warn(f"Key {key_to_unset} not removed from {dotenv_path}, key doesn't exist.")
        return None, key_to_unset

    success = flatten_and_write(dotenv_path, dotenv_as_dict, quote_mode)
    return success, key_to_unset


def dotenv_values(dotenv_path):
    """
    :param dotenv_path: env file
    :return: ordered dict
    """
    values = OrderedDict(parse_dotenv(dotenv_path))
    values = resolve_nested_variables(values)
    return values


def parse_dotenv(dotenv_path):
    """
    Parses the dotenv file, comments (#) are ignored.
    A key must have a '=' to mark it as a key. Strings without a '='
    are ignored.

    :param dotenv_path:
    :return: generator yielding (key,value)
    """
    with open(dotenv_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            k, v = line.split('=', 1)

            # Remove any leading and trailing spaces in key, value
            k, v = k.strip(), v.strip()

            if len(v) > 0:
                quoted = v[0] == v[len(v) - 1] in ['"', "'"]

                if quoted:
                    v = decode_escaped(v[1:-1])

            yield k, v


def resolve_nested_variables(values):
    def _replacement(name):
        """
        get appropriate value for a variable name.
        first search in environ, if not found,
        then look into the dotenv variables
        """
        ret = os.getenv(name, values.get(name, ""))
        return ret

    def _re_sub_callback(match_object):
        """
        From a match object get the variable name and return
        the correct replacement
        """
        return _replacement(match_object.group()[2:-1])

    for k, v in values.items():
        values[k] = __posix_variable.sub(_re_sub_callback, v)

    return values


def _get_format(value, quote_mode='always'):
    """
    Returns the quote format depending on the quote_mode.
    This determines if the key value will be quoted when written to
    the env file.

    :param value:
    :param quote_mode:
    :return: str
    :raises: KeyError if the quote_mode is unknown
    """

    formats = {'always': '{key}="{value}"\n', 'auto': '{key}={value}\n'}

    if quote_mode not in formats.keys():
        return KeyError(f'quote_mode {quote_mode} is invalid')

    _mode = quote_mode
    if quote_mode == 'auto' and ' ' in value:
        _mode = 'always'
    return formats.get(_mode)


def flatten_and_write(dotenv_path, dotenv_as_dict, quote_mode='always'):
    """
    Writes dotenv_as_dict to dotenv_path, flattening the values
    :param dotenv_path: .env path
    :param dotenv_as_dict: dict
    :param quote_mode:
    :return:
    """
    with open(dotenv_path, 'w') as f:
        for k, v in dotenv_as_dict.items():
            str_format = _get_format(v, quote_mode)
            f.write(str_format.format(key=k, value=v))
    return True


def _walk_to_root(path):
    """
    Yield directories starting from the given directory up to the root
    """
    if not os.path.exists(path):
        raise IOError('Starting path not found')

    if os.path.isfile(path):
        path = os.path.dirname(path)

    last_dir = None
    current_dir = os.path.abspath(path)
    while last_dir != current_dir:
        yield current_dir
        parent_dir = os.path.abspath(os.path.join(current_dir, os.path.pardir))
        last_dir, current_dir = current_dir, parent_dir


def find_dotenv(filename='.env', raise_error_if_not_found=False, usecwd=False):
    """
    Search in increasingly higher folders for the given file

    Returns path to the file if found, or an empty string otherwise
    """
    if usecwd or '__file__' not in globals():
        # should work without __file__, e.g. in REPL or IPython notebook
        path = os.getcwd()
    else:
        # will work for .py files
        frame_filename = sys._getframe().f_back.f_code.co_filename
        path = os.path.dirname(os.path.abspath(frame_filename))

    for dirname in _walk_to_root(path):
        check_path = os.path.join(dirname, filename)
        if os.path.exists(check_path):
            return check_path

    if raise_error_if_not_found:
        raise IOError('File not found')

    return ''
