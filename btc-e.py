'''
Api Key - Desc: fett_data
Key: X55OV0F6-V8K3P7DI-DPTL4AYT-X5KMIHXN-MWD8CQEX
Secret: a9bb4673675865ee85e1fdc0986ac5aa34c3e2d58bdc01d64e7d192c5822f967
'''

import errno
import warnings
from Cookie import CookieError, SimpleCookie
from decimal import Decimal
from hashlib import sha512 as _sha512
from hmac import new as hmacnew
from httplib import HTTPException, BadStatusLine, HTTPSConnection
from json import loads as jsonloads
from re import search as research
from socket import error as SocketError
from urllib import urlencode
from zlib import MAX_WBITS as _MAX_WBITS
from zlib import decompress as _zdecompress
 
API_REFRESH = 3    #: refresh time of the API [sec]
COMPRESSION = None        #: connection compression
CONN_TIMEOUT = 60         #: connection timeout [sec]
CF_COOKIE = '__cfduid'    #: CloudFlare security cookie
PARSE_FLOAT = Decimal    #: function for JSON float values
PARSE_INT = Decimal      #: function for JSON integer values
 
 
class APIError(Exception):
    "Raise exception when the BTC-E API returned an error."
    pass
 
class CloudFlare(HTTPException):
    "Raise exception when the CloudFlare returned an error."
    pass
 
 
