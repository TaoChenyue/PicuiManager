import hashlib
import shutil
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, List, Literal, Optional, Tuple

from tqdm import tqdm

from picuimanager.utils.confirm import confirm
from picuimanager.utils.logger import get_logger


class FilesManager:
    suffixs: List[str] = [".jpg", ".jpeg", ".png", ".gif"]

    def __init__(self, root: str, log_file: Optional[str] = None) -> None:
        self.root: Path = Path(root)
        self.logger = get_logger(log_file=log_file)
        if not self.root.exists():
            raise FileNotFoundError(f"Root directory '{root}' does not exist")

    @property
    def image_list(self) -> List[Path]:
        return [
            x for x in self.root.rglob("*") if x.is_file() and x.suffix in self.suffixs
        ]

    def get_hashes(self, method: Literal["md5", "sha1"]) -> Dict[str, str]:
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

    @staticmethod
    def generate_cache(root: Path) -> "FilesManager":
        cache_name = hashlib.md5(
            datetime.now().strftime("%Y%m%d%H%M%S").encode()
        ).hexdigest()
        cache_dir: Path = root.parent / f"{root.stem}_{cache_name}"
        cache_dir.mkdir(exist_ok=True, parents=True)
        return FilesManager(cache_dir)

    def generate_relation(
        self, fm: "FilesManager", method: Literal["md5", "sha1"] = "sha1"
    ) -> Dict[str, str]:
        hash1 = self.get_hashes(method=method)
        hash2 = fm.get_hashes(method=method)
        new_relation = {}
        for k1, v1 in hash1.items():
            for k2, v2 in hash2.items():
                if v1 == v2:
                    new_relation[k1] = k2
        return new_relation

    def sync(
        self,
        fm: "FilesManager",
        relation: Dict[str, str],
        zip_func: Callable,
        method: Literal["md5", "sha1"] = "sha1",
    ) -> Tuple[bool, Dict[str, str]]:
        hash1 = self.get_hashes(method=method)
        hash2 = fm.get_hashes(method=method)

        cache = self.generate_cache(fm.root)

        if not confirm(f"record has {len(relation)} items, are you sure?"):
            return False, relation

        for k, v in tqdm(
            relation.items(),
            desc=f"Validating relation",
        ):
            if k in hash1 and v in hash2:
                src_path = fm.root / hash2[v]
                dst_path = cache.root / hash1[k]
                dst_path.parent.mkdir(exist_ok=True, parents=True)
                src_path.rename(dst_path)

        sync_list = []
        for f in self.image_list:
            dst_path = cache.root / f.relative_to(self.root)
            if not dst_path.exists():
                sync_list.append(f.relative_to(self.root))

        try:
            zip_func(self.root, cache.root, sync_list)
        except:
            print("Zip failed")

        shutil.rmtree(fm.root.as_posix())
        cache.root.rename(fm.root)

        return True, self.generate_relation(fm, method=method)
