---
name: seekgene-oss-download
description: 从测序服务商「数据释放」邮件中提取阿里云 OSS 下载凭据，批量下载单细胞/组学测序数据，并做 MD5 完整性校验。覆盖邮件解析 parse_email、对象遍历 list_oss、断点续传下载 download、进度监控 progress、MD5 金标准校验 verify 五步流程，适用于测序数据释放（BAM/loom/matrix/raw_matrix/rds）。
---

# 🧬 寻因(SeekGene) OSS 数据下载 Skill

> 🎯 **一句话说明**：从测序服务商「数据释放」邮件中提取阿里云 OSS 下载凭据，批量下载单细胞/组学测序数据到本地，并自动完成 MD5 完整性校验。沉淀了 OSS 邮件凭据解析、Range 断点续传多线程下载、md5.txt 金标准校验等关键机制。

## 📖 目录

- [核心铁律](#核心铁律)
- [平台架构](#平台架构)
- [邮件解析](#邮件解析)
- [对象遍历](#对象遍历)
- [批量下载](#批量下载)
- [进度监控](#进度监控)
- [完整性校验（金标准）](#完整性校验金标准)
- [故障排查决策树](#故障排查决策树)
- [测试记录](#测试记录)
- [速查表](#速查表)
- [参考脚本](#参考脚本)

## 核心铁律

| # | 铁律 | 原因 |
|:--:|------|------|
| 1 | **凭据一律走环境变量**，绝不硬编码进代码 | 防 AccessKey 泄露进 Git 历史 |
| 2 | **大小一致 ≠ 数据完整**，必须跑 MD5 校验 | 断点续传/网络抖动都可能产生损坏 |
| 3 | **BAM 是下载主体**，小文件最后批量补齐 | BAM 占比 >95%，优先下载，小文件几十秒内补齐 |
| 4 | **断点续传判断用「本地大小 == OSS 大小」** | 已完成的文件直接跳过，重跑安全幂等 |
| 5 | **释放链接有有效期**，务必期限内完成 | 过期后 `403`，需联系服务商重新释放 |

## 平台架构

```
数据释放：  邮件（.eml）           → 提取 AK/SK/Endpoint/Bucket/Prefix/有效期
对象存储：  阿里云 OSS（S3 兼容）   → oss2 SDK list_objects + get_object(Range)
完整性：    md5.txt               → 逐文件 MD5 比对（金标准）
```

## 邮件解析

```bash
python3 scripts/parse_email.py "数据释放邮件.eml"
```

输出 JSON：`access_key_id`、`access_key_secret`、`endpoint`、`bucket`、`prefix`、`expire`。

| 要点 | 说明 |
|------|------|
| HTML 正文 | 脚本自动转纯文本再匹配，无需人工提取 |
| AccessKeyId | 通常以 `LTAI` 开头 |
| Endpoint | 形如 `oss-cn-beijing.aliyuncs.com`（华北2 北京） |
| Prefix | 形如 `release/temp-YYYYMMDDHHMMSS/` |

## 对象遍历

```bash
export OSS_ACCESS_KEY_ID="..." OSS_ACCESS_KEY_SECRET="..." \
       OSS_ENDPOINT="oss-cn-beijing.aliyuncs.com" \
       OSS_BUCKET="..." OSS_PREFIX="release/temp-.../"
python3 scripts/list_oss.py > list_objects.txt
```

`list_objects.txt` 每行：`<size字节> <key> <etag>`，供 `progress.py` 统计总量与完成度。

| 要点 | 说明 |
|------|------|
| 遍历 | oss2 `ObjectIteratorV2` 分页拉全量对象（含子目录） |
| 数据类别 | 典型结构 `data/bam`、`data/loom`、`data/matrix`、`data/raw_matrix`、`data/rds` + `md5.txt` |

## 批量下载

```bash
nohup python3 -u scripts/download.py > download.log 2>&1 &
```

| 要点 | 说明 |
|------|------|
| 并发 | `max_workers=6` 并行下载 |
| 断点续传 | 先按「本地大小 == OSS 大小」跳过已完成文件，否则 `Range` 续传 |
| 幂等 | 重跑安全，已完成的不会重复下载 |
| 完成标志 | 日志输出 `ALL_FINISHED` |

## 进度监控

```bash
python3 scripts/progress.py
```

输出：总体进度条、文件统计（DONE / PARTIAL / PENDING）、每个文件的字节进度与预计完成时间。

## 完整性校验（金标准）

```bash
python3 scripts/verify.py
# 全部通过输出 ALL_MD5_VERIFIED_OK
```

```
下载完成后校验：
1. 文件数：磁盘文件数 == 邮件/清单描述的文件数
2. 类别齐全：bam / loom / matrix / raw_matrix / rds 每类样本数一致
3. 内容一致性：逐文件 MD5 与 md5.txt 比对，必须 100% 匹配
```

⚠️ **大小一致不算数**——断点续传中断、网络抖动都可能产生「大小对但内容坏」的文件，必须用 md5.txt 做金标准校验。

## 故障排查决策树

```
下载报 403 / 链接打不开
  └─ 释放链接过期 → 联系服务商重新释放（有效期通常 90 天）

下载到一半中断 / 进程被杀
  └─ 脚本支持断点续传 → 直接重跑 download.py（已完成的自动跳过）

verify.py 报 FAILED / MD5 不匹配
  ├─ 先确认该文件是否下载完整（对比 OSS size）
  └─ 删除该文件重下（download.py 会 Range 续传补齐）

AccessKey 失效
  └─ 重新解析邮件 / 联系服务商索要新的 AccessKey

oss2 未安装
  └─ python3 -m pip install oss2
```

## 测试记录

| 日期 | 任务 | 结果 |
|------|------|------|
| 2026-09 | 某单细胞项目（7 例样本，5 类数据） | 87 对象 ~178 GB 全下，42/42 MD5 通过 |

## 速查表

| 操作 | 命令/要点 |
|------|------|
| 解析邮件 | `python3 scripts/parse_email.py 邮件.eml` |
| 列清单 | `python3 scripts/list_oss.py > list_objects.txt` |
| 批量下载 | `nohup python3 -u scripts/download.py > download.log 2>&1 &` |
| 看进度 | `python3 scripts/progress.py` |
| MD5 校验 | `python3 scripts/verify.py`（`ALL_MD5_VERIFIED_OK` = 通过） |
| 凭据注入 | 环境变量 `OSS_ACCESS_KEY_ID/SECRET/ENDPOINT/BUCKET/PREFIX` |
| 完成标志 | 下载 `ALL_FINISHED`，校验 `ALL_MD5_VERIFIED_OK` |

## 参考脚本

| 脚本 | 用途 |
|------|------|
| `scripts/parse_email.py` | 从 .eml 提取 OSS 凭据（AK/SK/Endpoint/Bucket/Prefix/有效期） |
| `scripts/list_oss.py` | 遍历 OSS 对象，输出 `size key etag` 清单 |
| `scripts/download.py` | 多线程并行 + Range 断点续传 + 完成即跳过 |
| `scripts/progress.py` | 总体进度条、文件统计、逐文件字节进度 |
| `scripts/verify.py` | 基于 md5.txt 的多线程 MD5 完整性校验 |

> 🔐 AccessKey 属敏感信息：脚本一律从环境变量读取，绝不硬编码，不写入 Git 历史。
