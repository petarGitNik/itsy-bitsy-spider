#!/usr/bin/python3


import pytest

from urllib.request import addinfourl
from urllib.request import build_opener
from urllib.request import install_opener
from urllib.request import HTTPSHandler
from io import StringIO
from bs4 import BeautifulSoup

from startit import Startit
from startit import StartitException


__version__ = 'v0.1.0'
__status__ = 'Development'


# Setup mock for urllib.request.urlopen
def read_mock_page():
    with open('example_page_python.html', 'r', encoding='utf-8') as f:
        return StringIO(f.read())

def mock_startit_response(request):
    mock_url = 'https://startit.rs/poslovi/pretraga/python/'
    if request.get_full_url() == mock_url:
        # addinfourl: https://archive.is/LpjxV
        response = addinfourl(
            read_mock_page(), 'mock header', request.get_full_url()
        )
        response.code = 200
        response.msg = 'OK'
        return response


class MockHttpHandler(HTTPSHandler):

    def https_open(self, request):
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

def test_page_retrieval(jobs):
    """
    Test the retrieve_page method.
    """
    soup = BeautifulSoup(read_mock_page(), 'lxml')
    assert jobs.retrieve_page() == soup

def test_page_retrieved(jobs):
    """
    Test if the page object in instantiated together with Startit object.
    """
    soup = BeautifulSoup(read_mock_page(), 'lxml')
    assert jobs.page == soup

@pytest.mark.skip(reason='too soon')
def test_premium_jobs(jobs):
    """
    Test the get_premium_jobs method.
    """
    soup = BeautifulSoup(read_mock_page(), 'lxml')
    premium = soup.find_all('div', attrs={'class' : 'listing-oglas-premium'})
    assert 1 == 1
