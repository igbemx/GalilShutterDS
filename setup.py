#!/usr/bin/env python3 
from setuptools import setup, find_packages
<<<<<<< HEAD
setup(name = "GalilShutter",
    version = "1.0.2",
=======
setup(name = "GalilShutterDS",
    version = "1.0.3",
>>>>>>> dd29cf6c4e27881fbe785bda5275f3fe232a8f76
    description = "Device server for the Galil motion controller based shutter at Softimax",
    author = "Igor Beinik",
    author_email = "igor.beinik@maxiv.lu.se",
    license = "GPLv3",
    url = "http://www.maxiv.lu.se",
    packages = find_packages(),
    install_requires = ['pytango',],
    entry_points={'console_scripts': ['SoftiGalilShutterDS = GalilShutter.GalilShutterDS:main',],}
    )


