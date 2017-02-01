'''
See:
http://en.wikipedia.org/wiki/List_of_HTTP_status_codes
'''

class HttpStatusCode(object):
    # 1xx
    CONTINUE = 100
    SWITCHING_PROTOCOLS = 101
    PROCESSING = 102

    # 2xx
    OK = 200
    CREATED = 201
    ACCEPTED = 202
    NON_AUTHORITATIVE_INFORMATION = 203
    NO_CONTENT = 204
    RESET_CONTENT = 205
    PARTIAL_CONTENT = 206
    MULTI_STATUS = 207
    ALREADY_REPORTED = 208
    IM_USED = 226
    
    # 3xx
    MULTIPLE_CHOICES = 300
    MOVED_PERMANENTLY = 301
    FOUND = 302
    SEE_OTHER = 303
    NOT_MODIFIED = 304
    USE_PROXY = 305
    SWITCH_PROXY = 306
    TEMPORARY_REDIRECT = 307
    PERMANENT_REDIRECT = 308
    
    # 4xx
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    PAYMENT_REQUIRED = 402
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    NOT_ACCEPTABLE = 406
    PROXY_AUTHENTICATION_REQUIRED = 407
    REQUEST_TIMEOUT = 408
    CONFLICT = 409
    GONE = 410
    LENGTH_REQUIRED = 411
    PRECONDITION_FAILED = 412
    REQUEST_ENTITY_TOO_LARGE = 413
    REQUEST_URI_TOO_LONG = 414
    UNSUPPORTED_MEDIA_TYPE = 415
    REQUESTED_RANGE_NOT_SATISFIABLE = 416
    EXPECTATION_FAILED = 417
    I_AM_A_TEAPOT = 418
    AUTHENTICATION_TIMEOUT = 419
    METHOD_FAILURE = 420
    ENHANCE_YOUR_CALM = 420
    UNPROCESSABLE_ENTITY = 422
    LOCKED = 423
    FAILED_DEPENDENCY = 424
    UPGRADE_REQUIRED = 426
    PRECONDITION_REQUIRED = 428
    TOO_MANY_REQUESTS = 429
    REQUEST_HEADER_FIELDS_TOO_LARGE = 431
    LOGIN_TIMEOUT = 440
    NO_RESPONSE = 444
    RETRY_WITH = 449
    BLOCKED_BY_WINDOWS_PARENTAL_CONTROLS = 450
    UNAVAILABLE_FOR_LEGAL_REASONS = 451
    REQUEST_HEADER_TOO_LARGE = 494
    CERT_ERROR = 495
    NO_CERT = 496
    HTTP_TO_HTTPS = 497
    TOKEN_EXPIRED_INVALID = 498
    CLIENT_CLOSED_REQUEST = 499
    TOKEN_REQUIRED = 499
    
    # 5xx
    INTERNAL_SERVER_ERROR = 500
    NOT_IMPLEMENTED = 501
    BAD_GATEWAY = 502
    SERVICE_UNAVAILABLE = 503
    GATEWAY_TIMEOUT = 504
    HTTP_VERSION_NOT_SUPPORTED = 505
    VARIANT_ALSO_NEGOTIATES = 506
    INSUFFICIENT_STORAGE = 507
    LOOP_DETECTED = 508
    BANDWIDTH_LIMIT_EXCEEDED = 509
    NOT_EXTENDED = 510
    NETWORK_AUTHENTICATION_REQUIRED = 511
    ORIGIN_ERROR = 520
    WEB_SERVER_IS_DOWN = 521
    CONNECTION_TIMED_OUT = 522
    PROXY_DECLINED_REQUEST = 523
    A_TIMEOUT_OCCURRED = 524
    NETWORK_READ_TIMEOUT_ERROR = 598
    NETWORK_CONNECT_TIMEOUT_ERROR = 599
