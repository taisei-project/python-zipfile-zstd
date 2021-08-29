# ported from https://github.com/cielavenir/zipfile39/blob/master/test/test_zipfile.py #

import os
import sys
import hashlib
import subprocess
import itertools
import pytest
from tempfile import TemporaryDirectory
from inspect import signature

mydir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(mydir,'..'))
os.chdir(mydir)

import zipfile
import zipfile_zstd

info7z  = subprocess.check_output(['7z', 'i'])
avail7z = {
    zipfile.ZIP_STORED:    True,
    zipfile.ZIP_DEFLATED:  b'    40108 Deflate' in info7z,
    zipfile.ZIP_BZIP2:     b'    40202 BZip2'   in info7z,
    zipfile.ZIP_LZMA:      b'    30101 LZMA'    in info7z,
    zipfile.ZIP_ZSTANDARD: b'  4F71101 ZSTD'    in info7z,
    # zipfile.ZIP_XZ:        b'       21 LZMA2'   in info7z,
    # zipfile.ZIP_PPMD:      b'    30401 PPMD'    in info7z,
}

fnames = [
    'data/10000SalesRecords.csv',
    # 'data/7zz',
]

methods = [
    (zipfile.ZIP_STORED, 0),
    (zipfile.ZIP_DEFLATED, 6),
    (zipfile.ZIP_BZIP2, 9),
    (zipfile.ZIP_LZMA, 6),
    (zipfile.ZIP_ZSTANDARD, 3),
    # (zipfile.ZIP_XZ, 6),
    # (zipfile.ZIP_PPMD, 5),
]

@pytest.mark.parametrize('fname,method,level',[
    tuple([fname]+list(method)) for fname, method in itertools.product(fnames, methods)
])
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

@pytest.mark.parametrize('fname,method,level',[
    tuple([fname]+list(method)) for fname, method in itertools.product(fnames, methods)
])
def test_zipfile_open(fname,method,level):
    chunksiz = 512
    st = os.stat(fname)
    cnt = (st.st_size+chunksiz-1)//chunksiz

    with open(fname, 'rb') as f:
        body = f.read()
        sha256 = hashlib.sha256(body).hexdigest()
    
    with TemporaryDirectory() as tmpdir:
        kwargs = {'compression': method}
        if 'compresslevel' in signature(zipfile._get_compressor).parameters:
            kwargs['compresslevel'] = level
        with zipfile.ZipFile(os.path.join(tmpdir, 'test.zip'), 'w', **kwargs) as zip:
            with zip.open(fname, 'w') as zf:
                for i in range(cnt):
                    zf.write(body[chunksiz*i:chunksiz*(i+1)])
        if avail7z[method]:
            subprocess.check_call(['7z', 't', os.path.join(tmpdir, 'test.zip')], shell=False)
        with zipfile.ZipFile(os.path.join(tmpdir, 'test.zip'), 'r') as zip:
            info = zip.getinfo(fname)
            assert info.compress_type == method
            decsiz = 0
            hashobj = hashlib.sha256()
            with zip.open(info, 'r') as zf:
                while True:
                    dec0 = zf.read(chunksiz)
                    decsiz += len(dec0)
                    hashobj.update(dec0)
                    if len(dec0) < chunksiz:
                        break
                    assert len(dec0) == chunksiz
            assert decsiz == st.st_size
            assert hashobj.hexdigest() == sha256
