#!/usr/bin/env python
"""A plugin for displaying recent uploads filtered in various ways.

Usage: ia recent --minutes-back=N [--help]

Options:
  -h, --help                Show this help message and exit.

Examples:
    $ ia recent
    Output?
"""
from __future__ import print_function
import sys
import datetime

from docopt import docopt


__title__ = __name__
__version__ = '0.0.1'
__url__ = 'https://github.com/JesseWeinstein/ia_recent'
__author__ = 'Jesse Weinstein'
__email__ = 'jesse@wefu.org'
__license__ = 'AGPL 3'
__copyright__ = 'Copyright 2016 Jesse Weinstein'
__all__ = [__title__]


def log(fmt, *args):
    print(datetime.datetime.now().isoformat() + '| ' + fmt.format(*args), file=sys.stderr)


def uploaders_by_upload_counts(session, query, max_count=None,
                               fields_to_include=('identifier',)):
    """List of uploaders, sorted by how many items they have uploaded.

Optionally include metadata fields from the item(s) found in the query.

Useful for identifying spam.
"""
    s = session.search_items(query, ['identifier'])
    log('{} items found by initial query: {}', len(s), query)
    uploaders = {}
    for i in s.iter_as_items():
        u = i.metadata.get('uploader')
        if u:
            x = uploaders.setdefault(u, [])
            if fields_to_include:
                x.append({f: i.metadata.get(f) for f in fields_to_include})
        else:
            log('No uploader found: {}', i.identifier)
    log('{} different uploaders seen', len(uploaders))
    ans = []
    for (k, v) in uploaders.items():
        count = len(session.search_items('uploader:"{}"'.format(k),
                                         params={'rows': 0}))
        if max_count is None or count < max_count:
            if fields_to_include:
                ans.append((count, k, v))
            else:
                ans.append((count, k))
    if max_count:
        log('{} uploaders with less than {} uploads', len(ans), max_count)
    else:
        log('Finished getting upload counts')
    ans.sort()
    return ans

F = ('identifier', 'title', 'description')


def recent_uploads_by_uploader_count(session, minutes_back, max_count=100,
                                     fields_to_include=F):
    now = datetime.datetime.now()
    query = 'addeddate:[{:%Y-%m-%dT%H:%M:%SZ} TO {:%Y-%m-%dT%H:%M:%SZ}]'.format(
        now-datetime.timedelta(minutes=minutes_back), now)
    return uploaders_by_upload_counts(session, query, max_count, fields_to_include)


def stringify_output(ans, desc_max_len=30):
    return u'\n'.join(u'{0}: {1}\n\t'.format(*x[:2]) + (u'\n\t'.join(
        y[u'identifier'] + ': ' + y[u'description'][:desc_max_len]
        for y in x[2] if y) if x[2] else '') for x in ans if x)


# `argv` is a list of args passed in from `ia`, and `session` is an
# `interenetarchive.ArchiveSession` object.
def main(argv=None, session=None):
    if session is None:
        import internetarchive.api
        session = internetarchive.api.get_session()
    # Parse the list of args passed in from `ia`.
    args = docopt(__doc__, argv=argv)

    ans = recent_uploads_by_uploader_count(session, int(args['--minutes-back']))
    print(stringify_output(ans))

if __name__ == '__main__':
    main()
