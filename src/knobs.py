from __future__ import absolute_import

import os
import sys

import click
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(usecwd=True))

BOOLEAN_TRUE_STRINGS = ('true', 'on', 'ok', 'y', 'yes', '1')


class Knob(object):
    """
    A knob can be tuned to satisfaction. Lookup and _cast environment variables to
    the required type.
    >>> knob = Knob('WUNDER', 'BAR', description='Foo Bar')
    >>> knob
    Knob('WUNDER', 'BAR', description='Foo Bar')
    >>> knob.get()
    'BAR'
    >>> pirate_count = Knob('JOLLY_ROGER_PIRATES', 124, description='Yar')
    >>> pirate_count
    Knob('JOLLY_ROGER_PIRATES', 124, description='Yar')
    >>> pirate_count.get()
    124
    >>> pirate_count.get_type()
    <type 'int'>
    >>> rum_flag = Knob('HAVE_RUM', True)
    >>> rum_flag
    Knob('HAVE_RUM', True, description='')
    >>> rum_flag.get()
    True
    """

    _register = {}

    def __init__(self, env_name, default, description='', validator=None):
        """
        :param env_name: Name of environment variable
        :param default: Default knob setting
        :param description: What does this knob do
        :param validator: Callable to validate value
        """

        # the default's type sets the python type of the value
        # retrieved from the environment
        self._cast = type(default)

        self.env_name = env_name
        self.default = default
        self.description = description
        self.validator = validator

        self._register[env_name] = self

    def __repr__(self):
        return "{_class}('{env_name}', {default}, description='{desc}')".format(
            _class=self.__class__.__name__,
            env_name=self.env_name,
            default=repr(self.default),
            desc=self.description
        )

    def __call__(self):
        return self.get()

    def get_type(self):
        """ The type of this knob """
        return self._cast

    def get(self):
        source_value = os.getenv(self.env_name, self.default)

        # bool
        if self._cast == bool:
            if isinstance(source_value, str):
                return source_value.lower() in BOOLEAN_TRUE_STRINGS
            if isinstance(source_value, bool):
                return source_value

        try:
            val = self._cast(source_value)
        except ValueError as e:
            click.secho(e.message, err=True, color='red')
            sys.exit(1)

        if self.validator:
            val = self.validator(val)

        return val

    @classmethod
    def clear_registry(cls):
        """ Clear knob registry """
        cls._register = {}

    @classmethod
    def get_knob_defaults(cls):
        r""" Returns a string with defaults
        >>> Knob.get_knob_defaults()
        '#HAVE_RUM=True\n#JOLLY_ROGER_PIRATES=124\n#WUNDER=BAR'
        """

        return '\n'.join(
            ['#{knob}={default}'.format(knob=knob, default=cls._register[knob].default)
             for knob in sorted(cls._register.keys())]
        )
