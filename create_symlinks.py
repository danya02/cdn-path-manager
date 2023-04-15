import CONFIG
from database import *
from pathlib import Path

def make_path_symlink_to_asset(path: Path, asset: BlobAsset) -> None:
    """Make it so that the path provided becomes a symbolic link to the given blob asset's path."""
    asset_path = asset.get_path().resolve().absolute()
    path.symlink_to(asset_path)