class BTCEConnection(object):
    """BTC-E Public/Trade API persistent HTTPS connection.
   @cvar conn: shared connection between class instances
   @cvar resp: response to the latest connection request"""
 
    conn = None    #: type 'httplib.HTTPSConnection'
    resp = None    #: type 'httplib.HTTPResponse'
 
    _headers = {    #: common HTTPS headers
        'Accept': 'application/json',
        'Accept-Charset': 'utf-8',
        'Accept-Encoding': 'identity',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        }
    _post_headers = {    #: common + POST headers
        'Content-Type': 'application/x-www-form-urlencoded',
        }
 
    @classmethod
    def __init__(cls, compr=COMPRESSION, timeout=CONN_TIMEOUT):
        """Initialization of the shared HTTPS connection.
       @param compr: HTTPS compression (default: identity)
       @param timeout: connection timeout (max: 60 sec)
       @note: class based 'compr' and 'timeout' arguments"""
 
        if compr is False:
            compr = 'identity'
        elif compr is True:
            compr = 'gzip, deflate'
 
        if not cls.conn:
            # Create a new connection.
            cls.conn = HTTPSConnection(
                    'btc-e.com', strict=True, timeout=timeout)
            cls._post_headers.update(cls._headers)
        elif timeout != cls.conn.timeout:
            # update: connection timeout
            cls.conn.timeout = timeout
            cls.conn.close()
 
        if compr and (compr != cls._headers['Accept-Encoding']):
            # update: connection compression
            cls._headers['Accept-Encoding'] = compr
            cls._post_headers.update(cls._headers)
            cls.conn.close()
 
    @classmethod
    def _signature(cls, apikey, encoded_params):
        """Calculation of the SHA-512 authentication signature.
       @param apikey: Trade API-Key {'Key': 'KEY', 'Secret': 'SECRET'}
       @param encoded_params: Trade API method and parameters"""
 
        signature = hmacnew(apikey['Secret'],
                            msg=encoded_params, digestmod=_sha512)
 
        cls._post_headers['Key'] = apikey['Key']
        cls._post_headers['Sign'] = signature.hexdigest()
 
    @classmethod
    def _cfcookie(cls):
        """Get the CloudFlare cookie and update security.
       @raise RuntimeWarning: where no CloudFlare cookie"""
 
        cookie_header = cls.resp.getheader('Set-Cookie')
 
        try:
            cf_cookie = SimpleCookie(cookie_header)[CF_COOKIE]
        except (CookieError, KeyError):
            # warn/failback: use the previous cookie
            if 'Cookie' not in cls._headers.iterkeys():
                warnings.warn("Missing CloudFlare security cookie",
                              category=RuntimeWarning, stacklevel=2)
        else:
            cls._post_headers['Cookie'] = \
                    cls._headers['Cookie'] = cf_cookie.OutputString('value')
 
    @classmethod
    def _decompress(cls, data):
        """Decompress a connection response.
       @return: decompressed data <type 'str'>"""
 
        encoding = cls.resp.getheader('Content-Encoding')
 
        if encoding == 'gzip':
            data = _zdecompress(data, _MAX_WBITS+16)
        elif encoding == 'deflate':
            data = _zdecompress(data, -_MAX_WBITS)
        # else/failback: the 'identity' encoding
        return data
 
    @classmethod
    def jsonrequest(cls, url, apikey=None, **params):
        """Create a query to the BTC-E API (with JSON response).
       @raise httplib.HTTPException, socket.error: connection errors
       @param url: Public/Trade API plain URL without parameters
       @param apikey: Trade API Key {'Key': 'KEY', 'Secret': 'SECRET'}
       @param **params: Public/Trade API method and/or parameters
       @return: BTC-E API response (JSON data) <type 'str'>"""
 
        if apikey:
            # args: Trade API
            http_method = 'POST'
            encoded_params = urlencode(params)
            cls._signature(apikey, encoded_params)
            headers = cls._post_headers
        else:
            # args: Public API
            http_method = 'GET'
            if params:
                url = '{}?{}'.format(url, urlencode(params))
            encoded_params = None
            headers = cls._headers
 
        while True:
            # Make a HTTPS request.
            try:
                cls.conn.request(http_method, url,
                                 body=encoded_params, headers=headers)
                cls.resp = cls.conn.getresponse()
            except HTTPException as error:
                cls.conn.close()
                if not isinstance(error, BadStatusLine):
                    raise    # HTTPS exceptions
            except SocketError as error:
                cls.conn.close()
                if error.errno != errno.ECONNRESET:    #: != connection reset
                    raise    # SSL/Socket exceptions
            else:
                cls._cfcookie()
                break    # The connection succeeded.
        return cls._decompress(cls.resp.read())
 
    @classmethod
    def apirequest(cls, url, apikey=None, **params):
        """Create a query to the BTC-E API (decode response).
       @raise APIError, CloudFlare: BTC-E and CloudFlare errors
       @param url: Public/Trade API plain URL without parameters
       @param apikey: Trade API Key {'Key': 'KEY', 'Secret': 'SECRET'}
       @param **params: Public/Trade API method and/or parameters
       @return: BTC-E API response (decoded data) <type 'dict'>"""
 
        jsondata = cls.jsonrequest(url, apikey, **params)
 
        try:
            data = jsonloads(jsondata,
                             parse_float=PARSE_FLOAT, parse_int=PARSE_INT)
        except ValueError:
            if cls.resp.status != 200:    #: != status OK
                # CloudFlare proxy errors
                raise CloudFlare("{0.status} {0.reason}".format(cls.resp))
            raise APIError(jsondata)    # BTC-E API unknown errors
        else:
            if 'error' in data:
                raise APIError(data['error'])    # BTC-E API standard errors
        return data
 
