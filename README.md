#Lightning Abstracts Screen-scraper

This is the code that will (hopefully) run as a cronjob on the completed Lightning Abstracts website.  Ultimately, it will use Ruby on Rails's sqlite3 database, but for now I've created a dummy database that will allow it to run independently.  Open test.db with sqlite3 to check out how it looks now, sans all the tables related to users and their article preferences.

To use this demo-scraper, just run read_feeds.py.

The program will access the "journal" table in test.db and visit all the journal listed therein, using the stored URL and appropriate screen-scraping function (right now it only supports articles hosted by Science Direct) to add any new abstracts to the "article" table.  This takes a while, so kill it at any time with Ctrl-C.
