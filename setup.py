#!/usr/bin/env python3.6
from setuptools import setup, find_packages

setup(
    name="tangods-softimax-galilshutter",
    use_scm_version=True,
    setup_requires=["setuptools_scm"],
    description="Device server for the Galil motion controller based shutter at Softimax",
    author="Igor Beinik",
    author_email="igor.beinik@maxiv.lu.se",
    url="https://gitlab.maxiv.lu.se/igobei/tangods-softimax-galilshutter",
    packages=find_packages(exclude=["tests", "*.tests.*", "tests.*", "scripts"]),
    install_requires=['pytango', ],
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'SoftiGalilShutter = SoftiGalilShutter.SoftiGalilShutter:main',
        ],
    },
)