class PublicAPIv3(BTCEConnection):
    """\
   BTC-E Public API v3 <https://btc-e.com/api/3/docs>."""
 
    def __init__(self, *pairs, **connkw):
        """Initialization of the BTC-E Public API v3.
       @param *pairs: [btc_usd[-btc_rur[-...]]] or arguments
       @param **connkw: ... (see: 'BTCEConnection' class)"""
 
        self.pairs = pairs    #: type 'str' (delimiter: '-')
 
        super(PublicAPIv3, self).__init__(**connkw)
 
        # Get the all pairs of the BTC-E API.
        if not self.pairs:
            self.pairs = self.call('info')['pairs'].iterkeys()
 
        if not isinstance(self.pairs, str):
            self.pairs = '-'.join(self.pairs)
 
    def call(self, method, **params):
        """Create a query to the BTC-E Public API v3.
       @param method: info | ticker | depth | trades
       @param **params: limit=150 (max: 2000), ignore_invalid=1
       @return: ... (see: online documentation) <type 'dict'>"""
 
        if method == 'info':
            url = '/api/3/{}'.format(method)
        else:    # method: ticker, depth, trades
            url = '/api/3/{}/{}'.format(method, self.pairs)
        return self.apirequest(url, **params)
 
class TradeAPIv1(BTCEConnection):
    """\
   BTC-E Trade API v1 <https://btc-e.com/tapi/docs>."""
 
    def __init__(self, apikey, **connkw):
        """Initialization of the BTC-E Trade API v1.
       @raise APIError: where no 'invalid nonce' in error
       @param apikey: Trade API Key {'Key': 'KEY', 'Secret': 'SECRET'}
       @param **connkw: ... (see: 'BTCEConnection' class)"""
 
        self._apikey = apikey    #: type 'dict' (keys: 'Key', 'Secret')
        self._nonce = None       #: type 'int' (min/max: 1 to 4294967294)
 
        super(TradeAPIv1, self).__init__(**connkw)
 
        # Get the nonce parameter from the BTC-E API.
        try:
            self.apirequest('/tapi', self._apikey, nonce=self._nonce)
        except APIError as error:
            if 'invalid nonce' not in error.message:
                raise    # BTC-E API errors
            self._nonce = int(research(r'\d+', error.message).group())
 
    def _nextnonce(self):
        """Increase the nonce POST parameter.
       @return: next nonce parameter <type 'int'>"""
 
        self._nonce += 1
        return self._nonce
 
    def call(self, method, **params):
        """Create a query to the BTC-E Trade API v1.
       @param method: getInfo | Trade | ActiveOrders | OrderInfo |
           CancelOrder | TradeHistory (max: 2000) | TransHistory (max: 2000) |
           WithdrawCoin | CreateCoupon | RedeemCoupon
       @param **params: param1=value1, param2=value2, ..., paramN=valueN
       @return: ... (see: online documentation) <type 'dict'>"""
 
        params['method'] = method
        params['nonce'] = self._nextnonce()
        return self.apirequest('/tapi', self._apikey, **params)['return']
RAW Paste Data

# coding: utf-8
# python: 2.7.3
# module: btcelib.py <http://pastebin.com/kABSEyYB>

