#!/usr/bin/python3


"""
How to use Startit class?

```python
from startit import Startit
startit = Startit('https://startit.rs/poslovi/pretraga/python/')
startit.extract_divs()
startit.extract_jobs()
```
"""


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

    def extract_jobs(self):
        """
        Using the raw_data, extract jobs as deque collection of  dictionary
        objects, where a job dictionary is in the following form:

        {
            'company-title' : company_title,
            'job-title' : job_title,
            'url' : url,
            'tags' : tags,
        }
        """
        for job in self.raw_data:
            if job['type'] == StartitJobTypes.PREMIUM:
                self.jobs.append(self.extract_from_premium(job['job-post']))
            elif job['type'] == StartitJobTypes.STANDARD:
                self.jobs.append(self.extract_from_standard(job['job-post']))
            elif job['type'] == StartitJobTypes.MINI:
                self.jobs.append(self.extract_from_mini(job['job-post']))
            else:
                raise StartitException('Unknown job type!')
        return

    def extract_from_premium(self, premium):
        """
        Extract content from premium job ad.
        """
        text = premium.find('div', attrs={'class' : 'listing-oglas-premium-text'})

        url = text.h1.a['href']
        job_title = text.h1.a.string.strip()
        company_title = text.div.a.string.strip()
        tags = self.extract_tags(text.find_all('small'))

        return {
            'company-title' : company_title,
            'job-title' : job_title,
            'url' : url,
            'tags' : tags,
        }

    def extract_from_standard(self, standard):
        """
        Extract content from standard job ad.
        """
        text = standard.find('div', attrs={'class' : 'listing-oglas-standard-text'})

        url = text.h1.a['href']
        job_title = text.h1.a.string.strip()

        title = text.div.a.string
        company_title = title.strip() if title else text.div.a.span.text.strip()
        tags = self.extract_tags(text.find_all('small'))

        return {
            'company-title' : company_title,
            'job-title' : job_title,
            'url' : url,
            'tags' : tags,
        }

    def extract_from_mini(self, mini):
        """
        Extract content from mini job ad.
        """
        url = mini.h1.a['href']
        job_title = mini.h1.a.string.strip()
        company_title = mini.div.string.strip()
        tags = self.extract_tags(
            mini.find('div', attrs={'class' : 'oglas-mini-tagovi'}).find_all('small')
        )

        return {
            'company-title' : company_title,
            'job-title' : job_title,
            'url' : url,
            'tags' : tags,
        }

    def extract_tags(self, smalls):
        """
        Extract tags from job ads. Tags are located between <small> html tag.
        """
        tags = []
        for small in smalls:
            tags.append(small.a.string.strip())
        return tags

    def extract_divs(self):
        """
        Extract all job related divs. These divs come in three 'flavours':
        premium, standard, and mini. Each of those object is labled correspondingly
        using constants from the StartitJobTypes class.
        """
        premium = self.get_premium_jobs()
        if premium:
            self.raw_data.extend(
                self.pack_by_type(
                    premium, StartitJobTypes.PREMIUM
                )
            )

        standard = self.get_standard_jobs()
        if standard:
            self.raw_data.extend(
                self.pack_by_type(
                    standard, StartitJobTypes.STANDARD
                )
            )

        mini = self.get_mini_jobs()
        if mini:
            self.raw_data.extend(
                self.pack_by_type(
                    mini, StartitJobTypes.MINI
                )
            )

        return

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
