import hashlib
import typing
import dataclasses

@dataclasses.dataclass
class MultihashResult:
    """The result of running a file through the supported hashing algorithms"""
    sha256: bytes

    def get_hash_by_id(self, id: int) -> bytes:
        if id == 0:
            return self.sha256
        else:
            raise ValueError("Unknown hash algorithm ID:", id)
            

def get_multihash(file: typing.BinaryIO) -> MultihashResult:
    """Read the contents of the given file, and compute the hashes of the file"""
    hashes = [
        hashlib.sha256(),
    ]

    data = file.read(16384)
    while data:
        for h in hashes:
            h.update(data)
        data = file.read(16384)
    
    return MultihashResult(
        sha256=hashes[0].digest()
    )
