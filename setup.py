from setuptools import setup

import sys
if sys.version_info[0] == 3 and sys.version_info[1] == 2:
    print("Sorry, Python 3.2 is not supported")
    print("Only supported version are 2.7, 3.3 and 3.4")
    sys.exit(1)

setup(
    name='blocktrail-sdk',
    version='1.0.6',
    description="BlockTrail's Developer Friendly API binding for Python",
    long_description='This package allows interacting with the BlockTrail API',
    maintainer='Ruben de Vries',
    maintainer_email='ruben@blocktrail.com',
    url='https://www.blocktrail.com/api/docs/lang/python',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'License :: OSI Approved :: MIT License'
    ],
    packages=["blocktrail"],
    install_requires=[
        'httpsig >= 1.1.0',
        'pycrypto >= 2.6.1',
        'requests >= 2.4.3',
        'future >= 0.14.3',
        'six >= 1.9.0',
    ],
    test_suite="tests.get_tests",
)
