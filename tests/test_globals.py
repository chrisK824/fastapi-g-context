import pytest
from fastapi_g_context import g


@pytest.fixture(autouse=True)
def clear_globals():
    """Ensure the Globals instance is cleared before each test."""
    g.clear()


def test_set_and_get_attribute():
    g.username = "JohnDoe"
    assert g.username == "JohnDoe"


def test_get_non_existing_attribute():
    with pytest.raises(AttributeError):
        _ = g.non_existing


def test_get_with_default():
    assert g.get("non_existing", "default_value") == "default_value"
    assert g.get("non_existing") is None


def test_pop_existing_attribute():
    g.to_pop = "value"
    assert g.pop("to_pop") == "value"
    assert "to_pop" not in g


def test_pop_non_existing_with_default():
    assert g.pop("non_existing", "default_value") == "default_value"


def test_pop_non_existing_without_default():
    assert g.pop("non_existing") is None


def test_contains():
    g.is_admin = True
    assert "is_admin" in g
    assert "non_existing" not in g


def test_keys():
    g.key1 = "value1"
    g.key2 = "value2"
    assert set(g.keys()) == {"key1", "key2"}


def test_values():
    g.key1 = "value1"
    g.key2 = "value2"
    assert set(g.values()) == {"value1", "value2"}


def test_items():
    g.key1 = "value1"
    g.key2 = "value2"
    assert dict(g.items()) == {"key1": "value1", "key2": "value2"}


def test_to_dict():
    g.key1 = "value1"
    g.key2 = "value2"
    assert g.to_dict() == {"key1": "value1", "key2": "value2"}
