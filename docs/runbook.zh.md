# 中文操作手册

这份文档说明如何把一个原始关键词文件跑成中文、可筛选的人工审阅工作簿。

## 0. Job 目录

每个原始文件使用一个独立输出目录：

```text
outputs/<job-id>/
```

示例：

```text
outputs/tiktok_phrase-match_us_2026-05-26/
```

## 1. 生成 Intake Fact Table

```bash
python3 scripts/keyword_intake.py \
  "/absolute/path/to/source.xlsx" \
  --sheet "<sheet-name>" \
  --id-prefix "<PREFIX>" \
  --out outputs/<job-id>/intake_fact_table.csv
```

可选：生成中文列名版本。

```bash
python3 scripts/keyword_intake.py \
  "/absolute/path/to/source.xlsx" \
  --sheet "<sheet-name>" \
  --id-prefix "<PREFIX>" \
  --locale zh \
  --out outputs/<job-id>/intake_fact_table_zh.csv
```

输出：

```text
outputs/<job-id>/intake_fact_table.csv
outputs/<job-id>/intake_fact_table_zh.csv
```

注意：intake 阶段只做事实提示，不做最终语义判断。

## 2. 切批次

```bash
python3 scripts/prepare_batches.py \
  outputs/<job-id>/intake_fact_table.csv \
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

每批最多 200 个词。

## 3. 语义标注一个批次

给 annotation subagent 的任务说明：

```text
读取：
- docs/schemas.md
- docs/batch-policy.md
- skills/intent-grouping/agents/annotation-subagent.md

输入：
outputs/<job-id>/batches/batch_XXX.csv

输出：
outputs/<job-id>/annotations/batch_XXX_annotations.csv

规则：
- 每个输入关键词必须输出一行
- 内容用中文
- 字段名用英文
- 语义标注独立于 keyword-intake
- intake 字段只能作为提示，不能作为最终结论
- web_verification_required=yes 时，web_verification_status 必须是 performed
- 网络核验结论必须是具体中文结论
```

## 4. 校验 annotation 结构

```bash
python3 scripts/validate_annotation_batch.py \
  --input-batch outputs/<job-id>/batches/batch_XXX.csv \
  --annotation outputs/<job-id>/annotations/batch_XXX_annotations.csv
```

通过时输出：

```text
annotation batch validation passed
```

如果结构校验失败，先修结构，再进入 QA。

## 5. 导出中文 annotation 表

```bash
python3 scripts/export_annotation_zh.py \
  outputs/<job-id>/annotations/batch_XXX_annotations.csv \
  --out outputs/<job-id>/annotations/batch_XXX_annotations_zh.csv
```

## 6. 独立 QA

给 QA subagent 的任务说明：

```text
读取：
- docs/qa-policy.md
- docs/batch-policy.md
- docs/schemas.md
- skills/intent-grouping/agents/qa-subagent.md

输入：
outputs/<job-id>/batches/batch_XXX.csv
outputs/<job-id>/annotations/batch_XXX_annotations.csv

输出：
outputs/<job-id>/qa/batch_XXX_qa.csv
outputs/<job-id>/qa/batch_XXX_qa_problems.csv  # 仅 problem_count > 0 时生成

禁止直接修改 annotation 文件。
```

通过条件：

```text
qa_status=pass
problem_count=0
```

只有 QA 通过的批次才能合并。

## 7. 判断修复方式

### targeted repair

适用于局部问题：

```text
- 少量词缺少具体网络核验
- 少量词标签/风险字段不一致
- 少量词语义判断错误
```

### full rerun

适用于系统性问题：

```text
- 批量模板化标注
- 大量语义/风险误判
- 大量复制 intake 标签
- 漏 ID 或重复 ID
- 大量 web_verification_required=yes 但不是 performed
```

## 8. targeted repair

给 repair subagent 的任务说明：

```text
输入：
outputs/<job-id>/annotations/batch_XXX_annotations.csv
outputs/<job-id>/qa/batch_XXX_qa_problems.csv

输出：
outputs/<job-id>/annotations/batch_XXX_annotations_repaired.csv

