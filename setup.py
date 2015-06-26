from setuptools import setup

import sys
if sys.version_info[0] == 3 and sys.version_info[1] == 2:
    print("Sorry, Python 3.2 is not supported")
    print("Only supported version are 2.7, 3.3 and 3.4")
    sys.exit(1)

setup(
    name='blocktrail-sdk-beta',
    version='1.0.6',
    description="BlockTrail's Developer Friendly Bitcoin SDK",
    long_description="""\
BlockTrail's Developer Friendly Bitcoin SDK

 - simple bindings to the various data API endpoints
    - block data and transactions
    - transaction data
    - address data and transactions
    - latest price
 - Contains Multi-Signature HD Wallet

For examples and instructions on how to use, please see our official documentation at https://www.blocktrail.com/api/docs/lang/python
""",
    keywords=["bitcoin", "sdk", "api", "payments", "crypto", "wallet", "multisig", "multisignature", "HD wallet"],
    maintainer='Ruben de Vries',
    maintainer_email='ruben@blocktrail.com',
    url='https://www.blocktrail.com/api/docs/lang/python',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License'
    ],
    packages=["blocktrail"],
    install_requires=[
        'httpsig-cffi == 15.0.0',
        'requests >= 2.4.3, < 2.5',
        'future >= 0.14.3, < 0.15',
        'six >= 1.9.0',
        'pycoin == 0.52',
        'python-bitcoinlib == 0.2.1',
        'mnemonic == 0.12'
    ],
    test_suite="tests.get_tests",
)
