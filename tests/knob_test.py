from knobs import Knob


def test_knob():
    knob = Knob('WUNDER', 'BAR', description='Foo Bar')
    assert knob() == 'BAR'
    assert knob.get() == 'BAR'
    assert knob.description == 'Foo Bar'


def test_knob_cast_str_auto_corrected_to_int():
    knob = Knob('WUNDER', 22, cast=str)
    assert knob.get() == 22


def test_cast_to_int():
    pirate_count = Knob('JOLLY_ROGER_PIRATES', 124, cast=int, description='Yar')
    assert pirate_count.get() == 124
