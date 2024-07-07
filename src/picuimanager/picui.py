from pathlib import Path
import requests
import logging.handlers
from .urls import Urls
from typing import Literal, Optional, List, Dict, Tuple
from .files import FilesManager


class PicuiManager:
    def __init__(self, token: str = "", log_file: str = "picui.log"):
        """
        Picui图像管理器,使用网站的API接口交互。
        [接口文档]https://picui.cn/page/api-docs.html

        Args:
            token (str, optional): 用户token. Defaults to "".
            log_file (str, optional): 日志文件. Defaults to "picui.log".
        """
        self.token = token
        self.logger = self._logger(log_file)
        #
        self.X_rate_limit = 1
        self.X_rate_remain = 1

    @property
    def headers(self) -> Dict[str, str]:
        """
        请求picui.cn的头文件

        Returns:
            Dict[str,str]: 头文件字典
        """
        ans = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36",
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json",
            "Connection": "close",
        }
        return ans

    def _logger(self, log_file: str) -> logging.Logger:
        """
        日志管理

        Args:
            log_file (str): 日志文件

        Returns:
            logging.Logger: 日志管理器
        """
        log_file: Path = Path(log_file)
        Path(log_file).parent.mkdir(exist_ok=True, parents=True)
        logger = logging.getLogger(log_file.name)
        logger.setLevel(logging.DEBUG)
        streamhandler = logging.StreamHandler()
        filehandler = logging.handlers.TimedRotatingFileHandler(
            log_file.as_posix(),
            when="D",
            interval=1,
            backupCount=7,
            encoding="utf-8",
        )
        logger.addHandler(filehandler)
        logger.addHandler(streamhandler)
        return logger

    def request(
        self,
        url: str,
        method: str = "get",
        params={},
        data={},
        files={},
    ) -> Dict:
        if self.X_rate_remain == 0:
            exception = "请求配额已用完，等待重置"
            self.logger.info(exception)
            raise Exception(exception)

        response = requests.request(
            method=method,
            url=url,
            headers=self.headers,
            params=params,
            data=data,
            files=files,
        )

        if response.status_code != 200:
            if response.status_code == 401:
                exception = "未登录或授权失败"
            elif response.status_code == 403:
                exception = "管理员关闭了接口功能或没有该接口权限"
            elif response.status_code == 429:
                exception = "超出请求配额，请求受限"
            elif response.status_code == 500:
                exception = "服务器出现异常"
            else:
                exception = f"请求失败，状态码：{response.status_code}"
            self.logger.info(exception)
            raise Exception(exception)

        headers = response.headers
        self.X_rate_limit = int(headers.get("X-RateLimit-Limit", 0))
        self.X_rate_remain = int(headers.get("X-RateLimit-Remaining", 0))

        data = response.json()
        status = data.get("status", False)
        message = data.get("message", "")
        if status == False:
            self.logger.info(f"状态异常，{message}")
            raise Exception(f"状态异常，{message}")

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

        self.logger.info(f"成功获取{url},{current_page}/{page}页")

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


