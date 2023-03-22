import os
from unittest.mock import Mock, call, sentinel

import pytest
from {{ cookiecutter.project_slug }} import config


@pytest.fixture
def patch_path():
    return "{{ cookiecutter.project_slug }}.config"


@pytest.fixture
def local_file():
    os.system("""echo 'a: 1' > /tmp/test_config.yaml""")
    yield "/tmp/test_config.yaml"
    os.system("rm /tmp/test_config.yaml")


def test_read_config_no_file():
    assert (
        config.Config.read(
            name="nonexistent_file",
        )
        == {}
    )


def test_read_config_local_file(local_file):
    assert (
        config.Config.read(
            name=local_file,
        )
        == {"a": 1}
    )
