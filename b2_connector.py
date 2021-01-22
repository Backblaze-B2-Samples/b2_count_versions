from __future__ import print_function
# Author: Nilay Patel

# Python Imports

import base64
import hashlib
import sys
import datetime

# Tools Imports

import yaml

# Project Imports

from library import fetchUrl
from library import postUrlPyCurl

class B2Connector:

    def __init__(self):
        '''
        Initiliaze & load configuration from settings file. Also -
        calls authentication method during initialization so object is ready
        to make requests to B2.
        :return: None
        '''

        settings_file = 'config.yaml'
        with open(settings_file, 'r') as stream:
            settings = yaml.safe_load(stream)

        self.key_id = settings['keyid']
        self.app_key = settings['appkey']
        self.bucket_name = settings['bucketName']
        self.api_version = settings['apiVersion']

        self.apiUrl = ''
        self.authToken = ''
        self.downloadUrl = ''
        self.accountId = ''

        self.authB2()
        self.bucket_id = self.getBucketIdFromName(self.bucket_name)

    def authB2(self):
        '''
        Authentication against B2 using the credentials stored in the
        configuration file. If successful, the return token will be stored in
        the instance of the class for future references.
        :return: None
        '''

        # TODO: Instead of fetching a new auth token each time this class is
        # instantiated, persist the token somewhere (on disk?) and try using
        # it. If it fails, fetch another one.

        auth_string = self.key_id + ':' + self.app_key
        basic_auth_string = 'Basic ' + base64.b64encode(auth_string.encode(
            'ascii')).decode('ascii')

        baseUrl = "https://api.backblaze.com" + self.api_version
        authCmd = "b2_authorize_account"

        url = baseUrl + authCmd

        headers = {}
        headers['Authorization'] = basic_auth_string

        result, elapsed_time, status_code = fetchUrl(url, 'GET',
                                                     headers=headers)
        self.apiUrl = result['apiUrl']
        self.authToken = result['authorizationToken']
        self.downloadUrl = result['downloadUrl']
        self.accountId = result['accountId']

    def getBucketIdFromName(self, bucket_name):
        '''
        Returns a bucket ID from a bucket_name.
        :param bucket_name: bucket_name
        :return: bucketId
        '''

        cmd = "b2_list_buckets"
        url = self.apiUrl + self.api_version + cmd

        headers = {}
        headers['Authorization'] = self.authToken

        params = {}
        params['accountId'] = self.accountId

        result, elapsed_time, status_code = fetchUrl(url, "GET",
                                                     headers=headers,
                                                     params=params)
        for r in result['buckets']:
            if r['bucketName'] == bucket_name:
                return r['bucketId']

    def getUploadFileUrl(self, retry_count):
        '''
        When uploading a file to B2, you first need to ask the central
        authority for a specific pod to upload the file to. You also need an
        upload authToken to upload a file. This method makes that request and
        returns the uploadUrl and authToken.
        :return: A tuple with uploadUrl used to upload a file to B2 and the
        authToken needed to do an upload.
        '''

        # Start the status code at something. 800 is failure. If success,
        # it will change to 200. If not, it will change to something else
        # that will be caught in the error handling.

        status_code = 800

        getUploadUrlCmd = "b2_get_upload_url"
        url = self.apiUrl + self.api_version + getUploadUrlCmd
        params = {}

        params['bucketId'] = self.bucket_id

        headers = {}
        headers['Authorization'] = self.authToken

        result, elapsed_time, status_code = fetchUrl(url, "GET", params=params,
                                                     headers=headers)
        if status_code == 200:
            return result['uploadUrl'], result['authorizationToken']

        else:
            print('Get Upload URL: status code ' + str(status_code),
                  file=sys.stderr)
            print('Retry count: ' + str(retry_count), file=sys.stderr)
            print(url, file=sys.stderr)
            print(params, file=sys.stderr)
            print(result, file=sys.stderr)

            # Try to call getUploadUrl three times. If it doesn't work after
            # that, bail.

            retry_count = retry_count + 1

            if retry_count < 4:
                self.getUploadFileUrl(retry_count)
            else:
                sys.exit(1)

    def uploadFile(self, filename, runfrom):
        '''
        Upload a file to the B2 service using b2_upload_file.
        :param filename: filename
        :return:
        '''

        payload = b""
        payload_sha1_hash = hashlib.sha1()

        with open(filename, 'rb') as file:
            for block in iter(lambda: file.read(65536), b''):
                payload_sha1_hash.update(block)
                payload = payload + block
        payload_sha1_hash = payload_sha1_hash.hexdigest()
        file.close()

        uploadUrl, authToken = self.getUploadFileUrl(0)
        size = len(payload)
        headers = {}

        headers['X-Bz-File-Name'] = filename
        headers['Content-Type'] = 'b2/x-auto'
        headers['X-Bz-Content-Sha1'] = payload_sha1_hash
        headers['Authorization'] = authToken

        timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

        result, data = postUrlPyCurl(uploadUrl, headers, payload)
        self.db.save_performance_stats(timestamp, data, uploadUrl,
                                       self.cluster, 'upload', size, runfrom)

    def list_file_versions(self, bucket_id, max_file_count,
                           next_file, next_file_id):
        '''
        This method calls list_files_versions.
        :param bucket_id: The bucket's id.
        :param max_file_count: The number of file versions to return
        :param next_file: The next file name, if continuing
        :param next_file_id: The next file version, if continuing
        :return: result in dictionary form
        '''

        list_file_versions_api = "b2_list_file_versions"
        url = self.apiUrl + self.api_version + list_file_versions_api
        data = {}

        data['bucketId'] = bucket_id
        data['maxFileCount'] = max_file_count

        if (next_file != '' and next_file_id != ''):
            data['startFileName'] = next_file
            data['startFileId'] = next_file_id

        headers = {}
        headers['Authorization'] = self.authToken

        result, elapsed_time, status_code = fetchUrl(url, "POST", data=data,
                                                     headers=headers)
        return result, status_code

    def output_files_with_multiple_versions(self):
        '''
        This function spiders through a bucket looking for all the files in
        the bucket that contain more than one version. It then outputs that
        file and the number of versions.
        :return:
        '''

        files_map = {}
        total_file_versions = 0
        next_file_name = ''
        next_file_id = ''
        first_run = True

        while ((next_file_name and next_file_id) or first_run):
            first_run = False
            result, status_code = self.list_file_versions(self.bucket_id, 10000,
                                            next_file_name, next_file_id)
            if status_code == 200:
                next_file_name = result['nextFileName']
                next_file_id = result['nextFileId']

                for item in result['files']:
                    total_file_versions = total_file_versions + 1
                    key = item['fileName']
                    if key in files_map:
                        files_map[key] = files_map[key] + 1
                    else:
                        files_map[key] = 1
            else:
                print('Non 200 status code issued.')
                sys.exit()

        # Output all the files with > 1 versions.
        print('Files where more than one version exists: (filename - count)')
        files_with_versions_count = 0
        total_files = 0
        for key, value in files_map.items():
            if(value > 1):
                files_with_versions_count = files_with_versions_count + 1
                print(key + ' - ', value)
            else:
                total_files = total_files + 1

        print('\nFound files with > 1 version count: ', str(files_with_versions_count))
        print('Total files in bucket: ', str(total_files))
        print('Total file versions in bucket: ', str(total_file_versions))