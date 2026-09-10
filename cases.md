# cases.md — 实战案例记录

> 以下案例已脱敏：不含真实项目编号、样本编号、机构/课题组名称、OSS 凭据或本地路径。

## 案例 1：某单细胞项目（7 例样本）— 完成 ✅

- **服务类型**：单细胞 3' 转录组建库测序
- **样本数**：7 例
- **数据类别**：rds、raw_matrix、loom、matrix、bam（5 类 × 7 样本）

### OSS 信息（示例）

| 项 | 值 |
|---|---|
| Endpoint | oss-cn-beijing.aliyuncs.com（华北2 北京） |
| Bucket | `<bucket>`（示例，实际按邮件填写） |
| Prefix | `release/temp-YYYYMMDDHHMMSS/` |
| 对象总数 | 87 |
| 总大小 | 约 178 GB |

### 下载过程

- 工具：`oss2` Python SDK，6 线程并行 + `Range` 断点续传。
- 速度：稳定约 40 MB/s（合计）。
- 耗时：约 1 小时 10 分钟。
- BAM 是下载主体；小文件最后几十秒内补齐。

### 完整性校验结果

```
VERIFY_RESULT: 42/42 OK
ALL_MD5_VERIFIED_OK
```

- 42 个数据文件全部 MD5 匹配（7 bam + 7 bam.bai + 7 loom + 7 matrix + 7 raw_matrix + 7 rds）。
- 无一缺失、无一不匹配，无需补下载。

### 复用要点（下次同类项目直接照做）

1. `parse_email.py` 解析新邮件 → 拿到新 AK/SK/Prefix。
2. 设置环境变量（AK/SK/Endpoint/Bucket/Prefix/LOCAL_ROOT）。
3. `list_oss.py > list_objects.txt` → `nohup python3 -u download.py > download.log 2>&1 &`。
4. 定时 `progress.py` 看进度，直到 `ALL_FINISHED`。
5. `verify.py` 做 MD5，确认 `ALL_MD5_VERIFIED_OK`。
