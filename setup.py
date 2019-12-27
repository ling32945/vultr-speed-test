# coding: utf-8

import os
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
        name = "vultr-speed-test",
        version = "0.1",
        author = "Jae",
        author_email = "ling32945@sina.com",
        description = "speed test for vultr node",
        license = "MIT",
        keywords = ["vultr","speed"],
        url = "https://github.com/ling32945/vultr-speed-test",
        long_description = read('README.md'),
        install_requires=['bs4','requests'],
        packages = ['vultr-speed-test'],
        entry_points={
        'console_scripts': [
            'vultr-speed-test = vultr-speed-test.main:main',
            ]
        },
        classifiers = [
             'Development Status :: 1 - Pre-Alpha',
             'Intended Audience :: Developers',
             'License :: OSI Approved :: MIT License',
             'Programming Language :: Python :: 2.7',
             'Programming Language :: Python :: 3.8',
             'Topic :: Software Development :: Libraries :: Python Modules',
        ]
)

