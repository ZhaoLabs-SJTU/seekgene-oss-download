# CHANGELOG — seekgene-oss-download

## v1.2.0 — 2026-09-10

- 沉淀二次校验实战经验，完善「完整性校验」章节：
  - 明确 **MD5 校验需后台运行**：读 178 GB 约 5–10 分钟，用 `nohup ... > verify_check.log 2>&1 &` + `tail` 轮询，避免前台阻塞。
  - 记录 **md5.txt 格式**：每行 `<md5>  <相对路径>`，行数 = 数据文件数（本案例 42 行）。
  - 记录 **verify 输出三态 + 汇总**：`OK / MISSING / MISMATCH` → `VERIFY_RESULT: X/Y OK` → `ALL_MD5_VERIFIED_OK`（有异常则 `FAILED N files` 且 exit 1）。
- 新增「参考脚本」路径说明：实战脚本在 `~/seekgene_dl/` 根目录而非 `scripts/` 子目录，曾因误用 `scripts/verify.py` 失败，需统一路径约定。

## v1.1.0 — 2026-09-10

- 补齐标准板块，对齐同组织其它 skill 仓库的排版布局：
  - 新增 `LICENSE`（MIT）。
  - 新增 `新手完全指南.md`（零基础小白从邮件到验收）。
  - 新增 `小白文档/` 三件套（docx 操作手册 / xlsx 操作表格 / pptx 演示文稿，均已脱敏）。
- 重写 `README.md`：badge + 文档导航 + 特性 + 平台架构 + 快速开始 + 实测结果 + 常见问题。
- 重写 `SKILL.md`：YAML frontmatter + 目录 + 核心铁律 + 平台架构 + 故障排查决策树 + 测试记录 + 速查表。
- 新增 `scripts/gen_docs.py`：一键生成小白三件套（可复用）。

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
