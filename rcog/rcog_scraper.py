#!/usr/bin/env python


import os, sys
import json

import lxml.html
import lxml.etree
import urllib2
import urlparse
import requests
import re

base = 'https://www.rcog.org.uk'

def scrape_pdf(source):
    html = requests.get(source).content
    page = lxml.html.fromstring(html)

    raw_title = page.cssselect('h1')[0].text_content()
    title = raw_title[0:raw_title.index('(')]

    try:
        link = page.cssselect('#Content_Content_hypDocLink')[0]
    except:
        # No link is archived
        return None

    url = urlparse.urljoin(base, link.get('href'))

    start = raw_title.index('(')+1
    length = (raw_title.index(')')+1) - start
    code = raw_title[start:start + length]

    block = page.cssselect('.col-md-8')[0].text_content()
    m = re.search('.*?(\d+/\d+/\d+).*', block)
    date = ''

    if m:
        date = m.groups()[0]
    data = {
            'code': code,
            'title': title.strip().decode('utf-8'),
            'date': date.strip(),
            'description': '',
            'url': url,
            'category': ''
    }

    return data


def scrape_page(source):
    html = requests.get(source).content
    page = lxml.html.fromstring(html)
    table = page.cssselect( 'table.results tr')
    if not len(table):
        return

    for row in table:
        link = row[0].cssselect('.title a')
        pdf_source = urlparse.urljoin(base, link[0].get('href'))
        yield scrape_pdf(pdf_source)


out = {'categories': [], 'guidelines': []}

for x in range(1, 7):  # Yeah, yeah, hard-coded page count
    source = "https://www.rcog.org.uk/guidelines?filter0[]=10&p=%s" % x
    for result in scrape_page(source):
        if result:
            out['guidelines'].append(result)

json.dump(out, sys.stdout)
