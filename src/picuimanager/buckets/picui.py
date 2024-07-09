from enum import Enum
from typing import Dict, List, Literal, Optional

import requests

from picuimanager.utils.confirm import confirm
from picuimanager.utils.logger import get_logger

from .files import FilesManager


class Urls(Enum):
    profile = "profile/"
    strategies = "strategies/"
    albums = "albums/"
    images = "images/"
    upload = "upload/"

    @property
    def path(self):
        return "https://picui.cn/api/v1/" + self.value


class ErrorStatus(Enum):
    _401 = "unauthorized"
    _403 = "API disabled by administrator"
    _429 = "request quota is exceeded and restricted"
    _500 = "server exception"
    unknown = "unknown error"


class PicuiManager:
    def __init__(self, token: str = "", log_file: Optional[str] = None):
        """
        Manage images in picui.cn, see [API docs]https://picui.cn/page/api-docs.html

        Args:
            token (str, optional): user token. Defaults to "".
            log_file (str, optional): file for log. Defaults to None.
        """
        self.token = token
        self.logger = get_logger(log_file)
        #
        self.X_rate_limit = 1
        self.X_rate_remain = 1

    @property
    def _headers(self) -> Dict[str, str]:
        """
        headers for request

        Returns:
            Dict[str, str]: header with token
        """
        return {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json",
        }

    def _report_error(self, message: str):
        self.logger.info(message)
        raise Exception(message)

    def _report_error_status_code(self, status_code: int):
        if status_code == 200:
            return
        if status_code != 200:
            if status_code == 401:
                message = ErrorStatus._401
            elif status_code == 403:
                message = ErrorStatus._403
            elif status_code == 429:
                message = ErrorStatus._429
            elif status_code == 500:
                message = ErrorStatus._500
            else:
                message = f"{ErrorStatus.unknown}, status_code={status_code}"
            self._report_error(message=message)

    def _parse_headers(self, headers: Dict[str, str]):
        self.X_rate_limit = int(headers.get("X-RateLimit-Limit", 0))
        self.X_rate_remain = int(headers.get("X-RateLimit-Remaining", 0))

    def request(
        self,
        url: str,
        method: str = "get",
        params={},
        data={},
        files={},
    ) -> Dict:
        if self.X_rate_remain == 0:
            exception = "request quota is exceeded, wait for reseting please."
            self.logger.info(exception)
            raise Exception(exception)

        response = requests.request(
            method=method,
            url=url,
            headers=self._headers,
            params=params,
            data=data,
            files=files,
        )

        self._report_error_status_code(response.status_code)
        self._parse_headers(headers=response.headers)

        try:
            data = response.json()
        except:
            self._report_error("response is not json")

        if not data.get("status", False):
            self._report_error(message=data.get("message", ""))

        data = data.get("data", {})

        return data

    def get_pages(
        self,
        url: str,
        params: Dict = {},
    ) -> List:
        page = params.get("page", 1)
        params["page"] = page

        ans = []
        data = self.request(
            url=url,
            params=params,
        )
        ans += data.get("data", [])

        current_page = data.get("current_page", 0)
        last_page = data.get("last_page", 0)

        self.logger.info(f"Got {url},{current_page}/{page}页")

        if current_page != last_page:
            ans += self.get_pages(
                url,
                {**params, "page": page + 1},
            )
        return ans

    def get_profile(self):
        return self.request(
            url=Urls.profile.path,
        )

    def get_strategies(self):
        return self.request(
            url=Urls.strategies.path,
        )

    def get_images(
        self,
        order: Literal["newest", "earliest", "utmost", "least"] = "newest",
        permission: Literal["public", "private"] = "private",
        album_id: Optional[int] = None,
        q: Optional[str] = None,
    ):
        params = {"order": order, "permission": permission}
        if album_id is not None:
            params["album_id"] = album_id
        if q is not None:
            params["q"] = q
        return self.get_pages(url=Urls.images.path, params=params)

    def get_albums(
        self,
        order: Literal["newest", "earliest", "utmost", "least"] = "newest",
        q: Optional[str] = None,
    ):
        params = {"order": order}
        if q is not None:
            params["q"] = q
        return self.get_pages(url=Urls.albums.path, params=params)

    def delete_image(self, key: str):
        self.request(url=Urls.images.path + key, method="delete")

    def delte_album(self, album_id: str):
        self.request(url=Urls.albums.path + album_id, method="delete")

    def upload_image(
        self,
        path: str,
        token: Optional[str] = None,
        permission: Literal[1, 0] = 0,
        strategy_id: Optional[int] = None,
        album_id: Optional[int] = None,
        expired_at: Optional[str] = None,
    ):
        data = {
            "permission": permission,
        }
        files = {"file": open(path, "rb")}
        if token is not None:
            data["token"] = token
        if strategy_id is not None:
            data["strategy_id"] = strategy_id
        if album_id is not None:
            data["album_id"] = album_id
        if expired_at is not None:
            data["expired_at"] = expired_at
        ans = self.request(url=Urls.upload.path, method="post", data=data, files=files)
        return ans

    def get_hashes(self, info: List[Dict], method: Literal["md5", "sha1"] = "sha1"):
        if method not in ["md5", "sha1"]:
            raise ValueError("method must be 'md5' or 'sha1'")
        return {x[method]: x["key"] for x in info}

    def sync(self, fm: FilesManager, method: Literal["md5", "sha1"] = "sha1"):
        remote_images = self.get_images()
        remote = self.get_hashes(remote_images, method=method)
        local = fm.get_hashes(method=method)
        all_hashs = set(local.keys()) | set(remote.keys())

        delete_items = []
        upload_items = []

        for h in all_hashs:
            l_e = h in local
            r_e = h in remote
            if l_e and r_e:
                continue
            if r_e:
                delete_items.append(h)
            if l_e:
                upload_items.append(h)

        if not confirm(
            f"{len(delete_items)} images will be deleted,{len(upload_items)} images will be uploaded. Continue?"
        ):
            return

        for i, h in enumerate(delete_items):
            self.delete_image(key=remote[h])
            self.logger.info(f"Deleted {i}/{len(delete_items)} {remote[h]}")

        for i, h in enumerate(upload_items):
            self.upload_image(path=(fm.root / local[h]).as_posix())
            self.logger.info(f"Uploaded {i}/{len(upload_items)} {local[h]}")
