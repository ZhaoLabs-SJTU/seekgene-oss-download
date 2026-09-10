#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, sys

LOCAL_ROOT = os.environ.get("LOCAL_ROOT", "")
LIST = os.environ.get("LIST_OBJECTS_FILE", "list_objects.txt")
PREFIX = os.environ.get("OSS_PREFIX", "")

if not LOCAL_ROOT:
    print("缺少环境变量 LOCAL_ROOT", file=sys.stderr)
    sys.exit(1)

def load_objects():
    objs = []
    with open(LIST) as f:
        for line in f:
            line = line.rstrip("\n")
            if not line.strip():
                continue
            parts = line.split(None, 2)
            if len(parts) < 2:
                continue
            size = int(parts[0])
            key = parts[1]
            rel = key.split(PREFIX, 1)[-1] if PREFIX else key
            objs.append((size, rel))
    return objs

def human(n):
    for u in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024:
            return f"{n:.2f} {u}"
        n /= 1024
    return f"{n:.2f} PB"

def bar(frac, width=26):
    filled = int(round(frac * width))
    return "█" * filled + "░" * (width - filled)

def main():
    objs = load_objects()
    total_size = sum(s for s, _ in objs)
    total_count = len(objs)
    rows = []
    done_bytes = 0
    n_done = 0
    n_partial = 0
    n_pending = 0
    for size, rel in objs:
        local = os.path.join(LOCAL_ROOT, rel.replace("/", os.sep))
        cur = os.path.getsize(local) if os.path.exists(local) else 0
        if cur >= size:
            status = "DONE"
            n_done += 1
            cur = size
        elif cur > 0:
            status = "PARTIAL"
            n_partial += 1
        else:
            status = "PENDING"
            n_pending += 1
        done_bytes += cur
        rows.append((size, cur, status, rel))

    order = {"PARTIAL": 0, "PENDING": 1, "DONE": 2}
    rows.sort(key=lambda r: (order[r[2]], -(r[0] - r[1])))

    frac = done_bytes / total_size if total_size else 0
    print("=" * 78)
    print(f"总体进度  {bar(frac)}  {frac*100:6.2f}%   ({human(done_bytes)} / {human(total_size)})")
    print(f"文件统计  完成 {n_done} / {total_count}   进行中 {n_partial}   待下载 {n_pending}")
    print("=" * 78)
    print(f"{'状态':<9}{'已下载':>11}{'总大小':>11}{'进度':>9}  文件")
    print("-" * 78)
    for size, cur, status, rel in rows:
        if status == "DONE":
            pct = "100.0%"
        elif status == "PENDING":
            pct = "0.0%"
        else:
            pct = f"{cur*100.0/size:5.1f}%"
        print(f"{status:<9}{human(cur):>11}{human(size):>11}{pct:>9}  {rel}")
    print("=" * 78)

if __name__ == "__main__":
    main()