规则：
- 保留所有行和原顺序
- 只修改 QA problem rows
- 非问题行不动
- 对 requires_web_search=yes 的行做网络核验
- web_verification_required=yes 时，status 必须是 performed
- 修完后跑 validate_annotation_batch.py
```

修完后重新跑独立 final QA。

## 9. full rerun

给 rerun subagent 的任务说明：

```text
输入：
outputs/<job-id>/batches/batch_XXX.csv
outputs/<job-id>/qa/batch_XXX_qa.csv
outputs/<job-id>/qa/batch_XXX_qa_problems.csv

输出：
outputs/<job-id>/annotations/batch_XXX_annotations_rerun.csv

规则：
- 整批 200 行重新标注
- 不只修 problem rows
- 避免模板化标签
- 对不稳定或 QA 标出的词做网络核验
- 修完后跑 validate_annotation_batch.py
```

修完后重新跑独立 final QA。

## 10. 准备 merge-ready 文件

final QA 通过后，把最终 annotation 复制到 merge-ready 目录。

```text
outputs/<job-id>/merge_ready_<range>/
```

示例：

```bash
mkdir -p outputs/<job-id>/merge_ready_001_004

cp outputs/<job-id>/annotations/batch_001_annotations_rerun_v3.csv \
  outputs/<job-id>/merge_ready_001_004/batch_001_final.csv

cp outputs/<job-id>/annotations/batch_002_annotations_repaired_v2.csv \
  outputs/<job-id>/merge_ready_001_004/batch_002_final.csv
```

## 11. 部分合并时生成 source slice

如果只合并部分批次，需要先生成对应的源表切片。

前 4 批是 800 行：

```bash
python3 - <<'PY'
import csv
from pathlib import Path

base=Path("outputs/<job-id>")
source=base/"intake_fact_table.csv"
out=base/"source_first_004_batches.csv"

with source.open(encoding="utf-8") as f:
    reader=csv.DictReader(f)
    fields=reader.fieldnames
    rows=[row for _, row in zip(range(800), reader)]

with out.open("w", encoding="utf-8", newline="") as f:
    writer=csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)
PY
```

如果是全量合并，直接使用完整 `intake_fact_table.csv`。

## 12. 合并并检查覆盖

```bash
python3 scripts/merge_annotations.py \
  --source outputs/<job-id>/source_first_004_batches.csv \
  --annotations-dir outputs/<job-id>/merge_ready_001_004 \
  --out outputs/<job-id>/merged/full_annotation_details_001_004.csv \
  --coverage-report outputs/<job-id>/merged/coverage_report_001_004.csv
```

通过时输出：

```text
coverage passed for <row-count> rows
```

覆盖检查失败时，不允许进入最终交付。

## 13. 导出中文合并明细

```bash
python3 scripts/export_annotation_zh.py \
  outputs/<job-id>/merged/full_annotation_details_001_004.csv \
  --out outputs/<job-id>/merged/full_annotation_details_001_004_zh.csv
```

## 14. 生成可筛选 Excel 审阅工作簿

```bash
python3 scripts/build_review_workbook.py \
  --detail outputs/<job-id>/merged/full_annotation_details_001_004_zh.csv \
  --qa-summary outputs/<job-id>/merged/qa_summary_001_004.csv \
  --coverage outputs/<job-id>/merged/coverage_report_001_004.csv \
  --out outputs/<job-id>/merged/人工审阅工作簿_001_004.xlsx
```

要求：每个 sheet 都必须有筛选器。

## 15. TikTok 当前示例

前 4 批最终使用：

```text
batch_001_annotations_rerun_v3.csv
batch_002_annotations_repaired_v2.csv
batch_003_annotations_repaired_v3.csv
batch_004_annotations_repaired.csv
```

最终输出：

```text
outputs/tiktok_phrase-match_us_2026-05-26/merged/full_annotation_details_001_004_zh.csv
outputs/tiktok_phrase-match_us_2026-05-26/merged/人工审阅工作簿_001_004.xlsx
```
