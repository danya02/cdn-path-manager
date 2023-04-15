import CONFIG
from CONFIG import db
import peewee as pw
import os
from pathlib import Path
from multihashing import MultihashResult
import typing

def create_table(cls):
    db.create_tables([cls])
    return cls

class MyModel(pw.Model):
    class Meta:
        database = db

HASH_ALGO_NAMES = {
    0: 'sha256',
}

@create_table
class FileExtension(MyModel):
    """Represents a file extension"""
    ext = pw.CharField(default='', unique=True)

    @classmethod
    def get_by_name(cls, name: str) -> MyModel:
        try:
            new_ext = cls(ext=name)
            new_ext.save()
            return new_ext
        except pw.IntegrityError:
            return cls.get(cls.ext == name)


@create_table
class BlobAsset(MyModel):
    """Represents a content-addressed file, with no associated path."""
    hash_algo = pw.SmallIntegerField(default=0)

    hash = pw.BlobField()
    size = pw.BigIntegerField(index=True)
    file_ext = pw.ForeignKeyField(FileExtension, null=True)

    class Meta:
        indexes = (
            (('hash_algo', 'hash'), True),
        )

    @classmethod
    def find_by_multihash(cls: MyModel, multihash: MultihashResult) -> typing.List[MyModel]:
        return list(
            BlobAsset.select()\
            .where((cls.hash_algo == 0) & (cls.hash == multihash.sha256))\
            #.orwhere((cls.hash_algo == 1) & (cls.hash == multihash.sha256))
        )
    
    def get_path(self) -> Path:
        return get_file_path(self.hash_algo, self.hash, self.file_ext.name if self.file_ext else '')


def get_file_path(hash_algo_id: int, hash: bytes, file_ext: str, also_make_dirs=True) -> Path:
    """Returns a path to a file according to its hash within the blob file directory."""
    if hash_algo_id not in HASH_ALGO_NAMES:
        raise ValueError("Unknown hash algorithm ID:", hash_algo_id)
    hash_algo_name = HASH_ALGO_NAMES[hash_algo_id]

    file_name = hash.hex() + (f'.{file_ext}' if file_ext else '')
    path_components = [CONFIG.BLOB_PATH, f"by-{hash_algo_name}"]
    for end_byte in range(CONFIG.BLOB_PATH_DEPTH):
        byte_range = hash[0:end_byte+1]
        path_components.append(byte_range.hex())
    path_components.append(file_name)
    
    file_path = Path(*path_components)

    # Ensure that the directory exists
    if also_make_dirs:
        os.makedirs(file_path.parent, exist_ok=True)
    
    return file_path

@create_table
class MappedFile(MyModel):
    """Represents a file reference that lives in the mapping directory and references a BlobAsset."""

    file_name = pw.CharField(unique=True)  # Relative path inside the mapping directory, like 'images/1337/hello.png'
    content = pw.ForeignKeyField(BlobAsset, backref="referring_files")
