import argparse
import json
from pathlib import Path

from picuimanager import FilesManager, PicuiManager, TinifyManager
from picuimanager.utils.confirm import confirm

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("root1", type=str)
    parser.add_argument("root2", type=str)
    parser.add_argument("picui", type=str)
    parser.add_argument("tinify", type=str)
    parser.add_argument("--relation", type=str, default="logs/relation.json")
    args = parser.parse_args()

    fm1 = FilesManager(args.root1)
    fm2 = FilesManager(args.root2)

    pm = PicuiManager(args.picui)
    tm = TinifyManager(args.tinify)

    relation_file = Path(args.relation)
    if relation_file.exists():
        relation = json.load(open(relation_file, "r"))
    else:
        if confirm("Relation file not found, create new one?"):
            relation = {}
        else:
            exit(0)

    pm.logger.info("-" * 10 + "synchronize original images with zipped images")

    status, relation = fm1.sync(
        fm=fm2,
        relation=relation,
        zip_func=tm.compress,
        method="sha1",
    )
    if status:
        pm.logger.info("-" * 10 + "update relation file")
        json.dump(relation, open(relation_file, "w"), indent=4)

    pm.logger.info("-" * 10 + "synchronize zipped images with picui.cn")
    pm.sync(fm2)
