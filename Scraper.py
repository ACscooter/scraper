from bs4 import BeautifulSoup
import requests
import json
import os

class Scraper:
    """Scraper object serves as a super class to all website scrapers. All
    Scrapers have the document limit set to 1000 by default. Scraping formats
    the data into json form and stores it into the data attribute.

    BeautifulSoup4 is used to handle all HTML parsing.
    """

    def __init__(self, document_limit = 1000):
        self.document_limit = document_limit
        self.data = {}

    def scrape(self):
        """Requires all subclasses to implement the scrape method."""
        raise NotImplementedError

    def soup(self, url):
        """Returns a BeautifulSoup object for the given url."""
        result = requests.get(url)
        return BeautifulSoup(result.text, "html.parser")

    def load(self, data, key, tags):
        """Stores the input into the data as a dictionary with the keys found in
        tags. The key argument denotes the key in self.data for which the each
        input is stored in.
        """
        assert type(data) == list, "Expecting list as input"
        for elem in data:
            entry = {k : elem[k] for k in tags}
            self.data[elem[key]] = entry

    def dump(self, filename):
        """Dumps the contents of data into "filename" placed in the "data"
        directory. If no directory with the name data is found, one will be
        created.
        """
        target = os.getcwd() + '/../data'
        if not os.path.isdir(target):
            os.mkdir(target)
        output = os.path.join(target, filename)
        with open(output, 'wb') as f:
            f.write(json.dumps(self.data))
            f.close()


class BuzzScraper(Scraper):
    """An object that scrapes BuzzFeed for article names.

    BuzzScraper requires that the community be inputed by the user. It also
    allows the user to set how many pages it she wants to scrape. By default,
    page_limit is set to -1 forcing it to scrape by document count.

    The current format of BuzzFeed's topic pages dictate that all target article
    names are placed under the "section Column1" <div> tag. To find the <li>
    tags with article information, we use beautiful soup and pass in a lambda
    function that determines if the tag has the attributes 'id' and 'rel:data'
    and the word "post" is in tag['id']. The lambda is stored in self.searcher.

    TARGET_URL : The URL to scrape.
    DIV_SEARCH : Search specs for the div
    """

    TARGET_URL = "http://www.buzzfeed.com/{}?p=11&z=4POKDW&r={}"
    DIV_SEARCH = {'class' : 'section Column1'}

    def __init__(self, page_limit = -1):
        Scraper.__init__(self)
        self.page_limit = page_limit
        self.searcher = lambda t : t.has_attr('id') and "post" in tag['id'] and t.has_attr('rel:data')

    def scrape(self, community):
        """Returns a collection of articles scraped from the given BuzzFeed
        community. It also stores two extra attributes in each document:
        publisher and store_key. The store_key is the key used in self.data and
        publisher is BuzzFeed.

        TODO: Should I add an assert for the buzz-id part?
        """
        documents = []
        if page_limit != -1:
            for page in range(1, page_limit + 1):
                url = self.TARGET_URL.format(community, page)
                documents += self.find_data(url)
        else:
            i = 0
            page = 1
            while i < self.document_limit:
                url = self.TARGET_URL.format(community, page)
                for d in self.find_data(url):
                    documents.append(d)
                    i += 1
                page += 1

        for doc in documents:
            doc['publisher'] = "BuzzFeed"
            doc['store_key'] = "BuzzFeed-" + doc['buzz-id'] # Assumes that theres a buzz-id

        tags = ['buzz_id', 'name', 'store_key', 'publisher']
        self.load(documents, 'store_key' tags)

    def find_data(self, url):
        """Generates all the preliminary data before it is stored in self.data.
        Makes a call to self.soup which returns a BeautifulSoup object after
        parsing through the url's HTML.
        """
        soup = self.soup(url)
        documents = soup.find_all("div", self.DIV_SEARCH).find_all(self.searcher)
        return [r['rel:data'] for r in documents]

class ClickHoleScraper(Scraper):
    """An object that scrapes Click Hole.

    Note: You may want to wrap this package in python
    https://www.npmjs.com/package/clickhole-headlines
    """

class GoogleScraper(Scraper):
    """An object that scrapes Google News.

    TODO: Implement
    """
