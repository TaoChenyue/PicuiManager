from pathlib import Path
from typing import Dict, Literal, Callable
from tqdm import tqdm
import hashlib
import shutil


class FilesManager:
    def __init__(self, root: str) -> None:
        self.root: Path = Path(root)
        if not self.root.exists():
            raise FileNotFoundError(f"Root directory '{root}' does not exist")

    def get_hashes(self, method: Literal["md5", "sha1"]) -> Dict[str, str]:
        """
        返回目录所有文件的{文件内容哈希值:文件绝对路径}

        Args:
            method (Literal["md5", "sha1"]): 加密算法

        Raises:
            ValueError: 不允许的加密算法

        Returns:
            Dict[str, str]: {文件内容哈希值:文件绝对路径}
        """
        ans = {}
        for f in tqdm(
            [x for x in self.root.rglob("*") if x.is_file()],
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

    def sync(
        self,
        fm: "FilesManager",
        relation: Dict[str, str],
        sync_func: Callable,
        method: Literal["md5", "sha1"] = "sha1",
        cache_dir: str = "images/cache",
    ) -> None:
        hash1 = self.get_hashes(method=method)
        hash2 = fm.get_hashes(method=method)

        Path(cache_dir).mkdir(exist_ok=True, parents=True)
        cache = FilesManager(cache_dir)

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
        files = [x.relative_to(self.root) for x in self.root.rglob("*") if x.is_file()]
        for f in files:
            dst_path = cache.root / f
            if not dst_path.exists():
                sync_list.append(f)
        sync_func(self.root, cache.root, sync_list)

        shutil.rmtree(fm.root.as_posix())
        cache.root.rename(fm.root)

        new_relation = {}
        hash2 = fm.get_hashes(method=method)
        for k1, v1 in hash1.items():
            for k2, v2 in hash2.items():
                if v1 == v2:
                    new_relation[k1] = k2

        return new_relation
