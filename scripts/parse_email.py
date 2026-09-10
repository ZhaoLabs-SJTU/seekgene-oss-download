#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从测序服务商「数据释放」邮件(.eml)中提取阿里云 OSS 下载凭据。

用法:
    python3 parse_email.py  <邮件文件.eml>

输出: JSON 格式的 OSS 连接参数 + 邮件元信息。
    {
      "project": "项目编号",
      "access_key_id": "LTAI...",
      "access_key_secret": "...",
      "endpoint": "oss-cn-beijing.aliyuncs.com",
      "bucket": "release-bucket",
      "prefix": "release/temp-.../",
      "release_date": "2026-09-09",
      "expire": "2026-12-08"
    }

说明:
  - 邮件正文通常直接给出 AccessKeyId / AccessKeySecret / Endpoint / Bucket / 路径。
  - 若正文为 HTML, 本脚本会先转成纯文本再匹配, 兼容绝大多数邮件客户端导出的 .eml。
"""
import email
import json
import re
import sys
import html
from email import policy


def extract_text(msg):
    """取出邮件正文, 优先纯文本, 其次 HTML(去标签)。"""
    plain_parts = []
    html_parts = []
    if msg.is_multipart():
        for part in msg.walk():
            ct = part.get_content_type()
            if ct == "text/plain":
                try:
                    plain_parts.append(part.get_content())
                except Exception:
                    pass
            elif ct == "text/html":
                try:
                    html_parts.append(part.get_content())
                except Exception:
                    pass
    else:
        ct = msg.get_content_type()
        try:
            body = msg.get_content()
        except Exception:
            body = ""
        if ct == "text/html":
            html_parts.append(body)
        else:
            plain_parts.append(body)

    text = "\n".join(plain_parts)
    if not text.strip() and html_parts:
        raw = "\n".join(html_parts)
        raw = re.sub(r"<br\s*/?>", "\n", raw, flags=re.I)
        raw = re.sub(r"</p>", "\n", raw, flags=re.I)
        raw = re.sub(r"<[^>]+>", " ", raw)
        text = html.unescape(raw)
    return text


def find_secret(text, key):
    """在文本中按 key=value / key: value / key value 三种形式找值。"""
    patterns = [
        rf"{re.escape(key)}\s*[=:：]\s*([^\s\r\n]+)",
        rf"{re.escape(key)}\s+([A-Za-z0-9/._\-]+)",
    ]
    for p in patterns:
        m = re.search(p, text)
        if m:
            return m.group(1).strip().strip("'\"")
    return None


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    eml_path = sys.argv[1]

    with open(eml_path, "rb") as f:
        msg = email.message_from_binary_file(f, policy=policy.default)

    subject = msg.get("Subject", "")
    date = msg.get("Date", "")
    text = extract_text(msg)

    # 项目编号: 常见 SGS + 8 位数字（按实际服务商格式调整）
    project = None
    m = re.search(r"SGS\d{6,}", subject + "\n" + text)
    if m:
        project = m.group(0)

    # 有效期: 常见 "有效期至 2026-12-08" / "数据保留 90 天"
    expire = None
    m = re.search(r"20\d{2}[-/.]\d{1,2}[-/.]\d{1,2}", text)
    if m:
        expire = m.group(0).replace("/", "-").replace(".", "-")

    # AccessKeyId 通常以 LTAI 开头
    ak = None
    m = re.search(r"LTAI[A-Za-z0-9]{12,}", text)
    if m:
        ak = m.group(0)
    if not ak:
        ak = find_secret(text, "AccessKeyId") or find_secret(text, "AccessKey ID")

    sk = find_secret(text, "AccessKeySecret") or find_secret(text, "AccessKey Secret")

    ep = None
    m = re.search(r"oss-cn-[a-z]+\.aliyuncs\.com", text)
    if m:
        ep = m.group(0)
    if not ep:
        ep = find_secret(text, "Endpoint")

    bucket = find_secret(text, "Bucket")

    # 路径前缀: 常见 oss://bucket/path 或 release/temp-.../
    prefix = None
    m = re.search(r"release/temp-[\w/\-]+/?", text)
    if m:
        prefix = m.group(0)
    if not prefix:
        m = re.search(r"oss://[^/\s]+/([^\s]+)", text)
        if m:
            prefix = m.group(1)

    result = {
        "project": project,
        "access_key_id": ak,
        "access_key_secret": sk,
        "endpoint": ep,
        "bucket": bucket,
        "prefix": prefix,
        "release_date": date,
        "expire": expire,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