"""BTC-E Trade API v1 and BTC-E Public API v3

The MIT License (MIT) <http://opensource.org/licenses/MIT>.
Copyright (c) 2014-2015, John Saturday <stozher@gmail.com>.

THE BTC-E IS NOT AFFILIATED WITH THIS PROJECT. THIS IS A COMPLETELY
INDEPENDENT IMPLEMENTATION BASED ON THE ONLINE BTC-E API DESCRIPTION:

    BTC-E Public API v3 <https://btc-e.com/api/3/docs>
    BTC-E Trade API v1 <https://btc-e.com/tapi/docs>

EXAMPLE:
    >>> import btcelib
    >>> from pprint import pprint
    >>> papi = btcelib.PublicAPIv3('btc_usd-ltc_xxx')
    >>> data = papi.call('ticker', ignore_invalid=1)
    >>> pprint(data)
    >>> # The next instance used the same connection...
    >>> apikey = {    # Replace with your API-Key/Secret!
    ...     'Key': 'YOUR-KEY',
    ...     'Secret': 'YOUR-SECRET',
    ...     }
    >>> tapi = btcelib.TradeAPIv1(apikey, compr=True)
    >>> data = tapi.call('TradeHistory', pair='btc_usd', count=2)
    >>> pprint(data)

CLASSES:
    __builtin__.object
        BTCEConnection
            PublicAPIv3
            TradeAPIv1
    exceptions.Exception(exceptions.BaseException)
        APIError
    httplib.HTTPException(exceptions.Exception)
        CloudFlare

class btcelib.BTCEConnection([compr=None[, timeout=60]]):
    BTC-E Public/Trade API persistent HTTPS connection.

    BTCEConnection.apirequest(url[, apikey=None[, **params]]):
        Create a query to the BTC-E API (decode response).
    BTCEConnection.jsonrequest(url[, apikey=None[, **params]]):
        Create a query to the BTC-E API (w/ JSON response).

    BTCEConnection.conn - shared connection between class instances
    BTCEConnection.resp - response to the latest connection request

class btcelib.PublicAPIv3([*pairs[, **connkw]]):
    BTC-E Public API v3 (see: online documentation).

    PublicAPIv3.call(method[, **params]):
        Create a query to the BTC-E Public API v3.
        method: info | ticker | depth | trades
        params: limit=150 (max: 2000), ignore_invalid=1

class btcelib.TradeAPIv1(apikey[, **connkw]):
    BTC-E Trade API v1 (see: online documentation).

    TradeAPIv1.call(method[, **params]):
        Create a query to the BTC-E Trade API v1.
        method: getInfo | Trade | ActiveOrders | OrderInfo |
                CancelOrder | TradeHistory (max: 2000) |
                TransHistory (max: 2000) | WithdrawCoin |
                CreateCoupon | RedeemCoupon
        params: param1=value1, param2=value2, ..., paramN=valueN

EXCEPTIONS:
    btcelib.APIError, btcelib.CloudFlare
    also raise: httplib.HTTPException, socket.error

exception btcelib.APIError(exceptions.Exception):
    Raise exception when the BTC-E API returned an error.

exception btcelib.CloudFlare(httplib.HTTPException):
    Raise exception when the CloudFlare returned an error."""


import errno
import warnings
from Cookie import CookieError, SimpleCookie
from decimal import Decimal
from hashlib import sha512 as _sha512
from hmac import new as hmacnew
from httplib import HTTPException, BadStatusLine, HTTPSConnection
from json import loads as jsonloads
from re import search as research
from socket import error as SocketError
from urllib import urlencode
from zlib import MAX_WBITS as _MAX_WBITS
from zlib import decompress as _zdecompress

API_REFRESH = 2    #: refresh time of the API [sec]

COMPRESSION = None        #: connection compression
CONN_TIMEOUT = 60         #: connection timeout [sec]
CF_COOKIE = '__cfduid'    #: CloudFlare security cookie

PARSE_FLOAT = Decimal    #: function for JSON float values
PARSE_INT = Decimal      #: function for JSON integer values


class APIError(Exception):
    "Raise exception when the BTC-E API returned an error."
    pass

class CloudFlare(HTTPException):
    "Raise exception when the CloudFlare returned an error."
    pass


