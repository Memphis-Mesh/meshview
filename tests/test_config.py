import os
import pytest
from unittest.mock import patch
from meshview import config
from importlib import reload


@pytest.fixture
def valid_config_file(request):
    # Get the directory of the current test file
    test_dir = os.path.dirname(request.fspath)
    # Construct the path to the data file
    data_file = os.path.join(test_dir, "test_config/good.ini")
    return data_file


@pytest.fixture
def empty_config_file(request):
    # Get the directory of the current test file
    test_dir = os.path.dirname(request.fspath)
    # Construct the path to the data file
    data_file = os.path.join(test_dir, "test_config/empty.ini")
    return data_file


def test_config_file_not_found():
    with patch("sys.argv", ["script.py", "--config", "nonexistent.ini"]):
        with pytest.raises(FileNotFoundError) as exc_info:
            import meshview.config

            reload(meshview.config)
        assert "Config file 'nonexistent.ini' not found" in str(exc_info.value)


def test_empty_config_file(empty_config_file):
    with patch("sys.argv", ["script.py", "--config", empty_config_file]):
        import meshview.config

        reload(meshview.config)
        assert config.CONFIG == {}


def test_config_sections(valid_config_file):
    with patch("sys.argv", ["script.py", "--config", valid_config_file]):
        import meshview.config

        reload(meshview.config)
        assert set(config.CONFIG.keys()) == {"mqtt", "site", "server", "database"}
        assert set(config.CONFIG["database"].keys()) == {"connection_string"}
        assert set(config.CONFIG["mqtt"].keys()) == {
            "server",
            "topics",
            "port",
            "username",
            "password",
        }
