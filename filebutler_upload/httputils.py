from functools import partial
from httplib import HTTPConnection, HTTPSConnection
from itertools import chain
from urlparse import urlparse

import multipart


def request(method, url, data, headers, callback=None):
    url = urlparse(url)

    # Connect
    if url.scheme == 'https':
        request = HTTPSConnection(url.netloc)
    else:
        request = HTTPConnection(url.netloc)

    request.connect()

    # Initiate request
    request.putrequest(method, url.path)

    encoded_data = multipart.encode(data)
    encoded_data_headers = encoded_data.get_headers()
    all_headers = chain(
        encoded_data_headers.iteritems(),
        headers.iteritems()
    )

    # Send headers
    for name, value in all_headers:
        request.putheader(name, value)

    request.endheaders()

    # Send body
    bytes_sent = 0
    bytes_total = int(encoded_data_headers['Content-Length'])
    for chunk in encoded_data:
        request.send(chunk)
        bytes_sent += len(chunk)

        if callable(callback):
            callback(bytes_sent, bytes_total)

    # TODO: Wrap the response in a container to allow chunked reading.
    response = request.getresponse()

    response_status = response.status
    response_data = response.read()

    request.close()

    return response_status, response_data

get = partial(request, 'GET')
post = partial(request, 'POST')
