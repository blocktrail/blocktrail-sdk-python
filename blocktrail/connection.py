from __future__ import print_function
from future.standard_library import install_aliases
install_aliases()

import datetime
from urllib.parse import urlparse, urlencode
import requests
import json
import hashlib

from httpsig.requests_auth import HTTPSignatureAuth
from requests.models import RequestEncodingMixin

import blocktrail
from blocktrail.exceptions import *


EXCEPTION_INVALID_CREDENTIALS = "Your credentials are incorrect."
EXCEPTION_GENERIC_HTTP_ERROR = "An HTTP Error has occurred!"
EXCEPTION_GENERIC_SERVER_ERROR = "An Server Error has occurred!"
EXCEPTION_EMPTY_RESPONSE = "The HTTP Response was empty."
EXCEPTION_UNKNOWN_ENDPOINT_SPECIFIC_ERROR = "The endpoint returned an unknown error."
EXCEPTION_MISSING_ENDPOINT = "The endpoint you've tried to access does not exist. Check your URL."
EXCEPTION_OBJECT_NOT_FOUND = "The object you've tried to access does not exist."


class RestClient(object):
    def __init__(self, api_endpoint, api_key, api_secret, debug=False):
        """
        :param str      api_endpoint:   the base url to use for all API requests
        :param str      api_key:        the API_KEY to use for authentication
        :param str      api_secret:     the API_SECRET to use for authentication
        :param bool     debug:          print debug information when requests fail
        """
        self.api_endpoint = api_endpoint
        self.debug = debug

        # create a default User-Agent
        self.default_headers = {
            'User-Agent': "%s/%s" % (blocktrail.SDK_USER_AGENT, blocktrail.SDK_VERSION)
        }

        # api_key is always in the query string
        self.default_params = {
            'api_key': api_key
        }

        # prepare HTTP-Signature Auth signer
        self.auth = HTTPSignatureAuth(key_id=api_key, secret=api_secret, algorithm='hmac-sha256',
                                      headers=['(request-target)', 'Date', 'Content-MD5'])

    def get(self, endpoint_url, params=None, auth=None):
        """
        :param str      endpoint_url:   the API endpoint to request
        :param dict     params:         query string params to add
        :param bool     auth:           do HMAC auth
        :rtype: requests.Response
        """
        if auth is True:
            auth = self.auth

        headers = dict_merge(self.default_headers, {
            'Date': RestClient.httpdate(datetime.datetime.utcnow()),
            'Content-MD5': RestClient.content_md5("")
        })

        params = dict_merge(self.default_params, params)

        response = requests.get(self.api_endpoint + endpoint_url, params=params, headers=headers, auth=auth)

        return self.handle_response(response)

    def post(self, endpoint_url, data, params=None, auth=None):
        """
        :param str      endpoint_url:   the API endpoint to request
        :param dict     data:           the POST body
        :param bool     auth:           do HMAC auth
        :rtype: requests.Response
        """
        if auth is True:
            auth = self.auth

        # do the post body encoding here since we need it to get the MD5
        data = json.dumps(data)

        headers = dict_merge(self.default_headers, {
            'Date': RestClient.httpdate(datetime.datetime.utcnow()),
            'Content-MD5': RestClient.content_md5(data),
            'Content-Type': 'application/json'
        })

        params = dict_merge(self.default_params, params)
        response = requests.post(self.api_endpoint + endpoint_url, data=data, params=params, headers=headers, auth=auth)

        return self.handle_response(response)

    def put(self, endpoint_url, data, params=None, auth=None):
        """
        :param str      endpoint_url:   the API endpoint to request
        :param dict     data:           the POST body
        :param bool     auth:           do HMAC auth
        :rtype: requests.Response
        """
        if auth is True:
            auth = self.auth

        # do the post body encoding here since we need it to get the MD5
        data = json.dumps(data)

        headers = dict_merge(self.default_headers, {
            'Date': RestClient.httpdate(datetime.datetime.utcnow()),
            'Content-MD5': RestClient.content_md5(data),
            'Content-Type': 'application/json'
        })

        params = dict_merge(self.default_params, params)
        response = requests.put(self.api_endpoint + endpoint_url, data=data, params=params, headers=headers, auth=auth)

        return self.handle_response(response)

    def delete(self, endpoint_url, data=None, params=None, auth=None):
        """
        :param str      endpoint_url:   the API endpoint to request
        :param dict     data:           the POST body
        :param bool     auth:           do HMAC auth
        :rtype: requests.Response
        """
        if auth is True:
            auth = self.auth

        data = json.dumps(data)

        params = dict_merge(self.default_params, params)

        headers = dict_merge(self.default_headers, {
            'Date': RestClient.httpdate(datetime.datetime.utcnow()),
            'Content-MD5': RestClient.content_md5(urlparse(self.api_endpoint + endpoint_url).path + "?" + urlencode(params)),
            'Content-Type': 'application/json'
        })

        response = requests.delete(self.api_endpoint + endpoint_url, data=data, params=params, headers=headers, auth=auth)

        return self.handle_response(response)

    def handle_response(self, response):
        """
        helper function to handle the response and raise Exceptions

        :param requests.Response   response:    the Response object to handle
        :rtype: requests.Response
        """
        if response.status_code == 200:
            if len(response.content) == 0:
                raise EmptyResponse(EXCEPTION_EMPTY_RESPONSE)

            return response
        elif self.debug:
            print(response.url, response.status_code, response.content)

        if response.status_code == 400 or response.status_code == 403:
            data = response.json()

            if data and data['msg'] and data['code']:
                raise EndpointSpecificError(msg=data['msg'], code=data['code'])
            else:
                raise UnknownEndpointSpecificError(EXCEPTION_UNKNOWN_ENDPOINT_SPECIFIC_ERROR)
        elif response.status_code == 401:
            raise InvalidCredentials(msg=EXCEPTION_INVALID_CREDENTIALS, code=401)
        elif response.status_code == 404:
            if response.reason == "Endpoint Not Found":
                raise MissingEndpoint(msg=EXCEPTION_MISSING_ENDPOINT, code=404)
            else:
                raise ObjectNotFound(msg=EXCEPTION_OBJECT_NOT_FOUND, code=404)
        elif response.status_code == 500:
            raise GenericServerError(msg=EXCEPTION_GENERIC_SERVER_ERROR, code=response.status_code)
        else:
            raise GenericHTTPError(msg=EXCEPTION_GENERIC_HTTP_ERROR, code=response.status_code)

    @classmethod
    def content_md5(cls, content=""):
        return hashlib.md5(content.encode("utf-8")).hexdigest()

    @classmethod
    def httpdate(cls, dt):
        """Return a string representation of a date according to RFC 1123
        (HTTP/1.1).

        The supplied date must be in UTC.
        """
        weekday = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][dt.weekday()]
        month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep",
                 "Oct", "Nov", "Dec"][dt.month - 1]
        return "%s, %02d %s %04d %02d:%02d:%02d GMT" % (weekday, dt.day, month, dt.year, dt.hour, dt.minute, dt.second)


def dict_merge(dict1, dict2):
    dict1 = dict1 if dict1 is not None else {}
    dict2 = dict2 if dict2 is not None else {}

    result = dict1.copy()
    result.update(dict2)

    return result
