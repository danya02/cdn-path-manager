import CONFIG
from CONFIG import db
import peewee as pw
import os

def create_table(cls):
    db.create_tables([cls])
    return cls

class MyModel(pw.Model):
    class Meta:
        database = db

@create_table
class BlobAsset(MyModel):
    """Represents a content-addressed file, with no associated path."""
    hash_algo = pw.SmallIntegerField(default=0)
    # Algorithm IDs:
    #  - 0: SHA256
    #  ...

    hash = pw.BlobField()
    size = pw.BigIntegerField(index=True)
    file_ext = pw.CharField()

    class Meta:
        indexes = (
            (('hash_algo', 'hash'), True),
        )

def get_file_path(hash_algo_id: int, hash: bytes, file_ext: str) -> str:
    """Returns a path to a file according to its hash within the blob file directory."""
    hash_algos = {
        0: 'sha256',
    }
    if hash_algo_id not in hash_algos:
        raise ValueError("Unknown hash algorithm ID:", hash_algo_id)
    hash_algo_name = hash_algos[hash_algo_id]

    file_name = hash.hex() + (f'.{file_ext}' if file_ext else '')
    path_components = [CONFIG.BLOB_PATH, f"by-{hash_algo_name}"]
    for end_byte in range(CONFIG.BLOB_PATH_DEPTH):
        byte_range = hash[0:end_byte+1]
        path_components.append(byte_range.hex())
    path_components.append(file_name)
    return os.path.join(*path_components)

@create_table
class MappedFile(MyModel):
    """Represents a file reference that lives in the mapping directory and references a BlobAsset."""

    file_name = pw.CharField(unique=True)  # Relative path inside the mapping directory, like 'images/1337/hello.png'
    content = pw.ForeignKeyField(BlobAsset, backref="referring_files")
