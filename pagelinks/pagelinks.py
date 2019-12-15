from .web import get_links, make_request


def page_links(url, max_links=100, max_depth=5, recursive=True):
    """
    Returns a generator for a set of links found on the specified page,
    and also optionally pages it links to.
    :param url:
        The url of the main page / entry point
    :param max_links:
        Maximal number of links to get / display
    :param max_depth:
        Maximal recursive depth for recursive search
    :param recursive:
        Whether or not search recursively
    :return:
        A generator of string urls
    """
    found_links = set()
    if not recursive:
        max_depth = 0

    def crawl(url, current_depth):
        if current_depth > max_depth or len(found_links) >= max_links:
            # Stop if we have enough links already, or if recursion got too deep
            return None
        html = make_request(url)
        for link in get_links(html):
            if len(found_links) < max_links:
                if link not in found_links:  # Do not add a link more than once
                    found_links.add(link)
                    yield link
            else:
                return None
        if len(found_links) < max_links:
            for link in set(found_links):  # Make a copy of the set, since found_links will change during the call
                yield from crawl(link, current_depth + 1)

    for href in crawl(url, 0):
        if href is not None:
            yield href
