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
        """Returns a BeautifulSoup object for the given url.

        TODO: Implement exception handling if there's no response from request
        """
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

    def __init__(self, page_limit = -1):
        Scraper.__init__(self)
        self.page_limit = page_limit

    def scrape(self, community):
        """Returns a collection of articles scraped from the given BuzzFeed
        community. It also stores two extra attributes in each document:
        publisher and store_key. The store_key is the key used in self.data and
        publisher is BuzzFeed.

        TODO: Should I add an assert for the buzz-id part?
        """
        documents = []
        if page_limit != -1:
            for page in range(1, self.page_limit + 1):
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
        searcher = lambda t : t.has_attr('id') and "post" in tag['id'] and t.has_attr('rel:data')
        soup = self.soup(url)
        documents = soup.find_all("div", {'class' : 'section Column1'}).find_all(searcher)
        return [r['rel:data'] for r in documents]

class ClickHoleScraper(Scraper):
    """An object that scrapes ClickHole for article names.

    ClickHoleScraper requires that the community be provided by the users. It
    also allows users to scrape by page. By default, the page limit is set to
    -1.

    The current format of ClickHole does not provide a data json for each
    article like BuzzFeed does. Instead, all articles can be found in an <h2>
    tag with the class titled "headline". These h2 tags are nested under
    <article> tags which are unique to article listings.

    TODO: Provide some kind of exception if it is not a proper community.
    """

    TARGET_URL = "http://www.clickhole.com/features/{}/?page={}"

    def __init__(self, page_limit = -1):
        Scraper.__init__(self)
        self.page_limit = page_limit

    def scrape(self, community):
        """Returns a collection of articles scraped from ClickHole. It also
        stores two extra keys: publisher and store_key. The publisher is
        ClickHole and the store_key is as described above.
        """
        documents = []
        if page_limit != -1:
            for page in range(1, self.page_limit + 1):
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
            doc['publisher'] = "ClickHole"
            doc['store_key'] = "ClickHole-" + doc['article_id']

        tags = ['name', 'publisher', 'store_key', 'article_id']
        self.load(documents, 'store_key', tags)


    def find_data(url):
        """Creates a preliminary list of dictionary objects that contain the
        keys name (for article name) and article_id (the unique article id as
        it is stored on ClickHole servers). The article name is formatted by
        trimming the first and last characters. This is due to the fact that
        each article name is surrounded by a line break character.
        """
        results = []
        soup = self.soup(url)
        articles = soup.find_all("article")
        for a in articles:
            name = a.find("h2", {'class' : 'headline'}).text
            results.append({'name' : name[1 : len(name) - 1],
                'article_id' : a['id']
            })
        return results

class UpworthyScraper(Scraper):
    """An object that scrapes Upworthy.

    TODO: Implement
    """

class UproxxScraper(Scraper):
    """An object that scrapes Uproxx.

    TODO: Implement
    """


class GoogleScraper(Scraper):
    """An object that scrapes Google News.

    TODO: Implement
    """

class NewYorkerScraper(Scraper):
    """An object that scrapes New Yorker article titles.

    TODO: Implement
    """
