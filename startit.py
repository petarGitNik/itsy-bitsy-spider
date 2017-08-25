#!/usr/bin/python3


import re
from urllib.request import urlopen
from urllib.error import HTTPError
from urllib.error import URLError
from bs4 import BeautifulSoup
from collections import deque


__version__ = 'v0.1.0'
__status__ = 'Development'


class Startit(object):

    def __init__(self, url):
        """
        Initiate Startit object.
        """
        self.url = self.sanitize(url)
        self.page = self.retrieve_page()
        self.raw_data = deque()
        self.jobs = deque()

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
        # add try catch, HTTPError URLError
        # if anything goes wrong, send email!

    def get_premium_jobs(self):
        """
        Parse page to get all premium sponsored job ads. Append the result to
        raw_data.
        """
        return self.page.find_all('div', attrs={'class' : 'listing-oglas-premium'})

    def get_standard_jobs(self):
        """
        Parse page to get standard sponsored job ads. Append the result to
        raw_data.
        """
        return self.page.find_all('div', attrs={'class' : 'listing-oglas-standard'})

    def get_mini_jobs(self):
        """
        Parse page to extract all jobs from the mini class. Append the result to
        raw_data.
        """
        return self.page.find_all('div', attrs={'class' : 'oglas-mini'})

    def pack_by_type(self, divs, job_type):
        """
        Pack divs by type, to make them suitable for further processing. E.g.

        [list of soup objects] -> {
            'type' : StartitJobTypes.PREMIUM,
            'job-post' : <soup/div object>
        }
        """
        packed = deque()
        for div in divs:
            packed.append({
                'type' : job_type,
                'job-post' : div,
            })
        return packed


class StartitJobTypes(object):
    PREMIUM = 'premium'
    STANDARD = 'standard'
    MINI = 'mini'


class StartitException(Exception):
    """
    This exception is raised if the supplied link is not valid.
    """
    pass
