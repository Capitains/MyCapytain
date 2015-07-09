from setuptools import setup, find_packages

setup(
  name='MyCapytain',
  version='0.0.1',
  description='Abstraction of CTS API for Python',
  url='http://github.com/Capitains/MyCapytain',
  author='Thibault Clerice',
  author_email='leponteineptique@gmail.com',
  license='MIT',
  packages=find_packages(),
  install_requires=[
    "requests==2.7.0",
    "six==1.9.0",
    "lxml==3.4.4"
  ],
  tests_require=[
    "mock==1.0.1",
    "xmlunittest"
  ],
  extras_require = {
    "DOC" : ["Sphinx==1.3.1"]
  },
  test_suite="tests",
  zip_safe=False
)
