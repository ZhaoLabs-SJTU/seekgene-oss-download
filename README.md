# 🧬 seekgene-oss-download

> 从测序服务商「数据释放」邮件中提取阿里云 OSS 下载凭据，批量下载单细胞/组学测序数据，并做 MD5 完整性校验，一站式自动化工具。

![python](https://img.shields.io/badge/python-3.8%2B-blue?style=for-the-badge)
![platform](https://img.shields.io/badge/platform-Linux%20%2F%20macOS-orange?style=for-the-badge)
![license](https://img.shields.io/badge/license-MIT-lightgrey?style=for-the-badge)

> 本仓库为通用工具 + 经验沉淀，不含任何真实凭据、样本编号或个人信息。

## 📖 文档导航

| 文档 | 适用人群 | 预计时间 |
|------|---------|:--:|
| **[🌟 新手完全指南](新手完全指南.md)** | 零基础小白（从邮件到下载验收） | 15 分钟阅读 + 约 1 天执行 |
| **[SKILL.md](SKILL.md)** | AI 助手 / 进阶用户（完整流程 + 故障排查） | — |
| **[cases.md](cases.md)** | 实战案例参考（已脱敏） | — |
| **[scripts/](scripts/)** | 五个可复用脚本 | — |
| **[小白文档](小白文档/)** | Word/Excel/PPT 三件套（课题组培训） | — |

> ⚠️ **如果你不确定该看哪个** → 直接打开 **[新手完全指南](新手完全指南.md)**，从第一章开始！

## ✨ 特性

- 📧 解析数据释放邮件（`.eml`），提取 OSS 连接参数（AK/SK/Endpoint/Bucket/Prefix/有效期）
- 📂 遍历 OSS 对象，输出完整清单（大小 / key / etag）
- ⬇️ 多线程并行 + `Range` 断点续传批量下载
- 📊 实时进度条 / 文件统计 / 预计完成时间
- ✅ 完整性金标准校验（基于 `md5.txt` 逐文件比对）
- 📄 Word / Excel / PPT 三件套报告自动生成

## 🏗️ 平台架构

```
数据释放：  邮件（.eml）           → 提取 AK/SK/Endpoint/Bucket/Prefix/有效期
对象存储：  阿里云 OSS（S3 兼容）   → oss2 SDK 遍历 + Range 断点续传下载
完整性：    md5.txt               → 逐文件 MD5 比对（金标准）
```

## 📦 安装

```bash
python3 -m pip install oss2
```

## 🚀 快速开始

### 0. 配置凭据（环境变量，绝不硬编码）

```bash
export OSS_ACCESS_KEY_ID="..."
export OSS_ACCESS_KEY_SECRET="..."
export OSS_ENDPOINT="oss-cn-beijing.aliyuncs.com"
export OSS_BUCKET="..."
export OSS_PREFIX="release/temp-.../"
export LOCAL_ROOT="/path/to/download/dir"
```

### 1. 解析邮件拿凭据

```bash
python3 scripts/parse_email.py "数据释放邮件.eml"
```

### 2. 列出 OSS 全部对象

```bash
python3 scripts/list_oss.py > list_objects.txt
```

### 3. 批量下载（断点续传 + 多线程）

```bash
nohup python3 -u scripts/download.py > download.log 2>&1 &
```

### 4. 查看进度

```bash
python3 scripts/progress.py
```

### 5. MD5 完整性校验（金标准）

```bash
python3 scripts/verify.py
# 全部通过输出 ALL_MD5_VERIFIED_OK
```

## 🧪 实测结果

| 批次 | 文件数 | 数据量 | 结果 |
|------|:--:|:--:|------|
| 某单细胞项目（7 例样本，5 类数据） | 87 | ~178 GB | 87 对象全下，42/42 MD5 通过 |

## 📂 目录结构

```
seekgene-oss-download/
├── SKILL.md                 ← 完整技能文档（流程 + 故障排查 + 速查表）
├── README.md
├── LICENSE
├── 新手完全指南.md            ← 零基础小白从入门到验收
├── cases.md                 ← 实战案例（已脱敏）
├── CHANGELOG.md
├── scripts/
│   ├── parse_email.py       ← 从 .eml 提取 OSS 凭据
│   ├── list_oss.py          ← 列出 OSS 对象清单
│   ├── download.py          ← 断点续传 + 多线程批量下载
│   ├── progress.py          ← 进度条 / 统计 / ETA
│   └── verify.py            ← MD5 完整性校验
└── 小白文档/                 ← 用户友好三件套
    ├── 寻因数据下载_小白操作手册.docx
    ├── 寻因数据下载_操作表格.xlsx
    └── 寻因数据下载_演示文稿.pptx
```

## ❓ 常见问题

| 现象 | 解决 |
|------|------|
| 释放链接失效 / `403` | 释放链接有有效期，务必在期限内完成；过期联系服务商重新释放 |
| 大小一致但怕数据损坏 | 大小一致 ≠ 完整，务必执行 MD5 校验 |
| 下载到一半中断 | 脚本支持 `Range` 断点续传，直接重跑即可 |
| 担心凭据泄露 | 一律走环境变量，不硬编码、不进 Git 历史 |

## 📄 License

[MIT](LICENSE)
