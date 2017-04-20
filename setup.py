#!usr/bin/env python

from setuptools import setup, find_packages

setup(name="capy",
	version="0.1",
	description="capy package",
	url="https://github.com/mkome/capy",
	packages=find_packages(),
	entry_points="""
	[console_scripts]
	capy = capy.capy:main
	""",
	)
