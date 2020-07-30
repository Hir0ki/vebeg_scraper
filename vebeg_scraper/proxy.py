from urllib import request
from http.client import HTTPException, HTTPResponse
from bs4 import BeautifulSoup, element  # type: ignore
import logging


class RequestProxy:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
        }
        self.logger = logging.getLogger("scraper.proxy")

    def get_bs_from_url(self, url: str) -> BeautifulSoup:
        response_object = self.__send_request(url)
        content = self.__get_response_content_as_str(response_object)
        return BeautifulSoup(content, "html.parser")

    def get_picture_from_url(self, url: str) -> bytes:
        response_object = self.__send_request(url)
        return response_object.read()

    def __send_request(self, url: str) -> HTTPResponse:
        request_obj = request.Request(self.base_url + url, headers=self.headers)
        self.logger.info(f"Sending request to {url}")
        response: HTTPResponse = request.urlopen(request_obj)
        if response.status == 200:
            return response
        else:
            self.logger.error(
                f"Send request to {url} and got response code {response.status}"
            )
            raise HTTPException

    def __get_response_content_as_str(self, response: HTTPResponse) -> str:
        encoding = response.info().get_content_charset("iso-8859-1")
        return response.read().decode(encoding)
