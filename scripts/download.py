#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, sys, time
import oss2
from concurrent.futures import ThreadPoolExecutor, as_completed

# 凭据与目标目录均通过环境变量注入，避免硬编码敏感信息
AK = os.environ.get("OSS_ACCESS_KEY_ID", "")
SK = os.environ.get("OSS_ACCESS_KEY_SECRET", "")
EP = os.environ.get("OSS_ENDPOINT", "oss-cn-beijing.aliyuncs.com")
BK = os.environ.get("OSS_BUCKET", "")
PREFIX = os.environ.get("OSS_PREFIX", "")
LOCAL_ROOT = os.environ.get("LOCAL_ROOT", "")

if not (AK and SK and BK and PREFIX and LOCAL_ROOT):
    print("缺少环境变量：OSS_ACCESS_KEY_ID / OSS_ACCESS_KEY_SECRET / OSS_BUCKET / OSS_PREFIX / LOCAL_ROOT", file=sys.stderr)
    sys.exit(1)

auth = oss2.Auth(AK, SK)
bucket = oss2.Bucket(auth, EP, BK)

def list_objects():
    return [o for o in oss2.ObjectIterator(bucket, prefix=PREFIX)]

def download_one(obj):
    rel = obj.key[len(PREFIX):]
    if rel == "":
        return "SKIP(empty) " + obj.key
    local = os.path.join(LOCAL_ROOT, rel.replace("/", os.sep))
    os.makedirs(os.path.dirname(local), exist_ok=True)
    # skip if already complete by size
    if os.path.exists(local) and os.path.getsize(local) == obj.size:
        return "SKIP " + rel
    # resume
    start = 0
    mode = "wb"
    if os.path.exists(local):
        cur = os.path.getsize(local)
        if cur < obj.size:
            start = cur
            mode = "ab"
        else:
            start = 0
            mode = "wb"
    headers = {}
    if start:
        headers["Range"] = f"bytes={start}-"
    resp = bucket.get_object(obj.key, headers=headers)
    downloaded = start
    t0 = time.time()
    last = start
    with open(local, mode) as f:
        for chunk in iter(lambda: resp.read(1024 * 1024), b""):
            f.write(chunk)
            downloaded += len(chunk)
            now = time.time()
            if now - t0 >= 15:
                speed = (downloaded - last) / (now - t0) / 1024 / 1024
                last = downloaded
                t0 = now
                pct = downloaded * 100.0 / obj.size
                print(f"[{pct:5.1f}%] {downloaded/2**30:.2f}/{obj.size/2**30:.2f} GB  {speed:6.1f} MB/s  {rel}", flush=True)
    # final size check
    if os.path.getsize(local) != obj.size:
        return f"INCOMPLETE {rel} (got {os.path.getsize(local)}, want {obj.size})"
    return "DONE " + rel

def main():
    objs = list_objects()
    print(f"TOTAL_OBJECTS={len(objs)}", flush=True)
    total = sum(o.size for o in objs)
    print(f"TOTAL_SIZE={total/2**30:.2f} GB", flush=True)
    with ThreadPoolExecutor(max_workers=6) as ex:
        futs = [ex.submit(download_one, o) for o in objs]
        for fu in as_completed(futs):
            try:
                print(fu.result(), flush=True)
            except Exception as e:
                print(f"ERROR {e}", flush=True)
    print("ALL_FINISHED", flush=True)

if __name__ == "__main__":
    main()
