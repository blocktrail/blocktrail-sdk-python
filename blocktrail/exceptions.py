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
