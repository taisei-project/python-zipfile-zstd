import os
import sys
import hashlib
import subprocess
import pytest
try:
    from tempfile import TemporaryDirectory
except ImportError:
    from backports.tempfile import TemporaryDirectory
try:
    from inspect import signature
except ImportError:
    from funcsigs import signature

mydir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(mydir,'..'))
os.chdir(mydir)

import zipfile
import zipfile_ppmd

info7z  = subprocess.check_output(['7z', 'i'])
avail7z = {
    zipfile.ZIP_STORED:    True,
    zipfile.ZIP_DEFLATED:  b'    40108 Deflate' in info7z,
    zipfile.ZIP_BZIP2:     b'    40202 BZip2'   in info7z,
    zipfile.ZIP_LZMA:      b'    30101 LZMA'    in info7z,
    # zipfile.ZIP_ZSTANDARD: b'  4F71101 ZSTD'    in info7z,
    # zipfile.ZIP_XZ:        b'       21 LZMA2'   in info7z,
    zipfile.ZIP_PPMD:      b'    30401 PPMD'    in info7z,
}

params = [
    ('data/10000SalesRecords.csv', zipfile.ZIP_STORED, 0),
    ('data/10000SalesRecords.csv', zipfile.ZIP_DEFLATED, 6),
    ('data/10000SalesRecords.csv', zipfile.ZIP_BZIP2, 9),
    ('data/10000SalesRecords.csv', zipfile.ZIP_LZMA, 6),
    # ('data/10000SalesRecords.csv', zipfile.ZIP_ZSTANDARD, 3),
    # ('data/10000SalesRecords.csv', zipfile.ZIP_XZ, 6),
    ('data/10000SalesRecords.csv', zipfile.ZIP_PPMD, 5),
]

@pytest.mark.parametrize('fname,method,level',params)
def test_zipfile_writeread(fname,method,level):
    st = os.stat(fname)
    with open(fname, 'rb') as f:
        body = f.read()
        sha256 = hashlib.sha256(body).hexdigest()
    
    with TemporaryDirectory() as tmpdir:
        kwargs = {'compression': method}
        if 'compresslevel' in signature(zipfile._get_compressor).parameters:
            kwargs['compresslevel'] = level
        with zipfile.ZipFile(os.path.join(tmpdir, 'test.zip'), 'w', **kwargs) as zip:
            zip.write(fname)
        if avail7z[method]:
            subprocess.check_call(['7z', 't', os.path.join(tmpdir, 'test.zip')], shell=False)
        with zipfile.ZipFile(os.path.join(tmpdir, 'test.zip'), 'r') as zip:
            info = zip.getinfo(fname)
            assert info.compress_type == method
            dec = zip.read(info)
            len(dec) == st.st_size
            hashlib.sha256(dec).hexdigest() == sha256

@pytest.mark.parametrize('fname,method,level',params)
def test_zipfile_open(fname,method,level):
    st = os.stat(fname)
    with open(fname, 'rb') as f:
        body = f.read()
        sha256 = hashlib.sha256(body).hexdigest()
    
    with TemporaryDirectory() as tmpdir:
        kwargs = {'compression': method}
        if 'compresslevel' in signature(zipfile._get_compressor).parameters:
            kwargs['compresslevel'] = level
        with zipfile.ZipFile(os.path.join(tmpdir, 'test.zip'), 'w', **kwargs) as zip:
            with zip.open(fname, 'w') as zf:
                zf.write(body)
        if avail7z[method]:
            subprocess.check_call(['7z', 't', os.path.join(tmpdir, 'test.zip')], shell=False)
        with zipfile.ZipFile(os.path.join(tmpdir, 'test.zip'), 'r') as zip:
            info = zip.getinfo(fname)
            assert info.compress_type == method
            with zip.open(info, 'r') as zf:
                dec = zf.read()
            len(dec) == st.st_size
            hashlib.sha256(dec).hexdigest() == sha256
