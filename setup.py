from setuptools import setup, find_packages

import MyCapytain

setup(
  name='MyCapytain',
  version=MyCapytain.__version__,
  description='Abstraction of CTS API for Python',
  url='http://github.com/Capitains/MyCapytain',
  author='Thibault Clerice',
  author_email='leponteineptique@gmail.com',
  license='MIT',
  packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
  install_requires=[
    "requests==2.7.0",
    "six==1.9.0",
    "lxml==3.4.4",
    "future==0.15.2"
  ],
  tests_require=[
    "mock==1.3.0",
    "xmlunittest==0.3.2"
  ],
  extras_require = {
    "DOC" : ["Sphinx==1.3.1"]
  },
  test_suite="tests",
  dependency_links=[
    "https://github.com/Ponteineptique/python-xmlunittest/tarball/master#egg=xmlunittest-0.3.2"
  ],
  zip_safe=False
)
