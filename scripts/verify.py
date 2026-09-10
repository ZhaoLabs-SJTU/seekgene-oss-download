#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, hashlib, sys
from concurrent.futures import ThreadPoolExecutor, as_completed

LOCAL_ROOT = os.environ.get("LOCAL_ROOT", "")
MD5FILE = os.environ.get("MD5_FILE", os.path.join(LOCAL_ROOT, "md5.txt"))

if not LOCAL_ROOT:
    print("缺少环境变量 LOCAL_ROOT", file=sys.stderr)
    sys.exit(1)

def parse_md5():
    entries = []
    with open(MD5FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line.strip():
                continue
            parts = line.split()
            md5 = parts[0].lower()
            path = line[len(parts[0]):].strip()
            entries.append((md5, path))
    return entries

def md5_of_file(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024 * 8), b""):
            h.update(chunk)
    return h.hexdigest()

def check_one(entry):
    md5, rel = entry
    local = os.path.join(LOCAL_ROOT, rel.replace("/", os.sep))
    if not os.path.exists(local):
        return ("MISSING", rel, md5, None)
    actual = md5_of_file(local)
    status = "OK" if actual == md5 else "MISMATCH"
    return (status, rel, md5, actual)

def main():
    entries = parse_md5()
    print(f"Total files to verify: {len(entries)}", flush=True)
    ok = 0
    bad = []
    with ThreadPoolExecutor(max_workers=8) as ex:
        futs = [ex.submit(check_one, e) for e in entries]
        for fu in as_completed(futs):
            status, rel, md5, actual = fu.result()
            if status == "OK":
                ok += 1
                print(f"OK     {rel}", flush=True)
            else:
                bad.append((status, rel, md5, actual))
                print(f"{status} {rel} (want {md5}, got {actual})", flush=True)
    print(f"\nVERIFY_RESULT: {ok}/{len(entries)} OK", flush=True)
    if bad:
        print(f"FAILED {len(bad)} files:", flush=True)
        for b in bad:
            print("  ", b, flush=True)
        sys.exit(1)
    else:
        print("ALL_MD5_VERIFIED_OK", flush=True)

if __name__ == "__main__":
    main()
