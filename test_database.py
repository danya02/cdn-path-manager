from database import *


def test_file_path():
    CONFIG.BLOB_PATH = '/blobs'
    CONFIG.BLOB_PATH_DEPTH = 2
    assert get_file_path(0, bytes([0,1,2,3,4,5,6,7,8]), 'png') == '/blobs/by-sha256/00/0001/000102030405060708.png'
    CONFIG.BLOB_PATH_DEPTH = 0
    assert get_file_path(0, bytes([255,254,253,252,251,250]), 'jpg') == '/blobs/by-sha256/fffefdfcfbfa.jpg'