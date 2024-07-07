from pathlib import Path
from typing import List
import tinify
import threading


class TinifyThread(threading.Thread):
    def __init__(self, src, dst):
        threading.Thread.__init__(self)
        self.src = src
        self.dst = dst
        Path(dst).parent.mkdir(exist_ok=True, parents=True)

    def run(self):
        tinify.from_file(self.src).to_file(self.dst)
        print(self.src, "->", self.dst)


class TinifyManager:
    def __init__(self, api_key: str):
        tinify.key = api_key

    def upload(self, root1: Path, root2: Path, paths: List[str]):
        threads = []
        for p in paths:
            threads.append(TinifyThread((root1 / p).as_posix(), (root2 / p).as_posix()))
        print(f"开始压缩{len(threads)}个文件...")
        for t in threads:
            t.start()
        for t in threads:
            t.join()
