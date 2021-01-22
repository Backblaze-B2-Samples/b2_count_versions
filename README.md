# Count Versions
This script spiders through a B2 bucket looking for
 versions of a objects. For any object that has multiple versions, it spits
 out the name of the object and the number of objects found. It also returns
  the total number of files and the total number of file versions that are
   found in the bucket.
  
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
Configuration is stored in config.yaml.

```yaml
bucketName : 'homelab-findingnilay-veeam'
keyid      : '[add keyId here]'
appkey     : '[add appkey here]'
apiVersion : '/b2api/v2/'
```

## Running the script
```bash
$ python start.py
```
