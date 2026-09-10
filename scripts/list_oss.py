#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, sys
import oss2

AccessKeyId = os.environ.get("OSS_ACCESS_KEY_ID", "")
AccessKeySecret = os.environ.get("OSS_ACCESS_KEY_SECRET", "")
Endpoint = os.environ.get("OSS_ENDPOINT", "oss-cn-beijing.aliyuncs.com")
Bucket = os.environ.get("OSS_BUCKET", "")
Prefix = os.environ.get("OSS_PREFIX", "")

if not (AccessKeyId and AccessKeySecret and Bucket and Prefix):
    print("缺少环境变量：OSS_ACCESS_KEY_ID / OSS_ACCESS_KEY_SECRET / OSS_BUCKET / OSS_PREFIX", file=sys.stderr)
    sys.exit(1)

auth = oss2.Auth(AccessKeyId, AccessKeySecret)
bucket = oss2.Bucket(auth, Endpoint, Bucket)

total_size = 0
total_count = 0
for obj in oss2.ObjectIterator(bucket, prefix=Prefix):
    total_count += 1
    total_size += obj.size
    print(f"{obj.size}\t{obj.key}\t{obj.etag}")

print(f"\nTOTAL_COUNT={total_count}", file=sys.stderr)
print(f"TOTAL_SIZE={total_size} ({total_size/1024/1024/1024:.2f} GB)", file=sys.stderr)
