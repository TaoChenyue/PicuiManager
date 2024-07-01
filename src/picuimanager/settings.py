from pathlib import Path


class Settings:
    def __init__(self, token: str = ""):
        self.token = token

    def get_token(self, token_file: str = "picui.token"):
        if Path(token_file).exists():
            with open(token_file, "r") as f:
                self.token = f.read()
        else:
            self.token = input("Enter your token: ")

    @property
    def headers(self):
        ans = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36",
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json",
            "Connection": "close",
        }
        return ans
