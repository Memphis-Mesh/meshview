import os
import pytest
from unittest.mock import patch
import tempfile
from meshview import config
from importlib import reload
from importlib import reload
from importlib import reload
from importlib import reload


@pytest.fixture
def valid_config_file():
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        f.write("""
[database]
connection_string = teststring

[api]
key = secret123
timeout = 30
""")
        temp_path = f.name
    yield temp_path
    os.unlink(temp_path)


@pytest.fixture
def empty_config_file():
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        temp_path = f.name
    yield temp_path
    os.unlink(temp_path)


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
        assert set(config.CONFIG.keys()) == {"database", "api"}
        assert set(config.CONFIG["database"].keys()) == {"connection_string"}
        assert set(config.CONFIG["api"].keys()) == {"key", "timeout"}
