from sitemon import __version__
import sitemon.sitemon as SM


def test_version():
    assert __version__ == '0.1.0'

def test_is_it_file():
    pass
    # SM.is_it_file