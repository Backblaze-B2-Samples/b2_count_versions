from __future__ import print_function
# Author: Nilay Patel

# Python Imports

import subprocess
import json
import os
import sys

# Tools Imports

import requests
from io import BytesIO

# Project Imports

def ping_test(hostname):
    '''
    This function pings a host for 30 seconds and averages the response time.
    :param hostname: hostname to ping
    :return: the average response time, in ms
    '''

    cmd = ['ping', '-c', '30', hostname]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    p.wait()

    output = ''
    err = ''

    for line in p.stderr:
        err = err + line

    for line in p.stdout:
        output = output + line

    output_array = [s.strip() for s in output.splitlines()]

    # If there's an error - bail.

    time = 0
    status_code = 0

    if err:
        time = 0
        status_code = 100
    else:

        ping_count = 0
        ping_time = 0.0
        packet_loss = 0

        for element in output_array:
            if element.startswith('64 bytes'):
                ping_count = ping_count + 1
                left, right = element[7:].split('time=')
                ping_time = ping_time + float(right[:-3])
            elif element.find('packets transmitted') > 0:

                # Found the summary line. Note that the format of this line
                # is different on Mac vs. Linux, of course

                # Linux:
                # 30 packets transmitted, 30 received, 0% packet loss, time 29034ms
                # Mac:
                # 5 packets transmitted, 5 packets received, 0.0% packet loss
                # I'm gonna resort to using uname. Ugh.

                host_os = os.uname()[0]

                if host_os == 'Darwin':
                    packet_loss = int(element.split(', ')[2].split('.')[0])
                if host_os == 'Linux':
                    packet_loss = int(element.split(', ')[2].split('%')[0])

        if ping_count == 0:
            time = 0
        else:
            time = ping_time / ping_count

        status_code = packet_loss

    return time, status_code

def postUrlPyCurl(url, headers={}, data=""):
    '''
    Post via PyCurl. There are better performance timing counters in PyCurl
    then requests. Docs that describe how pycurl work are:
    https://blog.cloudflare.com/a-question-of-timing/ (not pycurl, but curl)
    https://netbeez.net/blog/http-transaction-timing-breakdown-with-curl/
    https://stackoverflow.com/questions/744532/getting-ttfb-time-till-first-byte-for-an-http-request
    http://pycurl.io/docs/latest/index.html
    https://stackoverflow.com/questions/31826814/curl-post-request-into-pycurl-code

    :param url: url to fetch.
    :param http_verb: The http verb. Support GET and POST.
    :param headers: dictionary of headers to pass with the request (
    optional)
    :param params: dictionary of parameters to pass with the request (
    optional)
    :param data: data to be posted with the request (optional)
    :return: HTTP response, formatted as Python dictionary, elapsed time in
    seconds of the round trip, HTTP status code
    '''

    # Convert headers dictionary to the format
    # that pycurl requires.

    headers_as_array = []
    for item in headers.items():
        headers_as_array.append(item[0] + ': ' + item[1])

    try:

        buffer = BytesIO()

        c = pycurl.Curl()
        c.setopt(pycurl.URL, url)
        c.setopt(pycurl.POST, 1)
        c.setopt(pycurl.POSTFIELDS, data)
        c.setopt(c.HTTPHEADER, headers_as_array)
        c.setopt(c.WRITEDATA, buffer)

        content = c.perform()  # execute

        # Body is a byte string.
        # We have to know the encoding in order to print it to a text file
        # such as standard output.
        # http://pycurl.io/docs/latest/quickstart.html

        body = buffer.getvalue().decode('iso-8859-1')

        dns_time = c.getinfo(pycurl.NAMELOOKUP_TIME)  # DNS time
        conn_time = c.getinfo(pycurl.CONNECT_TIME)  # TCP/IP 3-way handshaking time
        app_conn_time = c.getinfo(pycurl.APPCONNECT_TIME)
        pretransfer_time = c.getinfo(pycurl.PRETRANSFER_TIME)
        starttransfer_time = c.getinfo(pycurl.STARTTRANSFER_TIME)  # time-to-first-byte time
        total_time = c.getinfo(pycurl.TOTAL_TIME)  # last requst time
        status_code = c.getinfo((pycurl.RESPONSE_CODE)) # status code

        c.close()

        data = {}
        data['dns_time']           = dns_time
        data['conn_time']          = conn_time
        data['app_conn_time']      = app_conn_time
        data['pretransfer_time']   = pretransfer_time
        data['starttransfer_time'] = starttransfer_time
        data['total_time']         = total_time
        data['status_code']        = status_code

        result = json.loads(body)
        return result, data

        '''
        # TODO: Check response status. If auth token fails, go retrieve

        result = json.loads(response.content)
        return result, response.elapsed.total_seconds(),\
               response.status_code
        '''
    except ValueError as e:
        print ('JSON decoding failed.', file=sys.stderr)
        print (url, file=sys.stderr)
        print ('status code: ' + str(data['status_code']), file=sys.stderr)
        print ('response content: ' + body, file=sys.stderr)
        print (e, file=sys.stderr)

        result = json.loads('[]')
        return result, data

    except pycurl.error as e:
        print('HTTP POST Request failed', file=sys.stderr)
        print(url, file=sys.stderr)
        print(e, file=sys.stderr)
        result = json.loads('[]')

        nulldata = {}

        nulldata['dns_time'] = -1
        nulldata['conn_time'] = -1
        nulldata['app_conn_time'] = -1
        nulldata['pretransfer_time'] = -1
        nulldata['starttransfer_time'] = -1
        nulldata['total_time'] = -1
        nulldata['status_code'] = -1

        return result, nulldata

