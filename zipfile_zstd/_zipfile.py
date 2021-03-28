
import zipfile
import zstandard as zstd
import threading

from ._patcher import patch


zipfile.ZIP_ZSTANDARD = 93
zipfile.compressor_names[zipfile.ZIP_ZSTANDARD] = 'zstandard'
zipfile.ZSTANDARD_VERSION = 63


@patch(zipfile, '_check_compression')
def zstd_check_compression(compression):
    if compression == zipfile.ZIP_ZSTANDARD:
        pass
    else:
        patch.originals['_check_compression'](compression)


class ZstdDecompressObjWrapper:
    def __init__(self, o):
        self.o = o

    def __getattr__(self, attr):
        if attr == 'eof':
            return False
        return getattr(self.o, attr)


@patch(zipfile, '_get_decompressor')
def zstd_get_decompressor(compress_type):
    if compress_type == zipfile.ZIP_ZSTANDARD:
        return ZstdDecompressObjWrapper(zstd.ZstdDecompressor().decompressobj())
    else:
        return patch.originals['_get_decompressor'](compress_type)


@patch(zipfile, '_get_compressor')
def zstd_get_compressor(compress_type, compresslevel=None):
    if compress_type == zipfile.ZIP_ZSTANDARD:
        if compresslevel is None:
            compresslevel = 3
        return zstd.ZstdCompressor(level=compresslevel, threads=12).compressobj()
    else:
        return patch.originals['_get_compressor'](compress_type, compresslevel=compresslevel)


@patch(zipfile.ZipInfo, 'FileHeader')
def zstd_FileHeader(self, zip64=None):
    if self.compress_type == zipfile.ZIP_ZSTANDARD:
        self.create_version = max(self.create_version, zipfile.ZSTANDARD_VERSION)
        self.extract_version = max(self.extract_version, zipfile.ZSTANDARD_VERSION)
    return patch.originals['FileHeader'](self, zip64=zip64)


