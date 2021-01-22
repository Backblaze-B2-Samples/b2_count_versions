#!/usr/bin/env python

import requests
from awsv4signature import awsv4sig
import xml.etree.ElementTree as ET

def pretty_print_request(req):
    """
    At this point it is completely built and ready
    to be fired; it is "prepared".

    However pay attention at the formatting used in
    this function because it is programmed to be pretty
    printed and may differ from the actual request.
    """
    print('{}\n{}\r\n{}\r\n\r\n{}'.format(
        '********** REQUEST **********',
        req.method + ' ' + req.url,
        '\r\n'.join('{}: {}'.format(k, v) for k, v in req.headers.items()),
        req.body,
    ))

def print_response(res):
    print('********** RESPONSE **********')
    print('HTTP/1.1 {status_code}\n{headers}\n\n{body}'.format(
        status_code=res.status_code,
        headers='\n'.join('{}: {}'.format(k, v) for k, v in res.headers.items()),
        body=res.content,
    ))

method = 'GET'
objectname = ''
payload = ''
parameters = 'versions=0'

aws = awsv4sig()
auth_header, headers = aws.get_authorization_header(method, objectname,
                                           payload, parameters)

# ************* SEND THE REQUEST *************
request_url = aws.endpoint
if (objectname):
    request_url = request_url + '/' + objectname
if (parameters):
    request_url = request_url + '?' + parameters

req = requests.Request(method, request_url, headers=headers,
                       data=payload)
prepared = req.prepare()
# pretty_print_request(prepared)

s = requests.Session()
r = s.send(prepared)

root = ET.parse(r.text)


print_response(r)