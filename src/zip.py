from pathlib import Path
import tinify
import threading


class Download(threading.Thread):
    def __init__(self, src, dst):
        threading.Thread.__init__(self)
        self.src = src
        self.dst = dst

    def run(self):
        tinify.from_file(self.src).to_file(self.dst)
        print(self.src, "->", self.dst)


def zip_image(
    root: str,
    output: str,
    key: str,
):
    tinify.key = key
    root: Path = Path(root)
    output: Path = Path(output)
    output.mkdir(exist_ok=True, parents=True)
    threads = []
    for image in [x for x in root.rglob("*") if x.is_file()]:
        dst = output / image.relative_to(root)
        if dst.exists():
            continue
        dst.parent.mkdir(exist_ok=True, parents=True)
        threads.append(Download(image, dst))
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    print(tinify.compression_count)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=str)
    parser.add_argument("output", type=str)
    args = parser.parse_args()
    
    if Path("tinify.key").exists():
        key = Path("tinify.key").read_text().strip()
    else:
        key = input("Tinify API Key: ")
   
    zip_image(args.root, args.output, key)
