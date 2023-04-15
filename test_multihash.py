from multihashing import *
import io

def test_parallel_hashing():
    data = io.BytesIO(b"Nobody inspects the spammish repetition")
    multihash = get_multihash(data)
    assert multihash == MultihashResult(
        sha256=bytes.fromhex('031edd7d41651593c5fe5c006fa5752b37fddff7bc4e843aa6af0c950f4b9406')
    )