from __future__ import division

SDK_VERSION = "1.0.2"
SDK_USER_AGENT = "blocktrail-sdk-python"

COIN = 100000000
PRECISION = 8
COIN_FORMAT = "%.8f"


def to_satoshi(btc):
    return int("%.0f" % (btc * COIN))


def to_btc(satoshi):
    return COIN_FORMAT % (satoshi / float(COIN))


from blocktrail import connection
from blocktrail import exceptions
from blocktrail.client import APIClient
