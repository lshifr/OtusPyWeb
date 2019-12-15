from pagelinks import page_links, is_valid_link
import click

DEFAULT_ENTRY = 'http://www.yandex.ru'


@click.command()
@click.option('--maxlinks', default=100, help='Max number of links.')
@click.option('--depth', default=5, help='Max recursion depth.')
@click.option('--recursive/--non-recursive', default=True, help='Process links recursively')
@click.argument('url', default=DEFAULT_ENTRY)
def display_links(maxlinks, depth, recursive, url):
    """
    Displays to the console a set of links from a wep page

    :param maxlinks:
        Maximal number of links to get / display

    :param depth:
        Maximal recursive depth for recursive search

    :param recursive:
        Whether or not search recursively

    :param url:
        The url of the main page / entry point

    :return:
        None
    """
    if not is_valid_link(url):
        print("The string '{}' does not look like a valid url".format(url))
        return
    print("Collecting links for page {}".format(url))
    for count, link in enumerate(
            page_links(url, max_links=maxlinks, max_depth=depth, recursive=recursive)
    ):
        print("{}  {}".format(count+1, link))


if __name__ == '__main__':
    display_links()
