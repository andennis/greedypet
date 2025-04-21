import pytest

from grpt_common.utils.converters import str_to_bool


@pytest.mark.parametrize("str_val, bool_val", [
    ('0', False),
    ('off', False),
    ('f', False),
    ('false', False),
    ('n', False),
    ('no', False),
    ('1', True),
    ('on', True),
    ('t', True),
    ('true', True),
    ('y', True),
    ('yes', True)
])
def test_str_to_bool(str_val: str, bool_val: bool):
    assert str_to_bool(str_val) == bool_val
