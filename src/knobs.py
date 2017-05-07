from __future__ import absolute_import

import os
import sys

import click
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(usecwd=True))

BOOLEAN_TRUE_STRINGS = ('true', 'on', 'ok', 'y', 'yes', '1')


class Knob(object):
    """
    A knob can be tuned to satisfaction. Lookup and cast environment variables to
    the required type.
    
    >>> knob = Knob('WUNDER', 'BAR', description='Foo Bar')
    >>> knob
    Knob('WUNDER', 'BAR', cast=str, description='Foo Bar')
    >>> knob.get()
    'BAR'
    >>> pirate_count = Knob('JOLLY_ROGER_PIRATES', 124, cast=int, description='Yar')
    >>> pirate_count 
    Knob('JOLLY_ROGER_PIRATES', '124', cast=int, description='Yar')
    >>> pirate_count.get()
    124
    >>> rum_flag = Knob('HAVE_RUM', True, cast=bool)
    >>> rum_flag
    Knob('HAVE_RUM', 'True', cast=bool, description='')
    >>> rum_flag.get()
    True
    """

    _register = {}

    def __init__(self, env_name, default, cast=str, description='', validator=None):
        """
        :param env_name: Name of environment variable
        :param default: Default knob setting
        :param cast: Cast value to python type
        :param description: What does this knob do
        :param validator: Callable to validate value
        """

        # force the cast to the type of the default
        if not isinstance(default, cast):
            cast = type(default)

        self.env_name = env_name
        self.default = default
        self.cast = cast
        self.description = description
        self.validator = validator

        self._register[env_name] = self

    def __repr__(self):
        return "{_class}('{env_name}', '{default}', cast={cast}, description='{desc}')".format(
            _class=self.__class__.__name__,
            env_name=self.env_name,
            default=self.default,
            cast=self.cast.__name__,
            desc=self.description
        )

    def __call__(self):
        return self.get()

    def get(self):
        source_value = os.getenv(self.env_name, self.default)

        if self.cast == bool and isinstance(source_value, str):
            val = source_value.lower() in BOOLEAN_TRUE_STRINGS

        try:
            val = self.cast(source_value)
        except ValueError as e:
            click.secho(e.message, err=True, color='red')
            sys.exit(1)

        if self.validator:
            val = self.validator(val)

        return val

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
