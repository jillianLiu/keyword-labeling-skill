# keyword-labeling-skill

这是一个独立的关键词打标项目，用来处理大批量关键词表，完成：

1. 原始关键词导入
2. 每个原始词完整保留
3. 事实信号预处理
4. 逐词语义/搜索意图打标
5. 独立 QA 审核
6. QA 失败后的局部修复或整批重跑
7. 已通过批次合并
8. 合并后覆盖检查
9. 输出中文、可筛选的人工审阅工作簿

本项目不负责：

- SEO 页面规划
- 营销文案生成
- 多语言本地化
- CMS 发布
- 图片生成

## 核心流程

```text
原始关键词文件
-> keyword-intake
-> 每 200 个词切一批
-> annotation subagent 逐批语义打标
-> QA subagent 独立审核
-> targeted repair 或 full rerun
-> final QA
-> 合并 QA 通过批次
-> 脚本覆盖检查
-> 中文人工审阅工作簿
```

## 关键原则

- `keyword-intake` 只做事实准备，不做最终语义判断。
- 第二步语义打标独立于第一步，intake 字段只能作为提示。
- 每批最多 200 个词。
- QA 必须由独立 subagent 完成，不能由同一个标注者自审。
- 如果只是一小批词缺少网络核验或字段不一致，走 `targeted repair`。
- 如果出现模板化标注、系统性误判、漏 ID、重复 ID，走 `full rerun`。
- 只有 final QA 通过的批次才能进入合并。
- 合并后必须跑覆盖检查，确认没有漏词、重复词或未知 ID。
- 给人工审核的最终表默认中文。
- 最终审阅交付优先给 `.xlsx`，每个 sheet 都启用筛选器。

## 快速命令

### 1. 生成 intake fact table

```bash
python3 scripts/keyword_intake.py "/absolute/path/to/source.xlsx" \
  --sheet "<sheet-name>" \
  --id-prefix "<PREFIX>" \
  --out outputs/<job-id>/intake_fact_table.csv
```

可选：生成中文列名版本，方便人工预览。

```bash
python3 scripts/keyword_intake.py "/absolute/path/to/source.xlsx" \
  --sheet "<sheet-name>" \
  --id-prefix "<PREFIX>" \
  --locale zh \
  --out outputs/<job-id>/intake_fact_table_zh.csv
```

### 2. 按 200 个词切批次

```bash
python3 scripts/prepare_batches.py outputs/<job-id>/intake_fact_table.csv \
  --out-dir outputs/<job-id> \
  --batch-size 200
```

输出：

```text
outputs/<job-id>/batch_manifest.csv
outputs/<job-id>/batches/batch_001.csv
outputs/<job-id>/batches/batch_002.csv
...
```

### 3. 校验一个 annotation batch

```bash
python3 scripts/validate_annotation_batch.py \
  --input-batch outputs/<job-id>/batches/batch_XXX.csv \
  --annotation outputs/<job-id>/annotations/batch_XXX_annotations.csv
```

通过时输出：

```text
annotation batch validation passed
```

### 4. 导出中文 annotation 表

```bash
python3 scripts/export_annotation_zh.py \
  outputs/<job-id>/annotations/batch_XXX_annotations.csv \
  --out outputs/<job-id>/annotations/batch_XXX_annotations_zh.csv
```

### 5. 合并 QA 通过的批次并检查覆盖

```bash
python3 scripts/merge_annotations.py \
  --source outputs/<job-id>/<source-slice-or-full-intake>.csv \
  --annotations-dir outputs/<job-id>/merge_ready_<range> \
  --out outputs/<job-id>/merged/full_annotation_details_<range>.csv \
  --coverage-report outputs/<job-id>/merged/coverage_report_<range>.csv
```

覆盖检查通过时输出：

```text
coverage passed for <row-count> rows
```

### 6. 生成可筛选的中文 Excel 审阅工作簿

```bash
python3 scripts/build_review_workbook.py \
  --detail outputs/<job-id>/merged/full_annotation_details_<range>_zh.csv \
  --qa-summary outputs/<job-id>/merged/qa_summary_<range>.csv \
  --coverage outputs/<job-id>/merged/coverage_report_<range>.csv \
  --out outputs/<job-id>/merged/人工审阅工作簿_<range>.xlsx
```

## Subagent 分工

### annotation subagent

负责逐批语义标注。

读取：

```text
docs/schemas.md
docs/batch-policy.md
skills/intent-grouping/agents/annotation-subagent.md
```

输入：

```text
outputs/<job-id>/batches/batch_XXX.csv
```

输出：

```text
outputs/<job-id>/annotations/batch_XXX_annotations.csv
```

要求：

- 每个输入词必须输出一行。
- 内容用中文。
- 字段名用英文，方便脚本校验。
- 不直接复制 intake 标签。
- 需要网络核验时，`web_verification_status` 必须是 `performed`。
- 网络核验结论必须是具体中文结论。

### QA subagent

负责独立审核 annotation。

读取：

```text
docs/qa-policy.md
docs/batch-policy.md
docs/schemas.md
skills/intent-grouping/agents/qa-subagent.md
```

输入：

```text
outputs/<job-id>/batches/batch_XXX.csv
outputs/<job-id>/annotations/batch_XXX_annotations.csv
```

输出：

```text
outputs/<job-id>/qa/batch_XXX_qa.csv
outputs/<job-id>/qa/batch_XXX_qa_problems.csv
```

QA 不允许直接修改 annotation 文件。

## QA 失败后怎么处理

### targeted repair

适用于局部问题：

- 少量词缺少具体网络核验
- 少量词标签和风险字段不一致
- 少量词语义判断错误

规则：

- 保留 200 行和原顺序。
- 只修 QA problem rows。
- 非问题行不动。
- 修完后重新结构校验。
- 再跑独立 final QA。

### full rerun

适用于系统性问题：

- 批量模板化标注
- 大量误判
- 大量从 intake 机械复制
- 漏 ID / 重复 ID
- 大量 `web_verification_required=yes` 但没有 `performed`

规则：

- 整批 200 行重新标注。
- 不只 patch 少数问题行。
- 修完后重新结构校验。
- 再跑独立 final QA。

## 当前 TikTok 示例

原始文件：

```text
tiktok_phrase-match_us_2026-05-26.xlsx
```

规模：

```text
50,003 个关键词
251 个 batch
```

已完成闭环：

```text
batch_001: pass
batch_002: pass
batch_003: pass
batch_004: pass
```

已合并：

```text
前 800 个词
```

已生成：

```text
outputs/tiktok_phrase-match_us_2026-05-26/merged/full_annotation_details_001_004_zh.csv
outputs/tiktok_phrase-match_us_2026-05-26/merged/人工审阅工作簿_001_004.xlsx
```

## 目录结构

```text
data/input/     原始输入样例或小测试文件
outputs/        生成的 fact table、批次、annotation、QA、合并表、工作簿
docs/           操作说明、规则、schema、QA 策略
scripts/        确定性脚本
skills/         Codex skill 定义和 subagent 规则
```

## 重要文档

- [中文操作手册](docs/runbook.zh.md)
- [英文操作手册](docs/runbook.md)
- [表结构说明](docs/schemas.md)
- [批次策略](docs/batch-policy.md)
- [QA 策略](docs/qa-policy.md)
- [输出契约](docs/output-contract.md)
