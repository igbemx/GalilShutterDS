#!/usr/bin/env python3 
from setuptools import setup, find_packages
setup(name = "GalilShutter",
    version = "1.0.2",
    description = "Device server for the Galil motion controller based shutter at Softimax",
    author = "Igor Beinik",
    author_email = "igor.beinik@maxiv.lu.se",
    license = "GPLv3",
    url = "http://www.maxiv.lu.se",
    package_dir = {'GalilShutter':'src'},
    packages = find_packages(),
    install_requires = ['pytango',],
    entry_points={'console_scripts': ['SoftiGalilShutterDS = GalilShutter.GalilShutterDS:main',],}
    )


