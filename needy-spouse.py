#/usr/env/python3

# needy-spouse
# uses the Sinch API to mass call a list of numbers

import requests

try:
    import urllib.request as urllib2
except ImportError:
    import urllib2

import json
import base64

class SinchCall(object):

    """ A class for handling communication with the Sinch REST apis. """

    CALL_URL = 'https://callingapi.sinch.com/v1/callouts'
    #CHECK_STATUS_URL = 'https://messagingApi.sinch.com/v1/message/status/'

    def __init__(self, app_key, app_secret):
        """Create a SinchCall client with the provided app_key and app_secret.

           Visit your dashboard at sinch.com to locate your application key and secret.
           These can be found under apps/credentials section.
        """
        b64bytes = base64.b64encode(('application:%s:%s' % (app_key, app_secret)).encode())
        self._auth = 'basic %s' % b64bytes.decode('ascii')

    def _request(self, url, values=None):
        """ Send a request and read response.

            Sends a get request if values are None, post request otherwise.
        """
        if values:
            json_data = json.dumps(values)
            request = urllib2.Request(url, json_data.encode())
            request.add_header('content-type', 'application/json')
            request.add_header('authorization', self._auth)
            connection = urllib2.urlopen(request)
            response = connection.read()
            connection.close()
        else:
            request = urllib2.Request(url)
            request.add_header('authorization', self._auth)
            connection = urllib2.urlopen(request)
            response = connection.read()
            connection.close()

        try:
            result = json.loads(response.decode())
        except ValueError as exception:
            return {'errorCode': 1, 'message': str(exception)}

        return result

    def call(self, to_number, message, from_number=None):
        """ Send a message to the specified number and return a response dictionary.

            The numbers must be specified in international format starting with a '+'.
            Returns a dictionary that contains a 'MessageId' key with the sent message id value or
            contains 'errorCode' and 'message' on error.

            Possible error codes:
                 40001 - Parameter validation
                 40002 - Missing parameter
                 40003 - Invalid request
                 40100 - Illegal authorization header
                 40200 - There is not enough funds to send the message
                 40300 - Forbidden request
                 40301 - Invalid authorization scheme for calling the method
                 50000 - Internal error
        """

        values = {'method': 'ttsCallout', 'ttsCallout': {'destination': {'type': 'number', 'endpoint': to_number}, 'text': message}}

        return self._request(self.CALL_URL, values)

def _main():
    """ A simple demo to be used from command line. """
    import sys
    import argparse
    import fileinput
    import random

    parser = argparse.ArgumentParser()
    parser.add_argument('--key', help='API key')
    parser.add_argument('--secret', help='API secret')
    parser.add_argument('--numbers', metavar='FILE', required=True, help='file(s) with numbers to call')
    parser.add_argument('--messages', metavar='FILE', required=True, help='file(s) with messages')
    args = parser.parse_args()

    key = args.key
    secret = args.secret
    numbers = open(args.numbers,'r').read().splitlines()
    messages = open(args.messages,'r').read().splitlines()

    for number in numbers:
	    message = random.choice(messages)
	    client = SinchCall(key, secret)
	    print('Calling {0} with the message "{1}": {2}'.format(number, message, client.call(number, message)))
    
    sys.exit(0)

if __name__ == '__main__':
    _main()
