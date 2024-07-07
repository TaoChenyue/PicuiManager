from picuimanager import PicuiManager, FilesManager, TinifyManager
import json
import argparse
from pathlib import Path

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("root1", type=str)
    parser.add_argument("root2", type=str)
    parser.add_argument("picui", type=str)
    parser.add_argument("tinify", type=str)
    parser.add_argument("--relation", type=str, default="relation.json")
    args = parser.parse_args()

    fm1 = FilesManager(args.root1)
    fm2 = FilesManager(args.root2)

    pm = PicuiManager(args.picui)
    tm = TinifyManager(args.tinify)

    relation_file = Path(args.relation)
    if relation_file.exists():
        relation = json.load(open(relation_file, "r"))
    else:
        confirm = input("Relation file not found, create new one? (y/n)")
        if confirm == "y":
            relation = {}
        else:
            exit(0)

    backup_file = relation_file.parent / f"{relation_file.stem}_backup.json"
    pm.logger.info("-" * 10 + f"backup relation file to {backup_file.as_posix()}")
    backup_file.write_bytes(relation_file.read_bytes())

    pm.logger.info("-" * 10 + "synchronize original images with zipped images")

    relation = fm1.sync(
        fm=fm2,
        relation=relation,
        sync_func=tm.upload,
        method="sha1",
    )

    pm.logger.info("-" * 10 + "update relation file")
    json.dump(relation, open(relation_file, "w"), indent=4)

    pm.logger.info("-" * 10 + "synchronize zipped images with picui.cn")
    pm.sync_images(fm2)
