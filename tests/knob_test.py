from knobs import Knob


def test_knob():
    knob = Knob('WUNDER', 'BAR', description='Foo Bar')
    assert knob() == 'BAR'
    assert knob.get() == 'BAR'
    assert knob.description == 'Foo Bar'


def test_knob_cast_str_auto_corrected_to_int():
    knob = Knob('WUNDER', 22)
    assert knob.get() == 22


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

    k1 = Knob('K1', 'First knob')
    k2 = Knob('K2', 'Second knob')
    k1 = Knob('K3', 'Third knob')

    assert Knob.get_knob_defaults() == '#K1=First knob\n#K2=Second knob\n#K3=Third knob'
