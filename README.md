# zipfile-zstd
[![PyPI](https://img.shields.io/pypi/v/zipfile-zstd)](https://pypi.org/project/zipfile-zstd/)

Monkey patch the standard `zipfile` module to enable Zstandard support.

Based on [`zipfile-deflate64`](https://github.com/brianhelba/zipfile-deflate64), which provides similar functionality but for the `deflate64` algorithm. Unlike `zipfile-deflate64`, this package supports both compression and decompression.

Requires [`python-zstandard`](https://github.com/indygreg/python-zstandard) for libzstd bindings.

## Installation
```bash
pip install zipfile-zstd
```

## Usage
Anywhere in a Python codebase:
```python
import zipfile_zstd  # This has the side effect of patching the zipfile module to support Zstandard
```

Alternatively, `zipfile_zstd` re-exports the `zipfile` API, as a convenience:
```python
import zipfile_zstd as zipfile

zipfile.ZipFile(...)
```

Compression example:
```python
import zipfile_zstd as zipfile

zf = zipfile.ZipFile('/tmp/test.zip', 'w', zipfile.ZIP_ZSTANDARD, compresslevel=19)
zf.write('large_file.img')
```

Dictionaries and advanced compression parameters are not supported, sorry.

