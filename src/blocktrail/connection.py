import hashlib
import datetime
import requests

import blocktrail
from httpsig.requests_auth import HTTPSignatureAuth
from requests.models import RequestEncodingMixin


EXCEPTION_INVALID_CREDENTIALS = "Your credentials are incorrect."
EXCEPTION_GENERIC_HTTP_ERROR = "An HTTP Error has occurred!"
EXCEPTION_GENERIC_SERVER_ERROR = "An Server Error has occurred!"
EXCEPTION_EMPTY_RESPONSE = "The HTTP Resone was empty."
EXCEPTION_UNKNOWN_ENDPOINT_SPECIFIC_ERROR = "The endpoint returned an unknown error."
EXCEPTION_MISSING_ENDPOINT = "The endpoint you've tried to access does not exist. Check your URL."
EXCEPTION_OBJECT_NOT_FOUND = "The object you've tried to access does not exist."


class RestClient(object):
    def __init__(self, api_endpoint, api_key, api_secret):
        self.api_endpoint = api_endpoint

        self.default_headers = {
            'User-Agent': "%s/%s" % (blocktrail.SDK_USER_AGENT, blocktrail.SDK_VERSION)
        }

        self.default_params = {
            'api_key': api_key
        }

        self.auth = HTTPSignatureAuth(key_id=api_key, secret=api_secret, algorithm='hmac-sha256',
                                      headers=['(request-target)', 'Date', 'Content-MD5'])

    def get(self, endpoint_url, auth=None):
        if auth is True:
            auth = self.auth

        headers = self.default_headers.copy().update({
            'Date': RestClient.httpdate(datetime.datetime.utcnow()),
            'Content-MD5': RestClient.content_md5("")
        })

        params = self.default_params.copy()

        response = requests.get(self.api_endpoint + endpoint_url, params=params, headers=headers, auth=auth)

        return RestClient.handle_response(response)

    def post(self, endpoint_url, data, auth=None):
        if auth is True:
            auth = self.auth

        # do the post body encoding here since we need it to get the MD5
        data = RequestEncodingMixin._encode_params(data)

        headers = self.default_headers.copy().update({
            'Date': RestClient.httpdate(datetime.datetime.utcnow()),
            'Content-MD5': RestClient.content_md5(data)
        })

        params = self.default_params.copy()

        response = requests.post(self.api_endpoint + endpoint_url, data=data, params=params, headers=headers, auth=auth)

        return RestClient.handle_response(response)

    @classmethod
    def handle_response(cls, response):
        if response.status_code == 200:
            if len(response.content) == 0:
                raise EmptyResponse(EXCEPTION_EMPTY_RESPONSE)

            return response
        elif response.status_code == 400 or response.status_code == 403:
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
        return hashlib.md5(content).hexdigest()

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


class BlockTrailSDKException(Exception):

    def __init__(self, msg, code=None):
        self.msg = msg
        self.code = code

    def __str__(self):
        if self.code:
            return "[%d] %s" % (self.code, self.msg)
        else:
            return self.msg


class InvalidFormat(BlockTrailSDKException):
    pass


class EmptyResponse(BlockTrailSDKException):
    pass


class EndpointSpecificError(BlockTrailSDKException):
    pass


class UnknownEndpointSpecificError(BlockTrailSDKException):
    pass


class InvalidCredentials(BlockTrailSDKException):
    pass


class MissingEndpoint(BlockTrailSDKException):
    pass


class ObjectNotFound(BlockTrailSDKException):
    pass


class GenericHTTPError(BlockTrailSDKException):
    pass


class GenericServerError(BlockTrailSDKException):
    pass
