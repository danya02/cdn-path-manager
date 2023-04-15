import peewee
# Database containing the mappings between files and their contents
db = peewee.SqliteDatabase('./file_assets.sqlite')

# Path to the directory where the underlying blobs are stored
BLOB_PATH = './blobs'

# The depth of the file hierarchy in the blobs directory.
# With the default of 2, file paths will look like: './blobs/by-sha256/1a/1a2b/1a2b3c4d5e6f...'
# With 1, './blobs/by-sha256/1a/1a2b3c4d5e6f...'
# With 4, './blobs/by-sha256/1a/1a2b/1a2b3c/1a2b3c4d/1a2b3c4d5e6f...'
BLOB_PATH_DEPTH = 2

# Path to the mapping directory.
# This is where symlinks will be created,
# and from where files will be moved into the blob directory to be replaced with their paths.
MAPPING_PATH='./files'

