from unittest.mock import call

import pytest
import {{ cookiecutter.project_slug }}


@pytest.fixture
def patch_path():
    return "{{ cookiecutter.project_slug }}.time_helpers"


def test_timestamp_millis(mock_time):
    mock_time.time.return_value = 100
    assert {{ cookiecutter.project_slug }}.timestamp_millis() == 100 * 1_000
    assert mock_time.mock_calls == [call.time()]
