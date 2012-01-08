"""
This file is part of the web2py Web Framework
Copyrighted by Massimo Di Pierro <mdipierro@cs.depaul.edu>
License: LGPLv3 (http://www.gnu.org/licenses/lgpl.html)
"""
import datetime
from storage import Storage
from html import TAG
import contrib.simplejson as simplejson
import contrib.rss2 as rss2


def xml_rec(value, key):
    if isinstance(value, (dict, Storage)):
        return TAG[key](*[TAG[k](xml_rec(v, '')) for k, v in value.items()])
    elif isinstance(value, list):
        return TAG[key](*[TAG.item(xml_rec(item, '')) for item in value])
    elif value == None:
        return 'None'
    elif isinstance(value,unicode):
        return value.encode('utf-8')
    else:
        return str(value)


def xml(value, encoding='UTF-8', key='document'):
    return ('<?xml version="1.0" encoding="%s"?>' % encoding) + str(xml_rec(value,key))


def json(value):
    return simplejson.dumps(value)


def csv(value):
    return ''


def rss(feed):
    if not 'entries' in feed and 'items' in feed:
        feed['entries'] = feed['items']
    now=datetime.datetime.now()
    rss = rss2.RSS2(title = feed['title'],
                    link = str(feed['link']),
                    description = feed['description'],
                    lastBuildDate = feed.get('created_on', now),
                    items = [rss2.RSSItem(\
                                        title=entry['title'],
                                        link=str(entry['link']),
                                        description=entry['description'],
                                        pubDate=entry.get('created_on', now)
                                        )\
                                    for entry in feed['entries']
                                    ]
                    )
    return rss2.dumps(rss)