class BTCEConnection(object):
    """BTC-E Public/Trade API persistent HTTPS connection.
    @cvar conn: shared connection between class instances
    @cvar resp: response to the latest connection request"""

    conn = None    #: type 'httplib.HTTPSConnection'
    resp = None    #: type 'httplib.HTTPResponse'

    _headers = {    #: common HTTPS headers
        'Accept': 'application/json',
        'Accept-Charset': 'utf-8',
        'Accept-Encoding': 'identity',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        }
    _post_headers = {    #: common + POST headers
        'Content-Type': 'application/x-www-form-urlencoded',
        }

    @classmethod
    def __init__(cls, compr=COMPRESSION, timeout=CONN_TIMEOUT):
        """Initialization of the shared HTTPS connection.
        @param compr: HTTPS compression (default: identity)
        @param timeout: connection timeout (max: 60 sec)
        @note: class based 'compr' and 'timeout' arguments"""

        if compr is False:
            compr = 'identity'
        elif compr is True:
            compr = 'gzip, deflate'

        if not cls.conn:
            # Create a new connection.
            cls.conn = HTTPSConnection(
                    'btc-e.com', strict=True, timeout=timeout)
            cls._post_headers.update(cls._headers)
        elif timeout != cls.conn.timeout:
            # update: connection timeout
            cls.conn.timeout = timeout
            cls.conn.close()

        if compr and (compr != cls._headers['Accept-Encoding']):
            # update: connection compression
            cls._headers['Accept-Encoding'] = compr
            cls._post_headers.update(cls._headers)
            cls.conn.close()

    @classmethod
    def _signature(cls, apikey, encoded_params):
        """Calculation of the SHA-512 authentication signature.
        @param apikey: Trade API-Key {'Key': 'KEY', 'Secret': 'SECRET'}
        @param encoded_params: Trade API method and parameters"""

        signature = hmacnew(apikey['Secret'],
                            msg=encoded_params, digestmod=_sha512)

        cls._post_headers['Key'] = apikey['Key']
        cls._post_headers['Sign'] = signature.hexdigest()

    @classmethod
    def _cfcookie(cls):
        """Get the CloudFlare cookie and update security.
        @raise RuntimeWarning: where no CloudFlare cookie"""

        cookie_header = cls.resp.getheader('Set-Cookie')

        try:
            cf_cookie = SimpleCookie(cookie_header)[CF_COOKIE]
        except (CookieError, KeyError):
            # warn/failback: use the previous cookie
            if 'Cookie' not in cls._headers.iterkeys():
                warnings.warn("Missing CloudFlare security cookie",
                              category=RuntimeWarning, stacklevel=2)
        else:
            cls._post_headers['Cookie'] = \
                    cls._headers['Cookie'] = cf_cookie.OutputString('value')

    @classmethod
    def _decompress(cls, data):
        """Decompress a connection response.
        @return: decompressed data <type 'str'>"""

        encoding = cls.resp.getheader('Content-Encoding')

        if encoding == 'gzip':
            data = _zdecompress(data, _MAX_WBITS+16)
        elif encoding == 'deflate':
            data = _zdecompress(data, -_MAX_WBITS)
        # else/failback: the 'identity' encoding
        return data

    @classmethod
    def jsonrequest(cls, url, apikey=None, **params):
        """Create a query to the BTC-E API (with JSON response).
        @raise httplib.HTTPException, socket.error: connection errors
        @param url: Public/Trade API plain URL without parameters
        @param apikey: Trade API Key {'Key': 'KEY', 'Secret': 'SECRET'}
        @param **params: Public/Trade API method and/or parameters
        @return: BTC-E API response (JSON data) <type 'str'>"""

        if apikey:
            # args: Trade API
            http_method = 'POST'
            encoded_params = urlencode(params)
            cls._signature(apikey, encoded_params)
            headers = cls._post_headers
        else:
            # args: Public API
            http_method = 'GET'
            if params:
                url = '{}?{}'.format(url, urlencode(params))
            encoded_params = None
            headers = cls._headers

        while True:
            # Make a HTTPS request.
            try:
                cls.conn.request(http_method, url,
                                 body=encoded_params, headers=headers)
                cls.resp = cls.conn.getresponse()
            except HTTPException as error:
                cls.conn.close()
                if not isinstance(error, BadStatusLine):
                    raise    # HTTPS exceptions
            except SocketError as error:
                cls.conn.close()
                if error.errno != errno.ECONNRESET:    #: != connection reset
                    raise    # SSL/Socket exceptions
            else:
                cls._cfcookie()
                break    # The connection succeeded.
        return cls._decompress(cls.resp.read())

    @classmethod
    def apirequest(cls, url, apikey=None, **params):
        """Create a query to the BTC-E API (decode response).
        @raise APIError, CloudFlare: BTC-E and CloudFlare errors
        @param url: Public/Trade API plain URL without parameters
        @param apikey: Trade API Key {'Key': 'KEY', 'Secret': 'SECRET'}
        @param **params: Public/Trade API method and/or parameters
        @return: BTC-E API response (decoded data) <type 'dict'>"""

        jsondata = cls.jsonrequest(url, apikey, **params)

        try:
            data = jsonloads(jsondata,
                             parse_float=PARSE_FLOAT, parse_int=PARSE_INT)
        except ValueError:
            if cls.resp.status != 200:    #: != status OK
                # CloudFlare proxy errors
                raise CloudFlare("{0.status} {0.reason}".format(cls.resp))
            raise APIError(jsondata)    # BTC-E API unknown errors
        else:
            if 'error' in data:
                raise APIError(data['error'])    # BTC-E API standard errors
        return data

