#!/usr/bin/env python3.6
from setuptools import setup, find_packages

setup(
    name="tangods-softimax-galilshutter",
    use_scm_version=True,
    setup_requires=["setuptools_scm"],
    description="Device server for the Galil motion controller based shutter at Softimax",
    author="Igor Beinik",
    author_email="igor.beinik@maxiv.lu.se",
    license="GPLv3",
    url="https://gitlab.maxiv.lu.se/igobei/tangods-softimax-galilshutter",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.6",
    install_requires=['pytango', ],
    entry_points={
        'console_scripts': [
            'SoftiGalilShutterDS = SoftiGalilShutterDS.GalilShutterDS:main',
        ],
    },
)
