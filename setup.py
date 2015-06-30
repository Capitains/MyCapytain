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
        "requests==2.7.0"
      ],
      zip_safe=False)
