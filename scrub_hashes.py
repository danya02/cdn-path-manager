import CONFIG
from database import *
import multihashing
import datetime
from concurrent.futures import ThreadPoolExecutor

def scrub_file(asset: BlobAsset) -> bool:
    """Compute the hash of the file on disk and compare it to the database hash"""
    # Quick check: does file size match?
    if asset.get_path().stat().st_size != asset.size:
        print("!!! Asset", asset, "failed file size check")
        return

    # Slow check: does file hash match?
    with open(asset.get_path().absolute(), 'rb') as o:
        multihash = multihashing.get_multihash(o)
    if asset.verify_multihash(multihash):
        asset.last_scrubbed_at = datetime.datetime.now()
        asset.save()
        return True
    else:
        print("!!! Asset", asset, "failed scrub")
        return False

def main():
    """Scrub all files older than a threshold."""
    with ThreadPoolExecutor(32) as tp:
        for i, scrub_result in tp.map(lambda x: (x, scrub_file(x)),
            BlobAsset.select().where(BlobAsset.last_scrubbed_at < (datetime.datetime.now() - datetime.timedelta(days=7))).iterator()
        ):
            if not scrub_result:
                print(i, 'failed scrub')

if __name__ == '__main__':
    main()