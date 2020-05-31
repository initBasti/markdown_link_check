"""
    Author: Sebastian Fricke
    License: GPLv3
    Date: 31.05.2020

    Check a list of files or scan all the files of the current directory +
    sub-directories. Search for the pattern provided by the CLI option
    or search all links. Perform basic URL-string sanity check and get
    the status code.
    Print a list of invalid URLs to stdout or file.
"""
import sys
import os
import time
from urllib.parse import urlparse
import re
import argparse
import requests

def progressbar(input_range, prefix="", size=60, file=sys.stdout):
    """
        Parameter:
            input_range [Range object] : generator for the amount of objects
            prefix [String] : Name of the bar
            size [Integer] : Length of the bar
            file [File/Stream] : Output destination
    """
    count = len(input_range)
    def show(index):
        x = int(size*index/count)
        file.write("%s[%s%s] %i/%i\r" % (prefix, "#"*x, "."*(size-x),
                                         index, count))
        file.flush()
    show(0)
    for index, item in enumerate(input_range):
        yield item
        show(index+1)
    file.write("\n")
    file.flush()

def validate_url(url):
    """
        Basic check to determine if the URL is valid.
        Only test if the URL contains required elements.

        Parameter:
            url [String]

        Return:
            True/False
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc, result.path])
    except Exception:
        return False

def check_status(url, verbose):
    """
        Get the status code of the URL.

        Parameter:
            url [String]
            verbose [Bool] : If true extra output to stdout

        Return:
            [Integer] A HTTP Status code, 400 on a failed request
    """
    if verbose:
        print(f"URL:\n{url}")
    try:
        head = requests.head(url)
    except Exception as err:
        print(f"ERROR: {url}\n{err}")
        return 400

    return head.status_code

def search_links(pattern):
    """
        Gather all files ending with '.md' and scan them for the given pattern.

        Parameter:
            pattern [String] : Search pattern

        Return:
            [list] : List of links
    """
    cwd = os.getcwd()
    links = []

    for root, dirs, files in os.walk(cwd, topdown=False):
        for name in files:
            if re.search(r'\.md', name):
                all_matches = search_pattern(pattern=pattern,
                                             path=os.path.join(root, name))
                if all_matches:
                    for link in all_matches:
                        links.append(link)
    l = [clean_link(x) for x in links if x]
    used = set()
    return [x for x in l if x not in used and (used.add(x) or True)]

def search_pattern(pattern, path):
    """
        Generate a list of matches to the pattern in a given file.

        Parameter:
            pattern [String] : URL search pattern for all links or restricted
                               to links starting with user option 'pattern'
            path [String] : file path to the file to scan

        Return:
            [list] : list of matches
    """
    with open(path, mode='r') as item:
        itemtext = item.read()
    return re.findall(pattern, itemtext)

def clean_link(link):
    """
        Remove all unnecessary symbols from the string.

        Parameter:
            link [String] : URL

        Return:
            link [Sring]
    """
    try:
        link = re.sub(r'[\(|\)|\s|,]', '', link)
        return link
    except TypeError as err:
        print(f"ERROR processing {link}\n{err}")
        return ''

def main():
    links = dict()
    columns = ['url', 'valid_url', 'status_code']
    i = 0
    pattern = ''

    parser = argparse.ArgumentParser(
        description='test if the links point to existing sites.')
    parser.add_argument('--pattern', dest='pattern',
                        help='Search for a specific pattern ')
    parser.add_argument('--file', dest='input_file',
                        help='Search only for links specified in the file')
    parser.add_argument('--output-file', dest='output_file',
                        help='Write invalid links into the specified file')
    parser.add_argument('-v', dest='verbose',
                        action='store_true',
                        help='Print information to stdout')
    args = parser.parse_args()

    if not args.pattern and not args.input_file:
        pattern = r'\(https:\/\/\S*\)'

    if pattern or args.pattern:
        if args.pattern:
            pattern = str(f"\(https:\/\/{args.pattern}\S*\)")
        content = search_links(pattern=pattern)
        if not content:
            print(f"Empty link list, no match with pattern: {pattern}")
            sys.exit(1)

    if args.input_file:
        with open(args.input_file, mode='r') as item:
            content = item.readlines()

        content = [x.strip() for x in content]

    if not content:
        print(f"{args.input_file} does not contain links")
        sys.exit(1)

    amount_links = len(content)
    for index in progressbar(range(amount_links), "Processing"):
        i += 1
        if args.verbose:
            if i % 100 == 0:
                print(f"Link counter: {i}")
        values = [content[index], validate_url(content[index]),
                  check_status(content[index], args.verbose)]
        links[i] = dict(zip(columns, values))
        time.sleep(0.1)

    if args.verbose:
        for row in links:
            print("URL: {0}, VALID:{1}, STATUS:{2}"
                  .format(links[row]['url'], links[row]['valid_url'],
                          links[row]['status_code']))

    bad_pages = [x['url'] for x in links.values() if x['status_code'] >= 400]
    if not bad_pages:
        print("All links correct!")
        sys.exit(0)
    if args.output_file:
        with open(args.output_file, mode='w') as item:
            for page in bad_pages:
                print(page, file=item)
        print(f"Invalid links written to {args.output_file}")
        sys.exit(0)
    for index, page in enumerate(bad_pages):
        print(f"{index}. {page}")

if __name__ == '__main__':
    main()
