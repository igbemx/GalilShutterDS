#!/usr/bin/env python3 
import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="GalilShutterDS",
    version="1.0.11",
    description="Device server for the Galil motion controller based shutter at Softimax",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Igor Beinik",
    author_email="igor.beinik@maxiv.lu.se",
    license="GPLv3",
    url="https://gitlab.maxiv.lu.se/igobei/tangods-softimax-galilshutter",
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
    install_requires=['pytango', ],
    entry_points={
        'console_scripts': [
            'SoftiGalilShutterDS = GalilShutter.GalilShutterDS:main',
        ],
    },
)
