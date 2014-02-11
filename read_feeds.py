# Jason Mushinski, 1/11/14
# Master abstract-reader - checks every journal in the site database
# for new abstracts and adds them to the db, using the appropriate
# screen-scraper function.

import sqlite3
from scrapers import *

DB_PATH = "test.db"

def main():

    conn = sqlite3.connect(DB_PATH)
    curs = conn.cursor()

    journals = curs.execute('''select * from journal;''').fetchall()

    for journal in journals:
        # For now, print the journal's name
        print journal[1]
        
        url = journal[0]
        scrub_function = journal[3]

        if scrub_function == "science_direct":
            science_direct.main(conn, curs, url)

    
if __name__ == "__main__":
    main()
