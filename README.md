# seekgene-oss-download

从测序服务商「数据释放」邮件中提取阿里云 OSS 下载凭据，批量下载单细胞/组学测序数据，并做 MD5 完整性校验。

> 本仓库为通用工具 + 经验沉淀，不含任何真实凭据、样本编号或个人信息。

## 功能

- 解析数据释放邮件（`.eml`），提取 OSS 连接参数
- 遍历 OSS 对象，输出完整清单（大小 / key / etag）
- 多线程并行 + `Range` 断点续传批量下载
- 实时进度条 / 文件统计 / 预计完成时间
- 基于 `md5.txt` 的完整性校验（金标准）

## 五步流程

1. **解析邮件拿凭据**：`python3 scripts/parse_email.py 邮件.eml`
2. **列清单**：`python3 scripts/list_oss.py > list_objects.txt`
3. **批量下载**：`nohup python3 -u scripts/download.py > download.log 2>&1 &`
4. **看进度**：`python3 scripts/progress.py`
5. **MD5 校验**：`python3 scripts/verify.py`（全通过输出 `ALL_MD5_VERIFIED_OK`）

## 凭据配置方式

所有脚本通过**环境变量**读取连接信息，避免把敏感凭据写进代码：

```bash
export OSS_ACCESS_KEY_ID="..."
export OSS_ACCESS_KEY_SECRET="..."
export OSS_ENDPOINT="oss-cn-beijing.aliyuncs.com"
export OSS_BUCKET="..."
export OSS_PREFIX="release/temp-.../"
export LOCAL_ROOT="/path/to/download/dir"
```

## 目录结构

```
seekgene-oss-download/
├── README.md
├── SKILL.md
├── cases.md
├── CHANGELOG.md
└── scripts/
    ├── parse_email.py   # 从 .eml 提取 OSS 凭据
    ├── list_oss.py      # 列出 OSS 对象清单
    ├── download.py      # 断点续传 + 多线程批量下载
    ├── progress.py      # 进度条 / 统计 / ETA
    └── verify.py        # MD5 完整性校验
```

## 依赖

```bash
python3 -m pip install oss2
```

## 注意事项

- 释放链接通常有有效期，务必在期限内完成下载。
- 大小一致不等于数据完整，务必执行 MD5 校验。
- 不要将 AccessKey 提交到任何公开仓库。
