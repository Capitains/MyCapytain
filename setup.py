from setuptools import setup

setup(name='MyCapytain',
      version='0.1.0',
      description='Abstraction of CTS API for Python',
      url='http://github.com/Capitains/MyCapytain',
      author='Thibault Clerice',
      author_email='leponteineptique@gmail.com',
      license='MIT',
      packages=['MyCapytain'],
      install_requires=[
        "requests==2.7.0",
        "lxml==3.4.4"
      ],
      tests_require=[
        "mock==1.0.1"
      ],
      extras_require = {
        "DOC" : ["Sphinx==1.3.1"]
      },
      zip_safe=False)
