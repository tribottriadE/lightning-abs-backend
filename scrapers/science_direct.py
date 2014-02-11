# Jason Mushinski, 1/11/14
# Improved function for scraping the abstracts from ScienceDirect
# articles - now with a REAL HTML parser, and a DECENT database schema!

import feedparser, urllib2, re, sqlite3
from bs4 import BeautifulSoup
from shared_functions import *


TEST_URL = "http://rss.sciencedirect.com/publication/science/03043932"
DB_NAME = "test.db"


def get_JEL(soup):
    '''Takes a Beautiful Soup tree representing a Science Direct article, returns a list of its JEL codes (if present)'''
    header = soup.find(is_JEL_header)

    if header:
        # Every item in the list after the header is wrapped in a
        # "span" tag, so...
        items = header.next_sibling.find_all("span")
        return [i.string for i in items]
    
    else:
        return []


def is_JEL_header(tag):
    '''Function allowing Beautiful Soup to find the header for an article's JEL codes.'''
    # Don't try to make string lowercase if it doesn't exist...
    return tag.name == "h2" and tag.string and tag.string.lower() in ("jel classification", "jel classifications")


def get_keywords(soup):
    '''Even if there aren't JEL codes for an article, they all appear to have keywords.  This extracts those as a list, given a Beautiful Soup HTML parse tree.

    This is all repeated code, but I'll keep it that way in case JEL codes and keywords end up having to be scraped in different ways.'''
    header = soup.find(is_keyword_header)

    if header:
        items = header.next_sibling.find_all("span")
        return [i.string for i in items]
    
    else:
        return []


def is_keyword_header(tag):
    '''Function allowing Beautiful Soup to find the header for an article's keywords.'''
    return tag.name == "h2" and tag.string and tag.string.lower() == "keywords"


def process_URL(url):
    '''Takes the URL of a Science Direct article, returns its JEL codes and keywords (as lists) in a tuple.'''

    source = read_source(url)

    soup = BeautifulSoup(source)
    
    codes = get_JEL(soup)
    words = get_keywords(soup)
        
    return (codes, words)


def process_RSS(body):
    '''From the description of a Science Direct RSS feed item, we can extract the relevant article's issue'''
    items = body.split("<br />")

    # The first item is the publication date, which we don't need

    # Next is the journal name, volume, and issue:
    volume = items[1].replace(' <b>Source:</b>', '')

    # Authors:
    author = items[2].replace('     Author(s): ', '')

    # Abstract:
    # Remove the space at the beginning.
    # Eventually we'll want to be able to remove all the html elements...
    abstract = items[3][1:]
    
    return (volume, author, abstract)


def main(conn, curs, feed_url):
    '''Takes a connection and cursor to an sqlite database and the url of a ScienceDirect RSS feed, and updates the database with new abstracts.'''
    # Unfortunately, ScienceDirect feeds don't support either eTags or
    # last-modified dates... sad face.
    
    fd = feedparser.parse(feed_url)

    for entry in fd.entries:
        # First, we check if this article has already been added

        # SO here's the thing about after_redirects... using it means
        # that we have to load the page TWICE, making the one bottleneck
        # in the program even worse.  We need it to load the page without
        # that annoying dynamic-text thing, though.
        # Only using it once we know the article hasn't already been
        # added would make things faster, but the URLs stored in the
        # database would be a lot longer and harder to understand.
        url = after_redirects(entry.link)
        matches = curs.execute('''SELECT * FROM article WHERE url=?''', (url,)).fetchall()

        if not matches:
            volume, author, abstract = process_RSS(entry.description)

            # If there's no abstract (e.g. it's an editorial thing),
            # we don't want it.
            if abstract:
                # The ?np=y stops the page from loading its text
                # dynamically, allowing the scraper to see everything.
                codes, keywords = process_URL(url + "?np=y")
                title = entry.title

                add_everything(conn, curs, url, feed_url, title, author, volume, abstract, codes, keywords)
