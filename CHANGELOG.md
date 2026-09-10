# CHANGELOG — seekgene-oss-download

## v1.0.0 — 2026-09-10

- 首次发布，源自一次真实的测序数据释放下载任务（已脱敏）。
- 完整走通「解析邮件 → 列清单 → 断点续传下载 → 进度监控 → MD5 校验」五步流程。
- 交付脚本 5 个：
  - `parse_email.py`：从 .eml 提取 OSS 凭据（AK/SK/Endpoint/Bucket/Prefix/有效期）。
  - `list_oss.py`：遍历 OSS 对象，输出 `size key etag` 清单。
  - `download.py`：多线程并行 + Range 断点续传 + 完成即跳过。
  - `progress.py`：总体进度条、文件统计、逐文件字节进度。
  - `verify.py`：基于 md5.txt 的多线程 MD5 完整性校验。
- 凭据全部改为环境变量注入，代码不含任何敏感信息。
- 实战验证：87 对象 / 约 178 GB 全部下载完成，42/42 MD5 校验通过。
