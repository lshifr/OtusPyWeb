from bs4 import BeautifulSoup
import re
import requests

url_pattern = re.compile('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*'
    + re.escape('(')
    + re.escape(')')
    + ']|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
)


def is_valid_link(url):
    """
    Tests a url for validity. Relative urls are considered invalid
    :param url: A url string
    :return: Boolean
    """
    return isinstance(url, str) and url_pattern.match(url) is not None


def make_request(url):
    """
    Encapsulates the logic of making a request.
    :param url: A url string
    :return: A string with response text if response status code is 200, and None otherwise
    """
    try:
        if not is_valid_link(url):
            return None
        resp = requests.get(url)
        if resp.status_code != 200:
            return None
        else:
            return resp.text
    except ConnectionError:
        return None


def get_links(html):
    """
    A generator to return all valid links (their href property) found on the web page
    :param html: The HTML contents of a web page, as a string
    :return:  A generator of strings
    """
    if not isinstance(html, str):
        yield None
    else:
        soup = BeautifulSoup(html, 'html.parser')
        for link in soup.find_all('a'):
            href = link.get('href')
            if is_valid_link(href):
                yield href
