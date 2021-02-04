# Count Versions

This script spiders through a B2 bucket looking for
versions of a objects. For any object that has multiple versions, it spits
out the name of the object and the number of objects found. It also returns
each object's MD5 and upload timestamp in milliseconds from Epoch. You can
use https://currentmillis.com/ to convert this number to a datetime. 

It also returns
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
bucketName : '[bucket name here]'
keyid      : '[add keyId here]'
appkey     : '[add appkey here]'
apiVersion : '/b2api/v2/'
```

## Running the script
```bash
$ python start.py
```

## Sample output (from a real bucket with Veeam data)
```
$ ./start.py 
Files where more than one version exists: 
	md5, uploadtimestamp for each object

 ... [tons of entries omitted for brevity] ...

filename: Veeam/Archive/VeeamPrimarySOBR/6845f524-dd79-44fa-b85a-e83df2f7162b/00000000-0000-0000-0000-000000000000/blocks/3c66fded328d769cfd63ef624ff6dbcb/12809.5f07b8547637068915b1fe23591f8db9.00000000000000000000000000000000.blk
	md5: 8c45923363a1a81dc8bdcbfadfb04423, upload timestamp: 1602805287000
	md5: 8c45923363a1a81dc8bdcbfadfb04423, upload timestamp: 1602805255000
filename: Veeam/Archive/VeeamPrimarySOBR/6845f524-dd79-44fa-b85a-e83df2f7162b/00000000-0000-0000-0000-000000000000/blocks/3c66fded328d769cfd63ef624ff6dbcb/190.6ef3de16f9f38d7a929d3c45f5246596.00000000000000000000000000000000.blk
	md5: daaca9e6a489d61d7e8a119f7ef06320, upload timestamp: 1602805177000
	md5: daaca9e6a489d61d7e8a119f7ef06320, upload timestamp: 1602805145000
filename: Veeam/Archive/VeeamPrimarySOBR/6845f524-dd79-44fa-b85a-e83df2f7162b/00000000-0000-0000-0000-000000000000/blocks/3c66fded328d769cfd63ef624ff6dbcb/34852.08f7cf2d0c71d369bb3c16f6fd86093d.00000000000000000000000000000000.blk
	md5: 72c03abac85928488636641e0830110f, upload timestamp: 1602805325000
	md5: 72c03abac85928488636641e0830110f, upload timestamp: 1602805294000
filename: Veeam/Archive/VeeamPrimarySOBR/6845f524-dd79-44fa-b85a-e83df2f7162b/00000000-0000-0000-0000-000000000000/blocks/3c66fded328d769cfd63ef624ff6dbcb/39051.eb325b315901f59a5a54c18dfaf783b3.00000000000000000000000000000000.blk
	md5: a167a8595a858b42cf4e5d4cfd92f449, upload timestamp: 1602805328000
	md5: a167a8595a858b42cf4e5d4cfd92f449, upload timestamp: 1602805296000
filename: Veeam/Archive/VeeamPrimarySOBR/6845f524-dd79-44fa-b85a-e83df2f7162b/00000000-0000-0000-0000-000000000000/blocks/3c66fded328d769cfd63ef624ff6dbcb/47247.8a9d85f279be809517a8efd6c58a1f90.00000000000000000000000000000000.blk
	md5: 614868fe0e36b669fef632d4bd77f432, upload timestamp: 1602805329000
	md5: 614868fe0e36b669fef632d4bd77f432, upload timestamp: 1602805298000
filename: Veeam/Archive/VeeamPrimarySOBR/6845f524-dd79-44fa-b85a-e83df2f7162b/00000000-0000-0000-0000-000000000000/blocks/3c66fded328d769cfd63ef624ff6dbcb/53281.78d6fb3c2d3324871d8cda02fd2e1d50.00000000000000000000000000000000.blk
	md5: cdb9424babec3e49bf48c1a04c1dd85d, upload timestamp: 1602805364000
	md5: cdb9424babec3e49bf48c1a04c1dd85d, upload timestamp: 1602805332000
filename: Veeam/Archive/VeeamPrimarySOBR/6845f524-dd79-44fa-b85a-e83df2f7162b/00000000-0000-0000-0000-000000000000/blocks/3c66fded328d769cfd63ef624ff6dbcb/6419.aeddd8aeb7d90e0a20551dc5568bb5a2.00000000000000000000000000000000.blk
	md5: 15a9f8a208726b7682523b8c36c360ed, upload timestamp: 1602805194000
	md5: 15a9f8a208726b7682523b8c36c360ed, upload timestamp: 1602805163000
filename: Veeam/Archive/VeeamPrimarySOBR/6845f524-dd79-44fa-b85a-e83df2f7162b/00000000-0000-0000-0000-000000000000/blocks/3c66fded328d769cfd63ef624ff6dbcb/6489.1efc44084fb99b2b022a442c248faec2.00000000000000000000000000000000.blk
	md5: d57e07bce82400e1291f2d6e583beec5, upload timestamp: 1602805228000
	md5: d57e07bce82400e1291f2d6e583beec5, upload timestamp: 1602805197000
filename: Veeam/Archive/VeeamPrimarySOBR/6845f524-dd79-44fa-b85a-e83df2f7162b/00000000-0000-0000-0000-000000000000/blocks/3c66fded328d769cfd63ef624ff6dbcb/7356.76f7e5206cb91992da9c43067d445614.00000000000000000000000000000000.blk
	md5: c8b57e1b590395c185bf693cb6aa23ae, upload timestamp: 1602805244000
	md5: c8b57e1b590395c185bf693cb6aa23ae, upload timestamp: 1602805210000

Found files with > 1 version count:  397
Total files in bucket:  68777
Total file versions in bucket:  69577
```
