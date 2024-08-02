import hashlib
import shutil
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, List, Literal, Tuple

from tqdm import tqdm

from picuimanager.utils.confirm import confirm
from picuimanager.utils.logger import get_logger


class FilesManager:
    suffixs: List[str] = [".jpg", ".jpeg", ".png", ".gif"]

    def __init__(self, root: str, log_name: str = "files") -> None:
        self.root: Path = Path(root)
        self.logger = get_logger(name=log_name)
        if not self.root.exists():
            raise FileNotFoundError(f"Root directory '{root}' does not exist")

    @property
    def image_list(self) -> List[Path]:
        return [
            x for x in self.root.rglob("*") if x.is_file() and x.suffix in self.suffixs
        ]

    def get_hashes(self, method: Literal["md5", "sha1"] = "sha1") -> Dict[str, str]:
        """
        hash_code -> image relative path

        Args:
            method (Literal["md5", "sha1"]): method for hashing

        Raises:
            ValueError: Invalid method

        Returns:
            Dict[str, str]: hash_code -> image relative path
        """
        ans = {}
        for f in tqdm(
            self.image_list,
            desc=f"Get hashes of {self.root}",
        ):
            if method == "md5":
                k = hashlib.md5(f.read_bytes()).hexdigest()
            elif method == "sha1":
                k = hashlib.sha1(f.read_bytes()).hexdigest()
            else:
                raise ValueError(f"Invalid method '{method}'")
            v = f.relative_to(self.root).as_posix()
            ans[k] = v
        return ans
