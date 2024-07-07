import requests
from .urls import Urls
from .settings import Settings
import json


class API:
    url = None

    def __init__(self, settings: Settings) -> None:
        self.data = {}
        self.status = False
        self.message = ""
        self.headers = {}
        self.settings = settings

    def request(self, method: str = "get", params={}, data={}, files={}):
        assert self.url is not None, "请先设置url"
        response = requests.request(
            method=method,
            url=self.url,
            headers=self.settings.headers,
            params=params,
            data=data,
            files=files,
        )
        open("log.html", "wb").write(response.content)
        self.headers = response.headers
        self.data = json.loads(response.text)
        self.status = self.data.get("status", False)
        self.message = self.data.get("message", "")
        self.data = self.data.get("data", {})

    def _request_all(self, method: str = "get", params={}):
        assert self.url is not None, "请先设置url"
        response = requests.request(
            method=method, url=self.url, params=params, headers=self.settings.headers
        )
        self.headers = response.headers
        self.data = json.loads(response.text)
        self.status = self.data.get("status", False)
        self.message = self.data.get("message", "")
        data = self.data.get("data", [])
        ans = data.get("data", [])
        if data.get("current_page") != data.get("last_page"):
            params["page"] = data.get("current_page") + 1
            ans += self._request_all(method, params)
        return ans

    def request_all(self, method: str = "get", params={}):
        self.data = self._request_all(method, params)


class Albums(API):
    url = Urls.albums.path


class Images(API):
    url = Urls.images.path


class Profile(API):
    url = Urls.profile.path


class Strategies(API):
    url = Urls.strategies.path


class Upload(API):
    url = Urls.upload.path
