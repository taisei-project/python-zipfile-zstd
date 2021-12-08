
import setuptools

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name='zipfile-zstd',
    version="0.0.4",
    author='Andrei Alexeyev',
    author_email='akari@taisei-project.org',
    description='Monkey patch the standard zipfile module to enable Zstandard support',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/taisei-project/python-zipfile-zstd',
    project_urls={
        'Bug Tracker': 'https://github.com/taisei-project/python-zipfile-zstd/issues',
    },
    keywords='zip zipfile zstd zstandard',
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: System :: Archiving',
        'Topic :: System :: Archiving :: Compression',
    ],
    packages=setuptools.find_packages(),
    python_requires=">=3.6",
    install_requires=[
        'zstandard>=0.15.0',
    ],
)

