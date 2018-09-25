import os
import sys
import json

import click
import tabulate

from environment import find_dotenv, load_dotenv

load_dotenv(find_dotenv(usecwd=True))

BOOLEAN_TRUE_STRINGS = ('true', 'on', 'ok', 'y', 'yes', '1')


class Knob:
    """
    A knob can be tuned to satisfaction. Lookup and _cast environment variables to
    the required type.
    >>> knob = Knob('WUNDER', 'BAR', description='Foo Bar')
    >>> knob
    Knob('WUNDER', 'BAR', unit='', description='Foo Bar', validator=None)
    >>> knob.get()
    'BAR'
    >>> pirate_count = Knob('PIRATE_COUNT', 124, description='Yar')
    >>> pirate_count
    Knob('PIRATE_COUNT', 124, unit='', description='Yar', validator=None)
    >>> pirate_count.get()
    124
    >>> pirate_count.get_type()
    <type 'int'>
    >>> rum_flag = Knob('HAVE_RUM', True)
    >>> rum_flag
    Knob('HAVE_RUM', True, unit='', description='', validator=None)
    >>> rum_flag.get()
    True
    """

    _register = {}

    def __init__(
        self,
        env_name: str,
        default,
        unit: str = '',
        description: str = '',
        validator=None,
    ):
        """
        :param env_name: Name of environment variable
        :param default: Default knob setting
        :param unit: Unit description
        :param description: What does this knob do
        :param validator: Callable to validate value
        """

        # the default's type sets the python type of the value
        # retrieved from the environment
        self._cast = type(default)

        self.env_name = env_name
        self.default = default
        self.unit = unit
        self.description = description
        self.validator = validator

        self._register[env_name] = self

    def __call__(self):
        return self.get()

    def get_type(self):
        """ The type of this knob """
        return self._cast

    def help(self):
        """
        :return: Description string with default appended
        """
        return f'{self.description}, Default: {self.get()}{self.unit}'

    def rm(self):
        """
        Remove environment variable
        :return:
        """
        del os.environ[self.env_name]

    def set(self, value):
        """
        set the environment variable
        This is useful when the default gets mutated by the cli
        """
        os.environ[self.env_name] = str(value)

    def get(self):
        source_value = os.getenv(self.env_name)
        # set the environment if it is not set
        if source_value is None:
            os.environ[self.env_name] = str(self.default)
            return self.default

        # bool
        if self._cast == bool:
            if isinstance(source_value, str):
                return source_value.lower() in BOOLEAN_TRUE_STRINGS
            if isinstance(source_value, bool):
                return source_value

        # list
        if self._cast == list:
            return source_value.split()

        # tuple
        if self._cast == tuple:
            return tuple(source_value.split())

        try:
            val = self._cast(source_value)
        except ValueError as e:
            click.secho(e.message, err=True, color='red')
            sys.exit(1)

        if self.validator:
            val = self.validator(val)

        return val

    def __repr__(self):
        _class = self.__class__.__name__
        env_name = self.env_name
        default = repr(self.default)
        unit = repr(self.unit)
        desc = self.description
        validator = repr(self.validator)
        return f"{_class}('{env_name}', {default}, unit={unit}, description='{desc}', validator={validator})"

    @classmethod
    def get_registered_knob(cls, name):
        return cls._register.get(name, None)

    @classmethod
    def clear_registry(cls):
        """ Clear knob registry """
        cls._register = {}

    @classmethod
    def print_knobs_table(cls, ctx, param, value):
        if not value or ctx.resilient_parsing:
            return
        click.echo(cls.get_knob_defaults_as_table())
        ctx.exit()

    @classmethod
    def get_knob_defaults_as_table(cls):
        """
        Renders knobs in table
        :return:
        """

        knob_list = [
            {
                'Knob': name,
                'Description': cls.get_registered_knob(name).description,
                'Default': cls.get_registered_knob(name).default
            } for name in sorted(cls._register.keys())
        ]
        return tabulate.tabulate(knob_list, headers='keys', tablefmt='fancy_grid')

    @classmethod
    def print_knobs_env(cls, ctx, param, value):
        if not value or ctx.resilient_parsing:
            return
        click.echo(cls.get_knob_defaults())
        ctx.exit()

    @classmethod
    def get_knob_defaults(cls):
        """ Returns a string with defaults
        >>> Knob.get_knob_defaults()
        '# \n# HAVE_RUM=True\n\n# Yar\n# JOLLY_ROGER_PIRATES=124\n\n# Foo Bar\n# WUNDER=BAR\n'
        """

        return '\n'.join(
            [
                '# {description}\n# {knob}={default}\n'.format(
                    description=cls.get_registered_knob(name).description,
                    knob=name,
                    default=cls.get_registered_knob(name).default
                ) for name in sorted(cls._register.keys())
            ]
        )


class ListKnob(Knob):
    """
    A specialised Knob that expects its value to be a json list environment variable like:
    ENV_LIST_EXAMPLE='["Foo", "bar"]'
    """

    def __init__(
        self,
        env_name: str,
        default,
        unit: str = '',
        description: str = '',
        validator=None,
    ):
        """
        :param env_name: Name of environment variable
        :param default: Default knob setting
        :param unit: Unit description
        :param description: What does this knob do
        :param validator: Callable to validate value
        """

        # the default's type sets the python type of the value
        # retrieved from the environment
        self._cast = type([])

        super().__init__(env_name, default, unit, description, validator)

    def get(self):
        """
        convert json env variable if set to list
        """
        source_value = os.getenv(self.env_name)
        # set the environment if it is not set
        if source_value is None:
            os.environ[self.env_name] = str(self.default)
            return self.default

        try:
            val = json.loads(source_value)
        except ValueError as e:
            click.secho(e.message, err=True, color='red')
            sys.exit(1)

        if self.validator:
            val = self.validator(val)

        return val
