from picuimanager import Settings, Images
import argparse
from pathlib import Path

if __name__ == "__main__":
    settings = Settings()
    settings.get_token()

    remote_images = Images(settings)
    remote_images.request_all()

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "path",
        type=str,
        help="Root directory to search for images",
    )
    args = parser.parse_args()

    root: Path = Path(args.path)
    root.mkdir(parents=True, exist_ok=True)
    h_urls = []
    v_urls = []
    s_urls = []

    for image in remote_images.data:
        url = image["links"]["url"]
        width = image["width"]
        height = image["height"]
        ratio = width / height
        if ratio >= 4 / 3:
            dst = h_urls
        elif ratio <= 3 / 4:
            dst = v_urls
        else:
            dst = s_urls
        dst.append(url)

    with open(root / "h.csv", "w") as f:
        f.write("\n".join(h_urls))

    with open(root / "v.csv", "w") as f:
        f.write("\n".join(v_urls))

    with open(root / "s.csv", "w") as f:
        f.write("\n".join(s_urls))
