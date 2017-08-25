#!/usr/bin/python3


import pytest

import pickle
from urllib.request import addinfourl
from urllib.request import build_opener
from urllib.request import install_opener
from urllib.request import HTTPSHandler
from io import StringIO
from bs4 import BeautifulSoup
from collections import deque

from startit import Startit
from startit import StartitJobTypes
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

def test_pack_by_type(jobs):
    """
    Test the pack_by_type method.
    """
    soup = BeautifulSoup(read_mock_page(), 'lxml')
    premium = soup.find_all('div', attrs={'class' : 'listing-oglas-premium'})
    result = deque([{
        'type' : StartitJobTypes.PREMIUM,
        'job-post' : premium[0]
    }, {
        'type' : StartitJobTypes.PREMIUM,
        'job-post' : premium[1]
    }])
    assert jobs.pack_by_type(premium, StartitJobTypes.PREMIUM) == result

def test_premium_jobs(jobs):
    """
    Test the get_premium_jobs method.
    """
    soup = BeautifulSoup(read_mock_page(), 'lxml')
    premium = soup.find_all('div', attrs={'class' : 'listing-oglas-premium'})
    assert jobs.get_premium_jobs() == premium

def test_standard_jobs(jobs):
    """
    Test the get_standard_jobs method.
    """
    soup = BeautifulSoup(read_mock_page(), 'lxml')
    standard = soup.find_all('div', attrs={'class' : 'listing-oglas-standard'})
    assert jobs.get_standard_jobs() == standard

def test_mini_jobs(jobs):
    """
    Test the get_mini_jobs method.
    """
    soup = BeautifulSoup(read_mock_page(), 'lxml')
    mini = soup.find_all('div', attrs={'class' : 'oglas-mini'})
    assert jobs.get_mini_jobs() == mini

def test_extract_divs(jobs):
    """
    Test extract_divs method.
    """
    raw_data = pickle.load(open('pickled_raw_data.p', 'rb'))
    jobs.extract_divs()
    assert jobs.raw_data == raw_data

def test_extract_from_premium(jobs):
    """
    Test extract_from_premium method.
    """
    soup = BeautifulSoup(read_mock_page(), 'lxml')
    premium = soup.find_all('div', attrs={'class' : 'listing-oglas-premium'})
    result = {
        'company-title' : 'Joker Games',
        'job-title' : 'C# .NET Developer',
        'url' : 'https://startit.rs/poslovi/c-net-developer-meridianbet/',
        'tags' : ['.net', 'chrarp', 'node.js', 'python'],
    }
    assert jobs.extract_from_premium(premium[0]) == result
