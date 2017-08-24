#!/usr/bin/python3


import pytest
from startit import Startit
from startit import StartitException


__version__ = 'v0.1.0'
_status__ = 'Development'


@pytest.fixture
def jobs():
    return Startit('https://startit.rs/poslovi/pretraga/python/')

def test_invalid_link_1():
    """
    Test if the invalid link raises an exception. What constitutes a
    valid link? The link of the following format is valid:

    https://startit.rs/poslovi/pretraga/[category]/

    Every other form is not valid.
    """
    with pytest.raises(StartitException):
        Startit('https://startit.rs/poslovi/pretraga/python/qa/')

def test_invalid_link_2():
    """
    Test if the invalid link raises an exception. What constitutes a
    valid link? The link of the following format is valid:

    https://startit.rs/poslovi/pretraga/[category]/

    Every other form is not valid.
    """
    with pytest.raises(StartitException):
        Startit('https://startit.rs/poslovi/pretraga/')

def test_valid_link():
    """
    Test if valid link does not raise an exception.
    """
    try:
        Startit('https://startit.rs/poslovi/pretraga/python/')
    except StartitException:
        pytest.fail('Exception raised, but not expceted.')
