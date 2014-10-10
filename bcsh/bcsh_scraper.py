#!/usr/bin/env python

import urlparse
import lxml.html
import datetime
import requests
import sys
import json

base = 'http://www.bcshguidelines.com/4_HAEMATOLOGY_GUIDELINES.html?dtype=All&dpage=0&dstatus=All&dsdorder=&dstorder=&dmax=9999&dsearch=&sspage=0&ipage=0#gl'

out = {'categories':[], 'guidelines': []}

html = requests.get(base).content.decode('utf-8', 'ignore')
page = lxml.html.fromstring( unicode(html) )
rows = page.cssselect('tr.topics')
for row in rows:
    title = row[0].text_content().strip()
    span = row[1].cssselect('.glTitle')[0]
    dt = row[2].text_content()
    a = row[3].cssselect('a')
    if not a:
        continue

    pdf = a[0].attrib.get('href')
    pdf = urlparse.urljoin(base, pdf)

    desc = row[1].cssselect('.glinfo')
    desc = desc[0].text_content() if desc else ''

    cat = row[0].get('class').split(' ')[-1]
    cat = cat.replace('_', ' ')
    if not cat in out['categories']:
        out['categories'].append(cat)

    # title, pdf, dt
    out['guidelines'].append({
            'code': '',
            'title': title.strip().decode('utf-8'),
            'date': dt,
            'description': desc,
            'url': pdf,
            'category': cat
    })

out['categories'] = sorted(out['categories'])

json.dump(out, sys.stdout)