import os

from knobs import Knob


def test_repr():
    pirate_count = Knob('JOLLY_ROGER_PIRATES', 124, description='Yar')
    assert repr(pirate_count) == "Knob('JOLLY_ROGER_PIRATES', 124, unit='', description='Yar', validator=None)"


def test_serialize():
    knob = Knob('WUNDER', 'BAR', description='Foo Bar')
    assert repr(knob) == "Knob('WUNDER', 'BAR', unit='', description='Foo Bar', validator=None)"


def test_knob():
    knob = Knob('WUNDER', 'BAR', description='Foo Bar')
    assert knob() == 'BAR'
    assert knob.get() == 'BAR'
    assert knob.description == 'Foo Bar'
    knob.rm()


def test_knob_cast_str_auto_corrected_to_int():
    knob = Knob('WUNDER', 22)
    assert knob.get() == 22


def test_tuple():
    knob = Knob('LIST', ('LOVE', 'THEY', 'NEIGHBOUR'))
    assert knob() == ('LOVE', 'THEY', 'NEIGHBOUR')


def test_list_from_env():
    os.environ['LIST'] = 'DEAD BEEF COFFEE'
    assert type(os.environ['LIST']) == str
    knob = Knob('LIST', ['LOVE', 'THEY', 'NEIGHBOUR'])
    assert knob.get_type() == list
    assert knob() == ['DEAD', 'BEEF', 'COFFEE']


def test_typle_from_env():
    os.environ['TUPLE'] = 'DEAD BEEF COFFEE'
    assert type(os.environ['TUPLE']) == str
    knob = Knob('LIST', ('LOVE', 'THEY', 'NEIGHBOUR'))
    assert knob.get_type() == tuple
    assert knob() == ('DEAD', 'BEEF', 'COFFEE')


def test_cast_to_int():
    pirate_count = Knob('JOLLY_ROGER_PIRATES', 124, description='Yar')
    assert pirate_count.get() == 124
    assert pirate_count.description == 'Yar'


def test_cast_to_string():
    rope = Knob('ROPE_TO_HANG_BY', 'A stiff rope for yer nek, mate')
    assert rope.get_type() == str


def test_registry():
    Knob.clear_registry()
    assert Knob.get_knob_defaults() == ''

    k1 = Knob('K1', 'First knob', description='Omi')
    k2 = Knob('K2', 'Second knob', description='Padre')
    k1 = Knob('K3', 'Third knob', description='Magnifici')

    print(Knob.get_knob_defaults())
    print(repr(Knob.get_knob_defaults()))

    envout = '# Omi\n# K1=First knob\n\n# Padre\n# K2=Second knob\n\n# Magnifici\n# K3=Third knob\n'
    assert Knob.get_knob_defaults() == envout


def test_set():
    setknob = Knob('KNOB_NAME', 'KNOB_VAL')
    assert setknob.get_type() == str
    assert setknob.get() == 'KNOB_VAL'

    setknob.set('XX123')
    assert setknob.get() == 'XX123'
