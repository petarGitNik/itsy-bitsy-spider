#!/usr/bin/python3


import re
from urllib.request import urlopen
from urllib.error import HTTPError
from urllib.error import URLError
from bs4 import BeautifulSoup


__version__ = 'v0.1.0'
_status__ = 'Development'


class Startit(object):

    def __init__(self, url):
        """
        Initiate Startit object.
        """
        self.url = self.sanitize(url)
        self.page = self.retrieve_page()

    def sanitize(self, url):
        """
        Check if the supplied link is valid. If not raise an exception.
        Valid link must be of the following form:

        https://startit.rs/poslovi/pretraga/[category]/
        """
        pattern = 'https:\/\/startit\.rs\/poslovi\/pretraga\/.+?\/'
        match_candidate = re.match(pattern, url)
        candidate = match_candidate.group(0) if match_candidate else ''
        if len(url) == len(candidate):
            return url
        raise StartitException('Invalid link.')

    def retrieve_page(self, parser='lxml'):
        """
        Retrieve page with job listing.
        """
        return BeautifulSoup(urlopen(self.url).read(), parser)


class StartitException(Exception):
    """
    This exception is raised if the supplied link is not valid.
    """
    pass
