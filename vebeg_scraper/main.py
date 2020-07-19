from urllib import request
from http.client import HTTPResponse
from bs4 import BeautifulSoup
import logging


class VebegSracper:

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.headers = { "User-Agent" : "Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"}
    
    def __send_request(self, url: str) -> HTTPResponse:
        request_obj = request.Request(self.base_url+url, headers=self.headers)
        return request.urlopen(request_obj)
    
    def __get_response_content_as_str(self, response: HTTPResponse ) -> str:
        encoding = response.info().get_content_charset('iso-8859-1')
        return response.read().decode(encoding)
    
    def get_car_listings(self):
        response = self.__send_request("/web/de/verkauf/suchen.htm?DO_SUCHE=1&SUCH_MATGRUPPE=1000&SUCH_STARTREC=0")
        if response.status == 200:
            bs_full_html = BeautifulSoup(self.__get_response_content_as_str(response),"html.parser")
            bs_offers_table = bs_full_html.find(id="content-wrapper")
            for offer in bs_offers_table.select("a.los-detaillink.tracklink"):
                print(offer['href'])
            
        else:
            logging.error(f"Car listings returned statuscode {response.status}")



s = VebegSracper("https://www.vebeg.de")

s.get_car_listings()