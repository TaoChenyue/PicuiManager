from enum import Enum


class Urls(Enum):
    profile = "profile/"
    strategies = "strategies/"
    albums = "albums/"
    images = "images/"
    upload = "upload/"

    @property
    def path(self):
        return "https://picui.cn/api/v1/" + self.value
