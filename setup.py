from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in big_bash_event/__init__.py
from big_bash_event import __version__ as version

setup(
	name="big_bash_event",
	version=version,
	description="it is for big bash event",
	author="Quantbit Technologies PVT LTD",
	author_email="contact@erpdata.in",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
