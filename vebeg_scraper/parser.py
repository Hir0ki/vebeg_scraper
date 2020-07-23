from vebeg_scraper.proxy import RequestProxy
from typing import List, Optional
from vebeg_scraper.models import Listing, Category
from bs4 import element, BeautifulSoup
import logging

class CategoryParser:
    def __init__(self, request_proxy: RequestProxy):
        self.request_proxy = request_proxy
        self.base_url = "/web/de/start/index.htm"
        self.logger = logging.getLogger("scraper.category")

    def get_categories(self) -> List[Category]:
        results = []
        main_page = self.request_proxy.get_bs_from_url(self.base_url)
        menu_bar = main_page.find(id="menubar-wrapper")
        level1 = menu_bar.select("a.menulevel1")
        for tag in level1:
            top_level_cat = self.__parse_a_tag(tag, True)
            results.append(top_level_cat)
            children: List[element.Tag] = sum(
                [i.find_all("a") for i in tag.parent.find_all("li")], []
            )
            for child in children:
                results.append(self.__parse_a_tag(child, False, top_level_cat.id))
        return results

    def __parse_a_tag(
        self, tag: element.Tag, is_top_level: bool, parent_id: Optional[int] = None
    ) -> Category:
        # excract id from url
        url = str(tag.get("href"))
        try:
            id_offset_start = int(url.find("MATGRUPPE=") + 10)
            id = int(url[id_offset_start : id_offset_start + 4])
        except ValueError as error:
            id = 0
            self.logger.error(f"Parse category tag error {tag}", exc_info=error)
        return Category(
            id=id, name=tag.contents[0], is_top_level=is_top_level, parent_id=parent_id
        )

class ListingsParser:
    def __init__(self, request_proxy: RequestProxy, categories: List[Category]):
        self.request_proxy = request_proxy
        self.base_url = "/web/de/verkauf/suchen.htm?DO_SUCHE=1"
        self.matgruppe_template = "&SUCH_MATGRUPPE="
        self.such_opsition = "&SUCH_STARTREC="
        self.categories = categories
        self.logger = logging.getLogger("scraper.listings")

    def __get_listings_for_category(self, category: Category) -> List[Listing]:
        url_with_matgruppe = self.base_url + self.matgruppe_template + str(category.id)
        page_count = 0
        listings: List[str] = []
        old_length = -1 
        self.logger.info("Start scraping Listings") 
        while len(listings) > old_length:
            rqeuest_url = url_with_matgruppe + self.such_opsition + str(page_count)
            listings_bs = self.request_proxy.get_bs_from_url(rqeuest_url)
            listings = self.__parse_listing_for_urls(listings_bs)
            page_count = page_count + 20
        for listing_url in listings:
            self.__parse_lisitng(listing_url, category)

    def __parse_lisitng(self, listing_url: str, category: Category) -> Listing:
        listing_bs = self.request_proxy.get_bs_from_url(listing_url)
        print(listing_bs.select("div.iconlink.losdetail_ausnr"))

    def __parse_listing_for_urls(self, listings_bs: BeautifulSoup ) -> List[str]:
        content = listings_bs.find(id="content")
        tags = content.select("a.los-detaillink.tracklink")
        results = []
        for a_tag in tags:
            results.append(a_tag.get('href'))
        return results
        
    def get_listings(self):
        for category in self.categories:
            self.__get_listings_for_category(category)