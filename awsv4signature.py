#!/usr/bin/env python

import sys, os, datetime, hashlib, hmac, configparser
import yaml
import boto3

class awsv4sig:
    def __init__(self):

        config_file = 'config.yaml'
        with open(config_file, 'r') as stream:
            config = yaml.safe_load(stream)

        # ************* REQUEST VALUES *************
        self.aws_profile = config['awsprofile']
        self.service = 's3'
        self.bucket = config['bucket']
        self.host = self.bucket + '.' + config['hostname']
        self.region = config['region']
        self.endpoint = 'https://' + self.host

        # Read AWS access key from ~/.aws directory
        awsconfig = configparser.ConfigParser()
        awsconfig.read_file(open(os.path.expanduser('~') + '/.aws/credentials'))

        self.access_key = str(awsconfig.get(self.aws_profile, 'aws_access_key_id'))
        self.secret_key = str(awsconfig.get(self.aws_profile, 'aws_secret_access_key'))

        self.s3 = boto3.resource(self.service,
                                 aws_access_key_id=self.access_key,
                                 aws_secret_access_key=self.secret_key,
                                 region_name=self.region,
                                 endpoint_url=self.endpoint)
        print('hello')

    def get_boto3_connection(self):

        return self.s3

    def get_bucket_contents_versions(self):

        return self.s3.Bucket(self.bucket).object_versions.filter()

    def get_authorization_header(self, method, objectname, payload, parameters):

        method = method
        objectname = objectname
        request_payload_file = payload
        request_parameters = parameters

        print('********** INPUTS **********')
        print('AWS Profile Name: %s' % self.aws_profile)
        print('HTTP Method: %s' % method)
        print('AWS Service Name: %s' % self.service)
        print('Host: %s' % self.host)
        print('Region: %s' % self.region)
        print('Endpoint: %s' % self.endpoint)
        print('Objectname: %s' % objectname)
        print('Payload filename: %s' % request_payload_file)
        print('HTTP parameters: %s' % request_parameters)

        # Key derivation functions. See:
        # http://docs.aws.amazon.com/general/latest/gr/signature-v4-examples.html#signature-v4-examples-python

        def getSignatureKey(key, dateStamp, regionName, serviceName):
            kDate = hmac.new(("AWS4" + key).encode("utf-8"), dateStamp.encode('utf-8'), hashlib.sha256).digest()
            kRegion = hmac.new(kDate, regionName.encode('utf-8'), hashlib.sha256).digest()
            kService = hmac.new(kRegion, serviceName.encode('utf-8'), hashlib.sha256).digest()
            kSigning = hmac.new(kService, 'aws4_request'.encode('utf-8'), hashlib.sha256)
            return kSigning.digest()

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

        if self.access_key is None or self.secret_key is None:
            print('No access key is available.')
            sys.exit()

        # Create a date for headers and the credential string
        t = datetime.datetime.utcnow()
        amzdate = t.strftime('%Y%m%dT%H%M%SZ')
        datestamp = t.strftime('%Y%m%d') # Date w/o time, used in credential scope

        # If there is a request body, load the file.
        # It is dumb that I'm reading the file twice.

        request_payload = b""
        if (request_payload_file != ''):
            payload_sha256_hash = hashlib.sha256()

            # Payload SHA-256 hash
            # Create payload hash (hash of the request body content). For GET
            # requests, the payload is an empty string (""). In addition, load the
            # file's content into request_payload to be used later in transmitting the
            # file data.

            with open(request_payload_file, 'rb') as file:
                for block in iter(lambda: file.read(65536), b''):
                    payload_sha256_hash.update(block)
                    request_payload = request_payload + block
            payload_sha256_hash = payload_sha256_hash.hexdigest()
            file.close()

        else:
            payload_sha256_hash = hashlib.sha256(('').encode('utf-8')).hexdigest()

        # ************* TASK 1: CREATE A CANONICAL REQUEST *************
        # http://docs.aws.amazon.com/general/latest/gr/sigv4-create-canonical-request.html

        # Step 1 is to define the verb (GET, POST, etc.)--already done.

        # Step 2: Create canonical URI--the part of the URI from domain to query
        # string (use '/' if no path)
        canonical_uri = '/' + objectname

        # Step 3: Create the canonical query string. In this example (a GET request),
        # request parameters are in the query string. Query string values must
        # be URL-encoded (space=%20). The parameters must be sorted by name.
        # For this example, the query string is pre-formatted in the request_parameters variable.
        canonical_querystring = request_parameters

        # Step 4: Create the canonical headers and signed headers. Header names
        # must be trimmed and lowercase, and sorted in code point order from
        # low to high. Note that there is a trailing \n.
        canonical_headers = 'host:' + self.host + '\n' + \
                            'x-amz-content-sha256:' + payload_sha256_hash + '\n' + \
                            'x-amz-date:' + amzdate + '\n'

        # Step 5: Create the list of signed headers. This lists the headers
        # in the canonical_headers list, delimited with ";" and in alpha order.
        # Note: The request can include any headers; canonical_headers and
        # signed_headers lists those that you want to be included in the
        # hash of the request. "Host" and "x-amz-date" are always required.
        signed_headers = 'host;x-amz-content-sha256;x-amz-date'

        # Step 6: Combine elements to create canonical request
        canonical_request = method + '\n' + canonical_uri + '\n' + \
                            canonical_querystring + '\n' + \
                            canonical_headers + '\n' + signed_headers + '\n' \
                            + payload_sha256_hash
        print('********** CANONICAL REQUEST **********')
        print(canonical_request)

        # ************* TASK 2: CREATE THE STRING TO SIGN*************
        # Match the algorithm to the hashing algorithm you use, either SHA-1 or
        # SHA-256 (recommended)
        algorithm = 'AWS4-HMAC-SHA256'
        credential_scope = datestamp + '/' + self.region + '/' + self.service\
                           + '/' + 'aws4_request'
        string_to_sign = algorithm + '\n' +  amzdate + '\n' + \
                         credential_scope + '\n' +  \
                         hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()
        print('********** STRING TO SIGN **********')
        print(string_to_sign)

        # ************* TASK 3: CALCULATE THE SIGNATURE *************
        # Create the signing key using the function defined above.
        signing_key = getSignatureKey(self.secret_key, datestamp, self.region,
                                      self.service)

        # Sign the string_to_sign using the signing_key
        signature = hmac.new(signing_key,
                             (string_to_sign).encode('utf-8'),
                             hashlib.sha256).hexdigest()
        print('********** SIGNATURE **********')
        print(signature)

        # ************* TASK 4: ADD SIGNING INFORMATION TO THE REQUEST *************
        # The signing information can be either in a query string value or in
        # a header named Authorization. This code shows how to use a header.
        # Create authorization header and add to request headers
        authorization_header = algorithm + ' ' + 'Credential=' + \
                               self.access_key  + '/' + credential_scope + \
                               ', ' +  'SignedHeaders=' + signed_headers + ', '\
                               + 'Signature=' + signature

        # The request can include any headers, but MUST include "host", "x-amz-date",
        # and (for this scenario) "Authorization". "host" and "x-amz-date" must
        # be included in the canonical_headers and signed_headers, as noted
        # earlier. Order here is not significant.
        # Python note: The 'host' header is added automatically by the Python 'requests' library.
        headers = {'x-amz-date':amzdate,
                   'Authorization':authorization_header,
                   'x-amz-content-sha256':payload_sha256_hash}

        print('********** AUTHORIZATION HEADER **********')
        print(authorization_header)

        return authorization_header, headers