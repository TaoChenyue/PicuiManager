from picuimanager import Settings, Albums, Upload, Images, Urls
from pathlib import Path
import json
from tqdm import tqdm
import argparse
import requests


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("dir", type=str, help="directory")
    return parser.parse_args()


def delete_all():
    settings = Settings()
    settings.get_token()
    images = Images(settings)
    images.request_all()
    delete_keys = [x["key"] for x in images.data]
    for url in tqdm(delete_keys):
        requests.delete(url=Urls.images.path + url, headers=settings.headers)


def sync_dir(path: str):
    settings = Settings()
    settings.get_token()

    record_path = Path("record.json")
    if not record_path.exists():
        record_path.touch()
        json.dump({}, open("record.json", "w"), indent=4)

    record = json.load(open("record.json", "r"))
    keys_local = [v["key"] for v in record.values()]

    remote_images = Images(settings)
    remote_images.request_all()
    with open("images.json", "w") as f:
        json.dump(remote_images.data, f, indent=4)
    keys_remote = [x["key"] for x in remote_images.data]

    keys_delete = [x for x in keys_remote if x not in keys_local]
    for key in tqdm(keys_delete, desc="deleting"):
        requests.delete(url=Urls.images.path + key, headers=settings.headers)

    root = Path(path)
    images = [x for x in root.rglob("*") if x.is_file()]

    keys_upload = [x for x in images if x.relative_to(root).as_posix() not in record]
    upload = Upload(settings)
    for image in tqdm(keys_upload, desc="uploading"):
        key = image.relative_to(root).as_posix()
        upload.request(method="post", files={image.name: open(image, "rb")})
        record[key] = upload.data
        json.dump(record, open("record.json", "w"), indent=4)


if __name__ == "__main__":
    args = parse_args()
    sync_dir(args.dir)
