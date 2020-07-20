from urllib import request
from http.client import HTTPResponse, HTTPException
from bs4 import BeautifulSoup, element  # type: ignore
from vebeg_scraper.models import Category
from typing import List, Optional
import logging


class RequestProxy:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
        }

    def get_bs_from_url(self, url: str) -> BeautifulSoup:
        response_object = self.__send_request(url)
        return BeautifulSoup(
            self.__get_response_content_as_str(response_object), "html.parser"
        )

    def __send_request(self, url: str) -> HTTPResponse:
        request_obj = request.Request(self.base_url + url, headers=self.headers)
        response = request.urlopen(request_obj)
        if response.status == 200:
            return response
        else:
            raise HTTPException

    def __get_response_content_as_str(self, response: HTTPResponse) -> str:
        encoding = response.info().get_content_charset("iso-8859-1")
        return response.read().decode(encoding)

    def get_car_listings(self):
        response = self.__send_request(
            "/web/de/verkauf/suchen.htm?DO_SUCHE=1&SUCH_MATGRUPPE=1000&SUCH_STARTREC=0"
        )
        if response.status == 200:
            bs_full_html = BeautifulSoup(
                self.__get_response_content_as_str(response), "html.parser"
            )
            bs_offers_table = bs_full_html.find(id="content-wrapper")
            for offer in bs_offers_table.select("a.los-detaillink.tracklink"):
                print(offer["href"])

        else:
            logging.error(f"Car listings returned statuscode {response.status}")


class CategoryParser:
    def __init__(self, request_proxy: RequestProxy):
        self.request_proxy = request_proxy
        self.base_url = "/web/de/start/index.htm"

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
            logging.error(f"Parse category tag error {tag}", exc_info=error)
        return Category(
            id=id, name=tag.contents[0], is_top_level=is_top_level, parent_id=parent_id
        )


s = RequestProxy("https://www.vebeg.de")

cat = CategoryParser(s)
cat.get_categories()
