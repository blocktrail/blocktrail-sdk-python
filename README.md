BlockTrail Python SDK
=====================
This is the BlockTrail Python SDK. This SDK contains methods for easily interacting with the BlockTrail API.
Below are examples to get you started. For additional examples, please see our official documentation
at https://www.blocktrail.com/api/docs/lang/python

[![Latest Stable Version](https://badge.fury.io/py/blocktrail-sdk.svg)](https://pypi.python.org/pypi/blocktrail-sdk)
[![Build Status](https://travis-ci.org/blocktrail/blocktrail-sdk-python.png?branch=master)](https://travis-ci.org/blocktrail/blocktrail-sdk-python)

IMPORTANT! FLOATS ARE EVIL!!
----------------------------
As is best practice with financial data, The API returns all values as an integer, the Bitcoin value in Satoshi's.

The BlockTrail SDK has some easy to use functions to do this for you, we recommend using these
and we also **strongly** recommend doing all Bitcoin calculation and storing of data in integers
and only convert to/from Bitcoin float values for displaying it to the user.

```php
import blocktrail

print "123456789 Satoshi to BTC: ", blocktrail.to_btc(123456789)
print "1.23456789 BTC to Satoshi: ", blocktrail.to_satoshi(1.23456789)
```

A bit more about this can be found [in our documentation](https://www.blocktrail.com/api/docs/lang/python#api_coin_format).

Installation
------------
You can install the package through Pypi (https://pypi.python.org/pypi/blocktrail-sdk).
```
$ pip install blocktrail-sdk
```

or you can use setuptools
```
$ python setup.py build
$ python setup.py install
```

Dependancies
------------
The following dependancies are required:
 - httpsig
 - pycrypto
 - requests

Usage
-----
Please visit our official documentation at https://www.blocktrail.com/api/docs/lang/python for the usage.

Support and Feedback
--------------------
Be sure to visit the BlockTrail API official [documentation website](https://www.blocktrail.com/api/docs/lang/python)
for additional information about our API.

If you find a bug, please submit the issue in Github directly.
[BlockTrail-PHP-SDK Issues](https://github.com/blocktrail/blocktrail-sdk-python/issues)

As always, if you need additional assistance, drop us a note at
[support@blocktrail.com](mailto:support@blocktrail.com).

Unit Tests
----------
Unit Tests are created with PyUnit and can be ran with `python setup.py test`

License
-------
The BlockTrail Python SDK is released under the terms of the MIT license. See LICENCE.md for more information or see http://opensource.org/licenses/MIT.

