from picuimanager import FilesManager, PicuiManager
from picuimanager.utils.warning import disable_warning
from picuimanager.utils.confirm import confirm_choice, confirm


def sync(pm: PicuiManager, fm: FilesManager, album_id: int, permission: str):
    remote_images = pm.get_images(permission="private", album_id=album_id)
    remote_images += pm.get_images(permission="public", album_id=album_id)
    remote = pm.get_hashes(remote_images)
    local = fm.get_hashes()
    all_hashs = set(local.keys()) | set(remote.keys())

    delete_items = []
    upload_items = []

    for h in all_hashs:
        l_e = h in local
        r_e = h in remote
        if l_e and r_e:
            continue
        if r_e:
            delete_items.append(h)
        if l_e:
            upload_items.append(h)

    if not confirm(
        f"{len(delete_items)} images will be deleted,{len(upload_items)} images will be uploaded. Continue?"
    ):
        return

    for i, h in enumerate(delete_items):
        pm.delete_image(key=remote[h])
        pm.logger.info(f"Deleted {i+1}/{len(delete_items)} {remote[h]}")

    for i, h in enumerate(upload_items):
        pm.upload_image(
            path=(fm.root / local[h]).as_posix(),
            permission=int(permission == "public"),
            album_id=album_id,
        )
        pm.logger.info(f"Uploaded {i+1}/{len(upload_items)} {local[h]}")


if __name__ == "__main__":
    disable_warning()
    root = input("Enter the root directory: ")
    fm = FilesManager(root)
    token = input("Enter your token: ")
    pm = PicuiManager(token)
    albums = pm.get_albums()
    print(albums)
    albums_id = [str(i["id"]) for i in albums]
    album_id = int(confirm_choice("Choose your album:", albums_id))
    permission = confirm_choice("Choose your permission:", ["public", "private"])
    sync(pm, fm, album_id, permission)
