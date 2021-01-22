import boto3
from awsv4signature import awsv4sig

aws = awsv4sig()
versions = aws.get_bucket_contents_versions()

for version in versions:
    object = version.get()
    print(object.get('VersionId'))
    print('next...')