def fetchUrl(url, http_verb, headers={}, params={}, data=""):
    '''
    Fetch URL. If the connection fails, it return a status 900 that will find
    it's way back to appengine. This is useful for debugging purposes.
    :param url: url to fetch.
    :param http_verb: The http verb. Support GET and POST.
    :param headers: dictionary of headers to pass with the request (
    optional)
    :param params: dictionary of parameters to pass with the request (
    optional)
    :param data: data to be posted with the request (optional)
    :return: HTTP response, formatted as Python dictionary, elapsed time in
    seconds of the round trip, HTTP status code
    '''

    if http_verb == 'GET':
        try:
            response = requests.get(
                url=url,
                params=params,
                headers=headers,
            )
            result = json.loads(response.content)
            return result, response.elapsed.total_seconds(), \
                   response.status_code

            # TODO: Check response status. If auth token fails, go retrieve
            # a new one and try this fetch again.

        except requests.exceptions.RequestException as e:
            print('HTTP GET Request failed', file=sys.stderr)
            print(url, file=sys.stderr)
            print(e, file=sys.stderr)

            result = json.loads('[]')
            return result, 0, 900

    elif http_verb == 'POST':
        try:
            response = requests.post(
                url=url,
                headers=headers,
                data=json.dumps(data)
            )

            # TODO: Check response status. If auth token fails, go retrieve

            result = json.loads(response.content)
            return result, response.elapsed.total_seconds(),\
                   response.status_code
        except ValueError as e:
            print ('JSON decoding failed.', file=sys.stderr)
            print (url, file=sys.stderr)
            print ('status code: ' + str(response.status_code), file=sys.stderr)
            print (response.content, file=sys.stderr)
            print (e, file=sys.stderr)

            result = json.loads('[]')
            return result, response.elapsed.total_seconds(),\
                   response.status_code

        except requests.exceptions.RequestException as e:
            print('HTTP POST Request failed', file=sys.stderr)
            print(url, file=sys.stderr)
            print(e, file=sys.stderr)

            result = json.loads('[]')
            return result, 0, 900

    elif http_verb == 'PUT':
        try:
            response = requests.put(
                url=url,
                headers=headers,
                data=data
            )

            # TODO: Check response status. If auth token fails, go retrieve
            # a new one and try this fetch again. In nothing else,
            # when an error occurs, it should complain.

            result = response.content

            return result, response.elapsed.total_seconds(),\
                   response.status_code
        except requests.exceptions.RequestException as e:
            print('HTTP PUT Request failed', file=sys.stderr)
            print(url, file=sys.stderr)
            print(e, file=sys.stderr)

            return "", 0, 900

    elif http_verb == 'DELETE':
        try:
            response = requests.delete(
                url=url,
                headers=headers,
            )

            # TODO: Check response status. If auth token fails, go retrieve
            # a new one and try this fetch again. In nothing else,
            # when an error occurs, it should complain.

            result = response.content

            return result, response.elapsed.total_seconds(),\
                   response.status_code
        except requests.exceptions.RequestException as e:
            print('HTTP DELETE Request failed', file=sys.stderr)
            print(url, file=sys.stderr)
            print(e, file=sys.stderr)

            return "", 0, 900