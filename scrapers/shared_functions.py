# Jason Mushinski, 1/11/14
# Basic functions shared by all scraper programs

import urllib2, sqlite3

def add_everything(conn, curs, url, journal_url, title, author, volume, abstract, codes, keywords):
    '''In case the process of adding an article's info to the database needs to be changed, I'll put it in this nice separate function'''
    
    add_article(conn, curs, url, journal_url, title, author, volume, abstract)
    
    if codes:
        add_JEL(conn, curs, url, codes)

    if keywords:
        add_keywords(conn, curs, url, keywords)
                
    # Eventually this should be output to a log file...
    print_nicely(title, volume, author, url, abstract, codes, keywords)


def add_article(conn, curs, url, journal_url, title, author, volume, abstract):
    '''Using an existing SQLite connection, adds an article's info to the database.'''
    
    curs.execute('''insert into article (url, journal, title, author, volume, abstract) values (?,?,?,?,?,?)''', (url,journal_url,title,author,volume,abstract) )
    conn.commit()


def add_JEL(conn, curs, article_url, codes):
    '''Adds an article's JEL codes to the correct table.'''

    for code in codes:
        curs.execute('''INSERT INTO contains_JEL VALUES (?,?)''', (article_url,code) )
        
    conn.commit()


def add_keywords(conn, curs, article_url, keywords):
    '''Adds an article's keywords to the correct table.'''

    for key in keywords:
        curs.execute('''INSERT INTO contains_keyword VALUES (?,?)''', (article_url,key) )

    conn.commit()
    
    
def after_redirects(url):
    '''Takes a link to an article from the RSS feed and follows all of its redirects, then returns the final address it arrives at.'''

    opener = urllib2.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    page = opener.open(url)

    return page.geturl()
    
    
def read_source(url):
    '''Returns the HTML source of a given webpage.'''

    opener = urllib2.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    source = opener.open(url).read()
    opener.close()

    return source


def print_nicely(title, volume, author, url, abstract, codes, keywords):
    '''Print out all the scrubbed data in a nice way.'''

    print title
    print volume
    print author
    print url, '\n'
    print abstract, '\n'
    print "JEL codes:",

    print codes
    print keywords
    
    for code in codes:
        print code + ",",

    print "\n", "Keywords:",

    for word in keywords:
        print word + ",",

    print "\n\n", "---------------------------", "\n"
