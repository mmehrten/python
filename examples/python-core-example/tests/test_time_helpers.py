from unittest.mock import call

import pytest
import python_core_example


@pytest.fixture
def patch_path():
    return "python_core_example.time_helpers"


def test_timestamp_millis(mock_time):
    mock_time.time.return_value = 100
    assert python_core_example.timestamp_millis() == 100 * 1_000
    assert mock_time.mock_calls == [call.time()]
