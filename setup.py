from setuptools import setup, find_packages

import MyCapytain

setup(
  name='MyCapytain',
  version=MyCapytain.__version__,
  description='Library for CTS APIs and CapiTainS guidelines in Python',
  url='http://github.com/Capitains/MyCapytain',
  author='Thibault Clerice',
  author_email='leponteineptique@gmail.com',
  license='Mozilla Public License Version 2.0',
  packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
  install_requires=[
    "requests>=2.8.1",
    "six>=1.10.0",
    "lxml>=3.6.4",
    "future>=0.16.0",
    "rdflib-jsonld>=0.4.0"
  ],
  tests_require=[
    "mock>=2.0.0",
    "responses>=0.8.1",
    "xmlunittest>=0.3.2"
  ],
  extras_require={
    "DOC": ["Sphinx==1.3.1"]
  },
  test_suite="tests",
  zip_safe=False,
  classifiers=[
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Developers",
    "Intended Audience :: Education",
    "Intended Audience :: Information Technology",
    "Intended Audience :: Science/Research",
    "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
    "Topic :: Software Development :: Libraries",
    "Topic :: Text Processing :: Markup :: XML",
    "Topic :: Text Processing :: General"
  ]
)
