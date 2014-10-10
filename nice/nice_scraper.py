#!/usr/bin/env python
import copy
import collections
import re
import copy
import requests
import time
import json
import sys
from lxml.html import fromstring
from urlparse import urljoin
from picklecache import cache
import pickle_warehouse.serializers

title_rx = re.compile('(.*)\((.*)\)')

content = collections.defaultdict(list)


@cache('~/.http')
def get(url):
    return requests.get(url).content

def process_page(href, data):
    html = get(href)
    page = fromstring(html)
    try:
        href = page.cssselect('.track-event')[0]
    except:
        return

    link = urljoin('http://www.nice.org.uk', href.get('href'))

    crumbs = page.cssselect('#guidance-breadcrumb li')
    cat = crumbs[-2].text_content().strip()

    data['url'] = link.encode('utf-8')
    data['category'] = cat.decode('latin1').encode('utf-8')
    content[cat].append(data)

def process():
    html = get("http://www.nice.org.uk/guidance/published?type=Guidelines")
    page = fromstring(html)
    rows = page.cssselect(".rowlink tr")
    for row in rows:
        title = row[0][0].text_content().encode('utf-8')
        title, code = title_rx.match(title).groups()
        if not code.strip().startswith('CG'):
            continue

        href = urljoin('http://www.nice.org.uk', row[0][0].get('href'))
        date = row[1].text_content()
        data = {
            'code': code.strip(),
            'title': title.strip().decode('utf-8'),
            'date': date.strip(),
            'description': ''
        }
        process_page(href, data)

process()

out = {
    'categories': [],
    'guidelines': []
}


for key in content.keys():
    if not key in out['categories']:
        out['categories'].append(key)

    for g in content[key]:
        out['guidelines'].append(copy.deepcopy(g))


out['categories'] = sorted(out['categories'])

json.dump(out, sys.stdout)