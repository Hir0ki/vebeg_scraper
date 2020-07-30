from vebeg_scraper.proxy import RequestProxy
from typing import List, Optional
from vebeg_scraper.models import Listing, Category, GEBOTSBASIS_NAMES, Dict
from bs4 import element, BeautifulSoup  # type: ignore
from datetime import datetime
import re
import logging
import pathlib


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
        self.gebotsbasis_regex = re.compile(
            r"Gebotsbasis({}|{})".format(GEBOTSBASIS_NAMES[0], GEBOTSBASIS_NAMES[1])
        )

    def __get_listings_for_category(self, category: Category) -> List[Listing]:
        url_with_matgruppe = self.base_url + self.matgruppe_template + str(category.id)
        page_count = 0
        listing_urls: List[str] = []
        run = True
        self.logger.info("Start scraping Listings")
        while run:
            rqeuest_url = url_with_matgruppe + self.such_opsition + str(page_count)
            listings_bs = self.request_proxy.get_bs_from_url(rqeuest_url)
            listing_urls = self.__parse_listing_for_urls(listings_bs)
            if len(listing_urls) == 0:
                run = False
            page_count = page_count + 20

        listings: List[Listing] = []
        for listing_url in listing_urls:
            listings.append(self._parse_lisitng(listing_url, category))
        return listings

    def _parse_lisitng(self, listing_url: str, category: Category) -> Listing:
        listing_bs = self.request_proxy.get_bs_from_url(listing_url)
        self.logger.info(f"parsing listing url:{listing_url} category:{category.id}")
        content = listing_bs.find(id="content")
        id = int(
            content.select("div.iconlink.losdetail_ausnr")[0]
            .find("b")
            .text.replace(".", "")
        )
        gebotstermin_str = self.__clean_string(
            content.select("div.iconlink.losdetail_gebotstermin")[0].find("b").text
        )
        gebotstermin = datetime.strptime(gebotstermin_str, "%d.%m.%Y,%H:%M h")
        title = self.__clean_string(content.find("h1").text)
        kurzbeschreibung = content.find("p").text

        regex_gebotsbasis = self.gebotsbasis_regex.search(
            content.select("td.detailtable.b_rdotted")[0].text
        )
        if regex_gebotsbasis is not None:
            gebotsbasis = regex_gebotsbasis.group(1)
        else:
            self.logger.warning(
                f"Didn't find gebotsbasis in listing url: {listing_url}"
            )
        lagerort = content.select("td.detailtable.detailtable_lagerort")[
            0
        ].text.replace("Lagerort / Standort", "")
        daten = self.__parse_data_listing(content)
        return Listing(
            id=id,
            title=title,
            daten=daten,
            kurzbeschreibung=kurzbeschreibung,
            gebotsbasis=gebotsbasis,
            lagerort=lagerort,
            pictures_paths=[],
            attachments=[],
            category=category,
            gebotstermin=gebotstermin,
        )

    def __parse_data_listing(self, content: BeautifulSoup) -> Dict[str, str]:
        table_left = content.select("td.detaildata_right")
        table_right = content.select("td.detaildata_left")
        output_dict: Dict[str, str] = {}
        for counter, key in enumerate(table_right):
            entry = table_left[counter]
            output_dict[key.text.strip(":")] = entry.text
        return output_dict

    def __parse_listing_for_urls(self, listings_bs: BeautifulSoup) -> List[str]:
        content = listings_bs.find(id="content")
        tags = content.select("a.los-detaillink.tracklink")
        results = []
        for a_tag in tags:
            results.append(a_tag.get("href"))
        return results

    def __clean_string(self, string: str) -> str:
        return string.replace("\n", "").replace("\t", "")

    def get_listings(self) -> List[Listing]:
        listings: List[Listing] = []
        for category in self.categories:
            if category.is_top_level is False:
                listings = listings + self.__get_listings_for_category(category)

        return listings
