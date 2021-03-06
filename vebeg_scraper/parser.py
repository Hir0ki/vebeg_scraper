from vebeg_scraper.proxy import RequestProxy
from typing import List, Optional, Dict
from vebeg_scraper.models import Listing, Category, GEBOTSBASIS_NAMES, AuctionResult
from vebeg_scraper.serializer.postgres_serializer.postgress_serializer import Database
from bs4 import element, BeautifulSoup  # type: ignore
from datetime import datetime
from vebeg_scraper import settings
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
                new_cat = self.__parse_a_tag(child, False, top_level_cat.id)
                if new_cat.id not in [cat.id for cat in results]:
                    results.append(new_cat)
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
            id=id,
            name=clean_string(str(tag.contents[0])),
            is_top_level=is_top_level,
            parent_id=parent_id,
        )


class ListingsParser:
    def __init__(
        self,
        request_proxy: RequestProxy,
        categories: List[Category],
        database: Database,
        will_download_pictures: bool,
    ):
        self.request_proxy = request_proxy
        self.base_url = "/web/de/verkauf/suchen.htm?DO_SUCHE=1"
        self.matgruppe_template = "&SUCH_MATGRUPPE="
        self.such_opsition = "&SUCH_STARTREC="
        self.categories = categories
        self.database = database
        self.will_download_pictures = will_download_pictures
        self.logger = logging.getLogger("scraper.listings")

    def __get_listings_for_category(self, category: Category) -> List[Listing]:
        url_with_matgruppe = self.base_url + self.matgruppe_template + str(category.id)
        page_count = 0
        listing_urls: List[str] = []
        run = True
        self.logger.info(f"Start scraping Listings cat:{category.id}")
        while run:
            rqeuest_url = url_with_matgruppe + self.such_opsition + str(page_count)
            listings_bs = self.request_proxy.get_bs_from_url(rqeuest_url)
            new_listing_urls = self.__parse_listing_for_urls(listings_bs)
            if len(new_listing_urls) == 0:
                run = False
            listing_urls = listing_urls + new_listing_urls
            page_count = page_count + 20

        listings: List[Listing] = []
        listing_parser = ListingParser(self.request_proxy, self.will_download_pictures)
        for listing_url in listing_urls:
            listings.append(listing_parser.get_listing(listing_url, category))
        self.logger.info("Writing data to database")
        [self.database.write_listing(listing) for listing in listings]
        return listings

    def __parse_listing_for_urls(self, listings_bs: BeautifulSoup) -> List[str]:
        content = listings_bs.find(id="content")
        tags = content.select("a.los-detaillink.tracklink")
        results = []
        for a_tag in tags:
            results.append(a_tag.get("href"))
        return results

    def get_listings(self) -> List[Listing]:
        listings: List[Listing] = []
        for category in self.categories:
            if category.is_top_level is False:
                listings = listings + self.__get_listings_for_category(category)

        return listings


class ListingParser:
    def __init__(self, request_proxy: RequestProxy, will_download_pictures: bool):
        self.request_proxy = request_proxy
        self.download_dir = pathlib.Path(settings.PICTURE_CACHE_PATH)
        if not self.download_dir.is_dir():
            self.download_dir.mkdir()
        self.logger = logging.getLogger("scraper.listing")
        self.will_download_pictures = will_download_pictures
        self.gebotsbasis_regex = re.compile(
            r"Gebotsbasis({}|{})".format(GEBOTSBASIS_NAMES[0], GEBOTSBASIS_NAMES[1])
        )

    def get_listing(self, listing_url: str, category: Category) -> Listing:
        listing_bs = self.request_proxy.get_bs_from_url(listing_url)
        self.logger.info(f"parsing listing url:{listing_url} category:{category.id}")
        content = listing_bs.find(id="content")
        id = int(
            content.select("div.iconlink.losdetail_ausnr")[0]
            .find("b")
            .text.replace(".", "")
        )
        gebotstermin_str = clean_string(
            content.select("div.iconlink.losdetail_gebotstermin")[0].find("b").text
        )
        if gebotstermin_str.lower() != "sofortverkauf":
            gebotstermin = datetime.strptime(gebotstermin_str, "%d.%m.%Y, %H:%M h")
        else:
            gebotstermin = datetime.now()

        title = clean_string(content.find("h1").text)
        kurzbeschreibung = content.find("p").text

        regex_gebotsbasis = self.gebotsbasis_regex.search(
            content.select("td.detailtable.b_rdotted")[0].text
        )
        if regex_gebotsbasis is not None:
            gebotsbasis = regex_gebotsbasis.group(1)
        else:
            self.logger.warning(f"Didn't find gebotsbasis in listing: {id}")
            gebotsbasis = ""
        lagerort = content.select("td.detailtable.detailtable_lagerort")[
            0
        ].text.replace("Lagerort / Standort", "")
        daten = self.__parse_data_listing(content)

        pictures_html_container = content.select("td.detailtable.b_l")
        picture_paths = []
        if len(pictures_html_container) == 1 and self.will_download_pictures is True:
            picture_paths = self.__download_pictures(
                [
                    a_tag.get("href")
                    for a_tag in pictures_html_container[0].find_all("a")
                ],
                id,
            )
        else:
            logging.info(f"No pictures for listing: {id}")

        return Listing(
            id=id,
            title=title,
            daten=daten,
            kurzbeschreibung=kurzbeschreibung,
            gebotsbasis=gebotsbasis,
            lagerort=lagerort,
            pictures_paths=picture_paths,
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

    def __download_pictures(self, urls: List[str], id: int) -> List[pathlib.Path]:

        picture_paths: List[pathlib.Path] = []
        for count, url in enumerate(urls):
            if "javascript" not in url.lower():
                picture_data = self.request_proxy.get_picture_from_url(url)
                picture_path = self.download_dir.joinpath(f"{id}_{count}.jpg")
                if not picture_path.is_file():
                    picture_path.write_bytes(picture_data)
                    picture_paths.append(picture_path)
                else:
                    self.logger.error(
                        f"picture was already downlaoded name: {id}_{count}"
                    )
        return picture_paths


class AuctionResultsParser:
    def __init__(self, request_porxy: RequestProxy):
        self.request_porxy = request_porxy
        self.url = "/web/de/verkauf/zuschlagspreise.htm"
        self.logger = logging.getLogger("scraper.AuctionResults")

    def get_all_results(self) -> List[AuctionResult]:
        result_bs = self.request_porxy.get_bs_from_url(self.url)
        results: List[AuctionResult] = []
        for row in result_bs.select("tr.highlighonhover.zuschlag_user"):
            columns = row.find_all("td")
            id = int(columns[0].text.replace(".", ""))
            gebotstermin = datetime.strptime(columns[1].text, "%d.%m.%Y")
            value = float(
                columns[3].text.replace("€", "").replace(".", "").replace(",", ".")
            )
            results.append(AuctionResult(id, gebotstermin, value))
        return results


def clean_string(string: str) -> str:
    return " ".join(string.split())
