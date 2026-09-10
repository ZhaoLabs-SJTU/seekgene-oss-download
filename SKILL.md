# Skill: seekgene-oss-download（测序数据 OSS 下载）

从测序服务商「数据释放」邮件中提取阿里云 OSS 凭据，批量下载单细胞/组学测序数据，并做 MD5 完整性校验。

## 适用场景

- 测序服务商释放测序数据，邮件里给出阿里云 OSS 下载链接与 AccessKey。
- 数据目录典型结构：`data/bam`、`data/loom`、`data/matrix`、`data/raw_matrix`、`data/rds`，外加 `md5.txt` 校验文件。
- 单细胞转录组（如 3' 建库测序）项目。

## 前置条件

- Linux / WSL2，Python 3，已安装 `oss2`：
  ```bash
  python3 -m pip install oss2
  ```
- 能访问目标下载磁盘（如 Windows 盘挂载到 `/mnt/d/...`）。

## 五步流程

### 第 1 步：解析邮件拿凭据

```bash
python3 scripts/parse_email.py "邮件文件.eml"
```

输出 JSON：`access_key_id`、`access_key_secret`、`endpoint`、`bucket`、`prefix`、`expire`。

> 若正文是 HTML，脚本会自动转纯文本再匹配。AccessKeyId 通常以 `LTAI` 开头，Endpoint 形如 `oss-cn-beijing.aliyuncs.com`。

### 第 2 步：列出 OSS 全部对象

设置环境变量后：

```bash
python3 scripts/list_oss.py > list_objects.txt
```

`list_objects.txt` 每行：`<size字节> <key> <etag>`，用于后续 progress.py 统计。

### 第 3 步：批量下载（断点续传 + 多线程）

```bash
nohup python3 -u scripts/download.py > download.log 2>&1 &
```

特点：
- `max_workers=6` 并行；每个文件先按「本地大小 == OSS 大小」跳过已完成的，否则用 `Range` 断点续传。
- 完成输出 `ALL_FINISHED`。

### 第 4 步：查看进度

```bash
python3 scripts/progress.py
```

输出总体进度条、文件统计（DONE / PARTIAL / PENDING）、每个文件的字节进度。

### 第 5 步：MD5 完整性校验（金标准）

```bash
python3 scripts/verify.py
```

读取 `md5.txt`，用多线程逐一计算每个数据文件的 MD5，与公司提供的值比对。全通过则输出：

```
VERIFY_RESULT: N/N OK
ALL_MD5_VERIFIED_OK
```

有任一不匹配/缺失则以非零退出码结束，需针对该文件重新下载。

## 关键约定 / 经验

1. **BAM 是大头**：通常 BAM 占总量 95% 以上。小文件（loom/matrix/raw_matrix/rds）每个仅几十~几百 MB。
2. **先并行下 BAM，再补小文件**：多线程跑 BAM 时速度可稳定到较高水平，百余 GB 一小时左右可下完。
3. **断点续传是关键**：网络中断后重跑 `download.py` 会跳过已完成的、续传未完成的，幂等安全。
4. **MD5 校验必须做**：大小一致不等于数据完整，以 `md5.txt` 为准。
5. **有效期**：释放邮件通常给数十天，逾期 OSS 临时路径会失效，务必在期限内下完。
6. **AccessKey 敏感**：勿提交到公开仓库；凭据仅供本次下载使用。

## 文件清单

```
seekgene-oss-download/
├── SKILL.md
├── cases.md
├── CHANGELOG.md
└── scripts/
    ├── parse_email.py   # 从 .eml 提取 OSS 凭据
    ├── list_oss.py      # 列出 OSS 对象清单
    ├── download.py      # 断点续传 + 多线程批量下载
    ├── progress.py      # 进度条 / 表格 / ETA
    └── verify.py        # MD5 完整性校验
```
