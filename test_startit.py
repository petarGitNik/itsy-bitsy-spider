#!/usr/bin/python3


import pytest

from urllib.request import addinfourl
from urllib.request import build_opener
from urllib.request import install_opener
from urllib.request import HTTPHandler

from startit import Startit
from startit import StartitException


__version__ = 'v0.1.0'
_status__ = 'Development'


# Setup mock for urllib.request.urlopen
def read_mock_page():
    with open('example_page_python.html', 'r', encoding='utf-8') as f:
        return f.read()

def mock_startit_response(request):
    mock_url = 'https://startit.rs/poslovi/pretraga/python/'
    if request.get_full_url() == mock_url:
        # addinfourl: https://archive.is/LpjxV
        response = addinfourl(
            read_mock_page(), 'mock header', request.get_full_url()
        )
        response.code = 200
        return response


class MockHttpHandler(HTTPHandler):

    def http_open(self, request):
        return mock_startit_response(request)


mock_opener = build_opener(MockHttpHandler)
install_opener(mock_opener)

# Tests

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
