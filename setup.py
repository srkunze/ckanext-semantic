from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(
	name='ckanext-semantic',
	version=version,
	description="semantic extension that uses lodstats and add personalization features based on it",
	long_description="""\
	""",
	classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
	keywords='',
	author='Sven R. Kunze',
	author_email='',
	url='',
	license='',
	packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
	namespace_packages=['ckanext', 'ckanext.semantic'],
	include_package_data=True,
	zip_safe=False,
	install_requires=[
		# -*- Extra requirements: -*-
	],
	entry_points=\
	"""
        [ckan.plugins]
        semantic=ckanext.semantic.plugin:LODstatsPlugin

        [paste.paster_command]
        semantic=ckanext.semantic.commands:LODStatsExtCommand
	""",
)
