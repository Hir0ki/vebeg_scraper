import pathlib
from bs4 import BeautifulSoup

class TestProxy:

    def __init__(self, url):
        test_path = pathlib.Path(__file__).parent
        main_page_file = test_path.joinpath("main_page.html") 
        self.main_page_bs = BeautifulSoup(main_page_file.read_text(), "html.parser")
        self.listings_page_bs = BeautifulSoup(test_path.joinpath("listings.html").read_text(), "html.parser")
        self.listing_page_bs = BeautifulSoup(test_path.joinpath("listing.html").read_text(), "html.parser")

    def get_bs_from_url(self, url):
        if  url =="/web/de/start/index.htm":
            return self.main_page_bs

