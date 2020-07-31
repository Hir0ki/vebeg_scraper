from http.client import HTTPException
from bs4 import BeautifulSoup  # type: ignore
import pathlib


class TestProxy:
    def __init__(self, url):
        test_path = pathlib.Path(__file__).parent
        main_page_file = test_path.joinpath("main_page.html")
        self.main_page_bs = BeautifulSoup(main_page_file.read_text(), "html.parser")
        self.listings_page_bs = BeautifulSoup(
            test_path.joinpath("listings.html").read_text(), "html.parser"
        )
        self.listing_page_bs = BeautifulSoup(
            test_path.joinpath("listing.html").read_text(), "html.parser"
        )

    def get_bs_from_url(self, url: str):
        if url == "/web/de/start/index.htm":
            return self.main_page_bs
        elif (
            "/web/de/verkauf/suchen.htm?DO_SUCHE=1&SUCH_MATGRUPPE=1000&SUCH_STARTREC=0"
            in url
            or "/web/de/verkauf/suchen.htm?DO_SUCHE=1&SUCH_MATGRUPPE=1757&SUCH_STARTREC=0"
            in url
        ):
            return self.listings_page_bs
        elif "test_listing":
            return self.listing_page_bs

        raise HTTPException

    def get_picture_from_url(self, url):
        return pathlib.Path(__file__).parent.joinpath("test_picture.jpg").read_bytes()
