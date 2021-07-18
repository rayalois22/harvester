import argparse
import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import colorama

NAME = "Harvest"
VERSION = "v1.0.0"

GREEN = None
GRAY = None
RESET = None 
YELLOW = None

class Harvest():
    links = set()
    page_links = set()
    internal_urls = set()
    external_urls = set()
    hops = 0
    pages = 0
    max_hops = 30
    max_pages = 100
    verbosity = 0

    def __init__(self) -> None:
        pass

    def __repr__(self) -> str:
        pass

    def __str__(self) -> str:
        pass

    def init_colorama():
        colorama.init()
        global GREEN, GRAY, RESET, YELLOW
        GREEN = colorama.Fore.GREEN
        GRAY  = colorama.Fore.LIGHTBLACK_EX
        RESET = colorama.Fore.RESET
        YELLOW = colorama.Fore.YELLOW

    @staticmethod
    def is_valid(url):
        '''
        Checks whether `url` is a valid URL
        '''
        parsed = urlparse(url)
        return bool(parsed.netloc) and bool(parsed.scheme)

    @classmethod
    def _generate_page_links(cls, url):
        '''
        Returns all URLs that are found on `url` in which 
        each URL belongs to the same website
        '''
        cls.page_links.clear()
        domain_name = urlparse(url).netloc
        soup = BeautifulSoup(requests.get(url).content, "html.parser")

        for a_tag in soup.findAll("a"):
            href = a_tag.attrs.get("href")
            if href == "" or href is None:
                continue
            if href.startswith("javascript:;"):
                continue
            href = urljoin(url, href)
            parsed_href = urlparse(href)
            href = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path.rstrip("/")
            if not cls.is_valid(href):
                continue
            if domain_name not in href:
                if href not in cls.external_urls:
                    if cls.verbosity > 2:
                        print(f"{GRAY}[!] External link: {href}{RESET}")
                    cls.external_urls.add(href)
                continue
            if cls.verbosity > 2:
                print(f"{GREEN}[*] Internal link: {href}{RESET}")
            cls.internal_urls.add(href)
            cls.page_links.add(href)

    @classmethod
    def _process_page_links(cls):
        '''
        Process url
        '''
        cls.links.update(cls.page_links)
        page = set()
        page.update(cls.links)
        while len(page) > 0:
            if cls.pages > cls.max_pages:
                break
            link = page.pop()
            if cls.verbosity > 0:
                print(f"{YELLOW}[*] Crawling: {link}{RESET}")
            cls._generate_page_links(link)
            cls.links.update(cls.page_links)

    @classmethod
    def crawl(cls):
        '''
        Crawls a web page and extracts all links.
        
        params:
            max_urls (int): number of max urls to crawl. default is 30.
        '''
        args = cls.cmd()
        cls.max_hops = args.hops
        cls.max_pages = args.pages
        cls.verbosity = args.verbosity
        cls.init_colorama()
        cls.hops += 1
        if cls.verbosity > 2:
            print(f"[=>]{GREEN} Hop {cls.hops}")
        cls._generate_page_links(args.url)
        cls._process_page_links()

    @staticmethod
    def cmd() -> argparse.Namespace:
        '''Uses argparse to handle commandline 
        arguments.
        
        See: https://docs.python.org/3/howto/argparse.html#id1
        '''
        global NAME, VERSION

        parser = argparse.ArgumentParser()

        description = f"{NAME} {VERSION} - Crawls the web"

        usage = '''
            prog [options] url

            Crawls all web pages under the authority of the 
            given url, retrieving and storing all URLs found on
            the pages. An important distinction is made betweeen 
            internal and external URLs and only internal URLs are crawled.
            External URLs are stored in a different file though.
            '''

        parser.description = description
        parser.usage = usage

        parser.add_argument(
            "url",
            help="the URL to crawl",
            type=str
        )

        parser.add_argument(
            "-m",
            "--hops",
            help="maximum hops",
            action="store",
            type=int,
            default=30
        )

        parser.add_argument(
            "-p",
            "--pages",
            help="maximum pages",
            action="store",
            type=int,
            default=100
        )

        verbosityGroup = parser.add_mutually_exclusive_group()
        
        verbosityGroup.add_argument(
            "-v",
            "--verbosity",
            help="increase output verbosity",
            action="count",
            default=0
        )

        verbosityGroup.add_argument(
            "-q",
            "--quiet",
            help="run stealthily",
            action="store_true"
        )

        return parser.parse_args()
        