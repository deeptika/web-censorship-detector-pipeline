import requests
from link_finder import LinkFinder
from general import *
from scrapy.exceptions import CloseSpider
import logging
import signal
import os
import sys
logger = logging.getLogger(__name__)

class Spider:

    # Class variables (shared among all instances)
    project_name = ''
    base_url = ''
    domain_name = ''
    queue_file = ''
    crawled_file = ''
    queue = set()
    crawled = set()

    # Limit the spider to crawl
    # Change the variable "N" to set the number of links to crawl
    N = 15  # Here change 10 to how many you want.
    count = 0  # The count starts at zero.

    def __init__(self, project_name, base_url, domain_name):
        Spider.project_name = project_name
        Spider.base_url = base_url
        Spider.domain_name = domain_name
        Spider.queue_file = Spider.project_name + '/queue.txt'
        Spider.crawled_file = Spider.project_name + '/crawled.txt'
        self.boot()
        self.crawl_page('First Spider', Spider.base_url)

    @staticmethod
    def boot():
        create_project_dir(Spider.project_name)
        create_data_files(Spider.project_name, Spider.base_url)
        Spider.queue = file_to_set(Spider.queue_file)
        Spider.crawled = file_to_set(Spider.crawled_file)

    @staticmethod
    def crawl_page(thread_name, page_url):
        if page_url not in Spider.crawled:
            print(thread_name + ' now crawling ' + page_url)
            print('Queue ' + str(len(Spider.queue)) + ' | Crawled ' + str(len(Spider.crawled)))
            Spider.add_links_to_queue(Spider.gather_links(page_url))
            if page_url in Spider.queue:
                Spider.queue.remove(page_url)
            Spider.crawled.add(page_url)
            Spider.update_files()

    @staticmethod
    def gather_links(page_url):
        #print(page_url)
        # logic to stop spider at specified count of pages parsed
        # Return if more than N
        # Approach 1
        if Spider.count >= Spider.N:
            # Spider.close_down = True
            #raise CloseSpider(f"Scraped {Spider.N} items. Eject!")
            #sys.exit()
            os._exit(1)
        # Increment to count by one:
        Spider.count += 1

        # Approach 1
        hdr = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
            'Accept-Encoding': 'identity',
            'Accept-Language': 'en-US,en;q=0.8',
            'Connection': 'keep-alive'}

        # # Approach 2
        # user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
        # headers = {'User-Agent': user_agent, }

        # Similarly for login we can pass cookie information also and bypass logins there

        # Next task - use URL proxies using crawlee concept to bypass any other error not only 403 - making it more robust


        html_string = ''
        try:
            # Approach 1
            r = requests.get(page_url, headers=hdr)
            # print("r.content check", r.content)
            # # Approach 2
            # r = requests.get(page_url, headers = headers)

            html_bytes = r.content
            html_string = html_bytes.decode("utf-8", errors='ignore')

            # assert html_string == r.text

            finder = LinkFinder(Spider.base_url, page_url)
            finder.feed(html_string)
        except requests.exceptions.RequestException as e:
            #print(r)
            print('Error: Cannot crawl the page')
            return set()
        return finder.page_links()

    @staticmethod
    def add_links_to_queue(links):
        for url in links:
            if url in Spider.queue:
                continue
            if url in Spider.crawled:
                continue
            if Spider.domain_name not in url:
                continue
            Spider.queue.add(url)

    @staticmethod
    def update_files():
        set_to_file(Spider.queue, Spider.queue_file)
        set_to_file(Spider.crawled, Spider.crawled_file)
