import CONFIG
from database import *
from pathlib import Path

def make_path_symlink_to_asset(path: Path, asset: BlobAsset) -> None:
    """Make it so that the path provided becomes a symbolic link to the given blob asset's path."""
    asset_path = asset.get_path().resolve().absolute()
    path.symlink_to(asset_path)

def restore_symlinks():
    """
    Iterate over mapped files in the database.
    For each one, ensure that there is a corresponding symlink in the mapped directory,
    and create them if missing.
    """

    for mapped_file in MappedFile.select().join(BlobAsset).iterator():
        target_path: Path = CONFIG.MAPPING_PATH / mapped_file.file_path
        if target_path.is_symlink():
            
            # If this symlink's target is inside the blob path,
            # and is the right one,
            # then it is OK
            if target_path.resolve().is_relative_to(CONFIG.BLOB_PATH.absolute()) and \
                    target_path.resolve().relative_to(CONFIG.BLOB_PATH.absolute()) == mapped_file.content.get_path().resolve().relative_to(CONFIG.BLOB_PATH.absolute()):
                # OK
                continue
            else:
                # Symlink exists, but is pointing at wrong thing
                # Remove and recreate symlink
                print(target_path, 'pointing at wrong item')
                target_path.unlink()
                make_path_symlink_to_asset(target_path, mapped_file.content)
                continue
        else:
            # File is not a symlink
            if target_path.exists():
                print(target_path, 'exists but is not a symlink')
                continue
            else:
                # File does not exist: create directories to it, then make symlink
                os.makedirs(target_path.parent, exist_ok=True)
                make_path_symlink_to_asset(target_path, mapped_file.content)
                print(target_path, 'created')
                continue

if __name__ == '__main__':
    restore_symlinks()
