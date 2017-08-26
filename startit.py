#!/usr/bin/python3


"""
How to use Startit class?

```python
from startit import Startit
startit = Startit('https://startit.rs/poslovi/pretraga/python/')
startit.extract_divs()
startit.extract_jobs()

startit.check_and_notify()
```
"""


import os
import re
import json
import sqlite3
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from argparse import ArgumentParser
from urllib.request import Request
from urllib.request import urlopen
from urllib.error import HTTPError
from urllib.error import URLError
from bs4 import BeautifulSoup
from collections import OrderedDict
from collections import deque


__version__ = 'v0.1.0'
__status__ = 'Development'


def parse_arguments():
    """
    Example:

    startit.py https://startit.rs/poslovi/pretraga/python/ example@mail.com

    For more information type:

    crawlddit.py --help
    """
    parser = ArgumentParser(description='startit job crawler')

    parser.add_argument('URL', help='source link')
    parser.add_argument('email', help='Email receiving notifications')

    args = parser.parse_args()

    return (args.URL, args.email)


class Startit(object):
    DB_TEMPLATE = """
        DROP TABLE IF EXISTS jobs;

        CREATE TABLE jobs (
          CompanyTitle TEXT,
          JobTitle TEXT,
          Url TEXT,
          Tags BLOB,
          Active TEXT,
          FirstCrawled TEXT
         );
    """

    def __init__(self, url, email):
        """
        Initiate Startit object.
        """
        self.url = self.sanitize(url)
        self.email = email

        sensitive_data = {}
        with open('./email.config', 'r') as f:
            for line in f:
                key, val = line.split(':')
                sensitive_data[key] = val

        self.spidy_mail = sensitive_data['email']
        self.spidy_password = sensitive_data['password']

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
        return BeautifulSoup(urlopen(
            Request(
                self.url,
                data=None,
                headers={
                    'User-Agent' : 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:55.0) Gecko/20100101 Firefox/55.0'
                }
            )
        ).read(), parser)
        #return BeautifulSoup(urlopen(self.url).read(), parser)
        # add try catch, HTTPError URLError
        # if anything goes wrong, send email!

    def check_and_notify(self):
        """
        Check if there are new jobs, and notify if there are. If the spider is
        set loose for the first time, just scrape the page, and do not notify.
        """
        db_path = './db.sqlite'
        if self.db_exists(db_path):
            stale_data = self.get_existing_data(db_path)

            tup_jobs = self.turn_jobs_into_tuples()

            new_jobs = set(tup_jobs).difference(stale_data)
            expired_jobs = set(stale_data).difference(tup_jobs)

            if expired_jobs:
                self.deactivate_expired_jobs(expired_jobs)

            if new_jobs:
                self.add_new_jobs(new_jobs)
                self.notify_master_about_new_jobs(new_jobs)
            
            return

        self.execute_first_time_scarping(db_path)
        self.send_welcome_email()
        return

    def deactivate_expired_jobs(expired_jobs):
        pass

    def add_new_jobs(new_jobs):
        pass

    def notify_master_about_new_jobs(new_jobs):
        pass

    def turn_jobs_into_tuples(self):
        tup_jobs = []
        for job in self.jobs:
            job['tags'] = json.dumps(job['tags'])
            tup_jobs.append(tuple(job.values()))
        return tup_jobs

    def get_existing_data(self, path):
        """
        Return all active jobs from the database.
        """
        conn = sqlite3.connect(path)
        c = conn.cursor()

        c.execute('SELECT CompanyTitle, JobTitle, Url, Tags FROM jobs WHERE Active=1')
        rows = c.fetchall()

        conn.close()
        return rows

    def execute_first_time_scarping(self, path):
        """
        Execute this method when the bot is scraping for the first time. Create
        database and populate it with new jobs.
        """
        conn = sqlite3.connect(path)
        c = conn.cursor()
        c.executescript(self.DB_TEMPLATE)

        for job in self.jobs:
            self.write_a_record_to_db(c, job, True)

        conn.commit()
        conn.close()
        return

    def send_welcome_email(self):
        """
        When the script is executed for the first time, send greeting email.
        """
        from_address = self.spidy_mail
        password = self.spidy_password
        to_address = self.email

        msg = MIMEMultipart()
        msg['From'] = from_address
        msg['To'] = to_address
        msg['Subject'] = "Greetings, it's your itsy bitsy spider /\(00)/\\"

        body = """
        The itsy bitsy spider climbed up the waterspout.
        Down came the rain
        and washed the spider out.
        Out came the sun
        and dried up all the rain
        and the itsy bitsy spider climbed up the spout again.
        """
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_address, password)
        text = msg.as_string()
        server.sendmail(from_address, to_address, text)
        server.quit()

    def write_a_record_to_db(self, cursor, job, active):
        """
        Write a single record to database.
        """
        to_write = (
            job['company-title'],
            job['job-title'],
            job['url'],
            json.dumps(job['tags']),
            active,
            str(datetime.now()),
        )
        cursor.execute('INSERT INTO jobs VALUES(?,?,?,?,?,?)', to_write)
        return

    def db_exists(self, path):
        """
        Check if database exists on a given path.
        """
        return os.path.exists(path)

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

        title = text.div.a.string
        company_title = title.strip() if title else text.div.a.span.text.strip()
        tags = self.extract_tags(text.find_all('small'))

        d = OrderedDict()
        d['company-title'] = company_title
        d['job-title'] = job_title
        d['url'] = url
        d['tags'] = tags

        return d

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

        d = OrderedDict()
        d['company-title'] = company_title
        d['job-title'] = job_title
        d['url'] = url
        d['tags'] = tags

        return d

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

        d = OrderedDict()
        d['company-title'] = company_title
        d['job-title'] = job_title
        d['url'] = url
        d['tags'] = tags

        return d

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


if __name__ == '__main__':
    url, email = parse_arguments()

    startit = Startit(url, email)

    startit.extract_divs()
    startit.extract_jobs()

    startit.check_and_notify()
