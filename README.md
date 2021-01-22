# Count Versions
This script spiders through an S3 or S3 compatible bucket looking for
 versions of a objects. For any object that has multiple versions, it spits
 out the name of the object and the number of objects found.
  
## Pre-requisites
This scripts requires: 

yaml
```
pip install pyyaml
```

requests
```
pip install requests
```

## Config
Configuration is stored in two places. 

config.yaml, which needs to be in the working directory.
```yaml
awsprofile: 'b2'
bucket    : ''
host      : 's3.us-west-001.backblazeb2.com'
region    : 'us-west-001'
```

AWS CLI credentials file. It needs be found in ~/.aws/credentials. The
 `awsprofile` found in config.yaml needs to match a profile in the
  credentials file. For example:
  
```ini
[b2]
aws_access_key_id = 001**************
aws_secret_access_key = K00*************
``` 

## Running the script
```bash
$ python start.py
```
