import os
import json
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup

BASE_URL = "https://consultaplacas.com.br"
BASE_DIR = os.getcwd()

retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504, 104],
    allowed_methods=["HEAD", "POST", "PUT", "GET", "OPTIONS"]
)
adapter = HTTPAdapter(max_retries=retry_strategy)


class Browser(object):

    def __init__(self):
        self.response = None
        self.headers = self.get_headers()
        self.session = requests.Session()

    def get_headers(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/87.0.4280.88 Safari/537.36"
        }
        return self.headers

    def get_soup(self):
        return BeautifulSoup(self.response.content, "html.parser")

    def send_request(self, method, url, **kwargs):
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
        return self.session.request(method, url, **kwargs)


class PlatesAPI(Browser):

    def __init__(self, plate):
        super().__init__()
        self.plate = plate
        self.token = None
        self.get_token()

    def get_token(self):
        self.response = self.send_request(
            "GET",
            f"{BASE_URL}",
            headers=self.headers
        )
        self.token = self.get_soup().find_all("input")[0]["value"]

    def search(self):
        payload = {
            "_token": self.token,
            "plate": self.plate
        }
        self.headers["referer"] = BASE_URL
        self.response = self.send_request(
            "POST",
            f"{BASE_URL}/search/apigratis",
            data=payload,
            headers=self.headers
        )
        return self.response


if __name__ == "__main__":
    client = PlatesAPI("gvt0671")
    result = client.search()
    print(json.dumps(result.json(), indent=4))
