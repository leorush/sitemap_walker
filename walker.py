from __future__ import print_function

import requests
from bs4 import BeautifulSoup

import argparse

sitemap_url = 'https://example.com/sitemap.xml'
errors = 0
errors_log = False
auth = ''
log = []

parser = argparse.ArgumentParser()
parser.add_argument('--url', type=str,
                    help='XML sitemap url')
parser.add_argument('--auth', type=str,
                    help='Base Auth in login:password format')
parser.add_argument('--errors', action='store_true',
                    help='Write to log only errors')
args = parser.parse_args()

if args.url:
    sitemap_url = args.url
else:
    print('No sitemap URL argument passed, using default %s.' % sitemap_url)

if args.auth:
    auth = args.auth

if args.errors:
    errors_log = True

def get_urls(url):
    global errors
    global log
    links = []
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    for element in soup.findAll('loc'):
        link = element.text
        if auth != '':
            link = link.replace('://', '://' + auth + '@')
        links += [link]
        r = requests.get(link)
        res = 'Status code: '+str(r.status_code) + ' URL: ' + link + ' XML: ' + url
        result = [str(r.status_code) + ',' + link + ',' + url]
        if not errors_log:
            log += result
        if r.status_code != 200:
            print('ERROR! ' + res)
            errors += 1
            log += result
        else:
            print(res, end='\r', flush=True)
    return links


def get_all_urls(sitemap_url):
    if auth != '':
        sitemap_url = sitemap_url.replace('://', '://' + auth + '@')
    urls = get_urls(sitemap_url)

    sitemap_urls = []
    for i, url in enumerate(urls):
        links = get_urls(url)
        sitemap_urls += links

    return sitemap_urls


def main():

    sitemap_urls = get_all_urls(sitemap_url)

    with open('sitemap_urls.csv', 'w') as f:
        f.write('Code,URL,XML\n')
        for url in log:
            f.write(url + '\n')

    print('\nChecked {:,} URLs'\
            .format(len(sitemap_urls)))
    print('Errors {:,}'\
            .format(errors))

if __name__ == '__main__':
    main()

