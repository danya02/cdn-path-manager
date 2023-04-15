import peewee
from pathlib import Path
# Database containing the mappings between files and their contents
db = peewee.SqliteDatabase('./file_assets.sqlite')

# Path to the directory where the underlying blobs are stored
BLOB_PATH = './blobs/'
BLOB_PATH = Path(BLOB_PATH)

# The depth of the file hierarchy in the blobs directory.
# With the default of 2, file paths will look like: './blobs/by-sha256/1a/1a2b/1a2b3c4d5e6f...'
# With 1, './blobs/by-sha256/1a/1a2b3c4d5e6f...'
# With 4, './blobs/by-sha256/1a/1a2b/1a2b3c/1a2b3c4d/1a2b3c4d5e6f...'
BLOB_PATH_DEPTH = 2

# Path to the mapping directory.
# This is where symlinks will be created,
# and from where files will be moved into the blob directory to be replaced with their paths.
MAPPING_PATH='./files/'
MAPPING_PATH = Path(MAPPING_PATH)

# Preferred hash algorithm for new files.
# Refers to the internal hash algorithm IDs; see `database.py` for a list along with the IDs.
NEW_FILE_HASH_ALGO = 0