class PublicAPIv3(BTCEConnection):
    """\
    BTC-E Public API v3 <https://btc-e.com/api/3/docs>."""

    def __init__(self, *pairs, **connkw):
        """Initialization of the BTC-E Public API v3.
        @param *pairs: [btc_usd[-btc_rur[-...]]] or arguments
        @param **connkw: ... (see: 'BTCEConnection' class)"""

        self.pairs = pairs    #: type 'str' (delimiter: '-')

        super(PublicAPIv3, self).__init__(**connkw)

        # Get the all pairs of the BTC-E API.
        if not self.pairs:
            self.pairs = self.call('info')['pairs'].iterkeys()

        if not isinstance(self.pairs, str):
            self.pairs = '-'.join(self.pairs)

    def call(self, method, **params):
        """Create a query to the BTC-E Public API v3.
        @param method: info | ticker | depth | trades
        @param **params: limit=150 (max: 2000), ignore_invalid=1
        @return: ... (see: online documentation) <type 'dict'>"""

        if method == 'info':
            url = '/api/3/{}'.format(method)
        else:    # method: ticker, depth, trades
            url = '/api/3/{}/{}'.format(method, self.pairs)
        return self.apirequest(url, **params)

class TradeAPIv1(BTCEConnection):
    """\
    BTC-E Trade API v1 <https://btc-e.com/tapi/docs>."""

    def __init__(self, apikey, **connkw):
        """Initialization of the BTC-E Trade API v1.
        @raise APIError: where no 'invalid nonce' in error
        @param apikey: Trade API Key {'Key': 'KEY', 'Secret': 'SECRET'}
        @param **connkw: ... (see: 'BTCEConnection' class)"""

        self._apikey = apikey    #: type 'dict' (keys: 'Key', 'Secret')
        self._nonce = None       #: type 'int' (min/max: 1 to 4294967294)

        super(TradeAPIv1, self).__init__(**connkw)

        # Get the nonce parameter from the BTC-E API.
        try:
            self.apirequest('/tapi', self._apikey, nonce=self._nonce)
        except APIError as error:
            if 'invalid nonce' not in error.message:
                raise    # BTC-E API errors
            self._nonce = int(research(r'\d+', error.message).group())

    def _nextnonce(self):
        """Increase the nonce POST parameter.
        @return: next nonce parameter <type 'int'>"""

        self._nonce += 1
        return self._nonce

    def call(self, method, **params):
        """Create a query to the BTC-E Trade API v1.
        @param method: getInfo | Trade | ActiveOrders | OrderInfo |
            CancelOrder | TradeHistory (max: 2000) | TransHistory (max: 2000) |
            WithdrawCoin | CreateCoupon | RedeemCoupon
        @param **params: param1=value1, param2=value2, ..., paramN=valueN
        @return: ... (see: online documentation) <type 'dict'>"""

        params['method'] = method
        params['nonce'] = self._nextnonce()
        return self.apirequest('/tapi', self._apikey, **params)['return']
