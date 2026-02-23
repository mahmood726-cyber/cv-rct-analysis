import pytest
from src.app_utils import format_rate

def test_format_rate():
    assert format_rate(0.5) == "50.0%"
    assert format_rate(1.0) == "100.0%"
    assert format_rate(0.0) == "0.0%"
    assert format_rate(0.12345) == "12.3%"
