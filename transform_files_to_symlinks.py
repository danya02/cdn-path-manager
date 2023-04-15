import CONFIG
from database import *
import pathlib
from pathlib import Path
import shutil
import CONFIG
import multihashing
import create_symlinks

def make_file_into_symlink(path: Path):
    """
    Transforms a file in the mapping directory into a symlink,
    moving the file's content into the blob directory.
    """

    # Check that the path is inside the mapping directory and is a file
    rel_path = path.relative_to(CONFIG.MAPPING_PATH)
    if not path.is_file():
        raise ValueError("The given path is not a file: ", path)
    
    # Now check whether a file of this hash is in the database
    with open(path, 'br') as o:
        multihash = multihashing.get_multihash(o)
    
    matching_files = BlobAsset.find_by_multihash(multihash)
    if len(matching_files) > 1:
        print('!!! DATABASE INCONSISTENCY !!!')
        print('While processing file:', path)
        print('Computed multihash:', multihash)
        print('The following files all match this multihash:')
        for file in matching_files:
            print(file, 'is located at', get_file_path(file.hash_algo, file.hash, file.file_ext.ext))
        print('Fix this manually before continuing!')
        exit(1)
    
    elif len(matching_files) == 1:
        # There is already such a file in the asset dir
        # So we need to replace this file with a symlink to that one
        # and create a record in the database about this
        matching_file = matching_files[0]
        with db.atomic():
            MappedFile(
                file_path=str(rel_path),
                content=matching_file
            ).save()
        
        path.unlink()
        create_symlinks.make_path_symlink_to_asset(path, matching_file)
    
    else:
        # There are no matching files,
        # so the current file needs to be moved to where its asset needs to be stored,
        # and a record about it created.
        with db.atomic():
            extension = path.name.split('.')[-1] if '.' in path.name else None
            new_file = BlobAsset(
                hash_algo=CONFIG.NEW_FILE_HASH_ALGO,
                hash=multihash.get_hash_by_id(CONFIG.NEW_FILE_HASH_ALGO),
                size=path.stat().st_size,
                file_ext=FileExtension.get_by_name(extension) if extension else None
            )
            new_file.save()
            MappedFile(
                file_path=str(rel_path),
                content=new_file
            ).save()

            # It is important that the move is performed atomically with the database transaction,
            # so it is placed inside the db.atomic() block.
            shutil.move(path, new_file.get_path())
        
        # The creation of the symlink does not need to be atomic, though,
        # because if it fails then it can be recreated later from the database record.
        # Also, if its failure undoes the transaction, then the moved asset would become hanging.
        create_symlinks.make_path_symlink_to_asset(path, new_file)

def walk(path: Path):
    print(path)
    if path.is_dir():
        for item in path.iterdir():
            walk(item)
    elif path.is_file() and not path.is_symlink():
        print("Transforming", path, "...")
        make_file_into_symlink(path)

def main():
    # Walk the directory tree of the mapping directory looking for files and apply the transformation.
    walk(CONFIG.MAPPING_PATH)

if __name__ == '__main__':
    main()