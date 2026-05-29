# 简明操作步骤 / Simple Operator Steps

这份文档给人工操作者看，尽量不用脚本细节。需要复制命令时，再看 `docs/runbook.zh.md` 或 `docs/runbook.md`。

## 中文版

### 1. 准备原始关键词文件

把原始关键词表放到项目可访问的位置。确认表里至少有关键词列，最好也保留来源、搜索量、竞争度等原始字段。

### 2. 生成 intake fact table

先运行 intake。这个步骤只做事实整理：保留原始词，生成稳定 ID，并补充一些机械可判断的提示字段。

注意：intake 不是最终语义打标结果，只能给后面的标注者参考。

### 3. 检查 intake 结果

确认总行数和原始表一致，没有漏词。抽查几个关键词，确认原始词没有被改写。

### 4. 按 200 个词切批次

把 intake 表切成多个小批次。默认每批 200 个词，方便 subagent 标注和 QA。

### 5. 逐批做语义打标

让 annotation subagent 读取某一个 batch，逐个关键词判断真实语义、搜索意图、风险、平台/品牌/竞品等信息。

标注内容用中文，字段名保留英文，方便脚本检查。

### 6. 对需要核验的词做网络搜索

如果关键词含义不确定、像品牌/人物/平台/竞品、可能涉风险，或者 QA 指出不合适，就需要做网络搜索核验。

只要 `web_verification_required=yes`，就必须真的完成搜索核验，并写出具体中文结论。

### 7. 跑结构校验

每个 batch 标注完后，先用脚本检查有没有漏行、重复 ID、未知 ID、字段缺失或非法枚举值。

结构校验没过时，先修结构，不进入 QA。

### 8. 让独立 QA subagent 审核

QA 必须由另一个 subagent 做，不能自己审自己。QA 只判断问题，不直接改 annotation 文件。

通过标准是 `qa_status=pass` 且 `problem_count=0`。

### 9. QA 失败后选择修复方式

如果只是少量词有问题，例如网络核验不具体、单个标签不一致，可以做 targeted repair，只修问题行。

如果是系统性问题，例如整批模板化、很多语义误判、漏 ID、重复 ID、大量没有完成网络核验，就整批 full rerun。

修完后必须重新跑结构校验和 final QA。

### 10. 只合并 QA 通过的批次

不要把未通过 QA 的批次放进最终结果。把每个通过 final QA 的最终 annotation 文件放进 merge-ready 目录。

### 11. 合并后做覆盖检查

合并脚本必须对照源表检查：有没有漏词、重复词、未知 ID。

覆盖检查失败时，不进入最终交付。

### 12. 输出中文审阅表

最终给人工看的表使用中文列名和中文结论。优先输出 `.xlsx`，并确保每个 sheet 都可以筛选。

### 13. 人工审核

人工重点看：语义是否合理、风险词是否需要排除、品牌/平台/竞品是否符合项目范围、是否有需要合并或拆分的意图组。

## English Version

### 1. Prepare the raw keyword file

Place the raw keyword table somewhere the project can access. The file must include a keyword column. Keep original source fields such as volume, competition, or source when available.

### 2. Create the intake fact table

Run intake first. This step preserves the original keyword, creates stable IDs, and adds deterministic hint fields.

Important: intake is not the final semantic annotation. It is only a hint table.

### 3. Check the intake output

Confirm that the row count matches the source file. Spot-check several rows to make sure the original keywords were not rewritten.

### 4. Split into 200-keyword batches

Split the intake table into smaller batches. The default batch size is 200 keywords so annotation and QA stay manageable.

### 5. Annotate each batch

Ask the annotation subagent to process one batch at a time. It should decide the real meaning, search intent, risk, platform, brand, competitor, and other semantic fields for every keyword.

Use Chinese for review-facing content, but keep field names in English for script validation.

### 6. Search the web when verification is required

Use web search for unclear terms, brand/person/platform/competitor-like terms, risky terms, or terms flagged by QA.

Whenever `web_verification_required=yes`, the verification must actually be performed, and the conclusion must be specific.

### 7. Run structural validation

After annotation, run the validation script to catch missing rows, duplicate IDs, unknown IDs, missing fields, or invalid enum values.

If validation fails, fix the structure before QA.

### 8. Run independent QA

QA must be done by a different subagent. The QA subagent reviews the annotation and reports issues, but does not edit the annotation file directly.

A batch passes only when `qa_status=pass` and `problem_count=0`.

### 9. Choose targeted repair or full rerun

Use targeted repair for bounded row-level issues, such as a few weak web verification notes or inconsistent labels.

Use full rerun for systemic issues, such as templated annotations, many wrong judgments, missing IDs, duplicate IDs, or many required web verifications not performed.

After repair or rerun, run validation and final QA again.

### 10. Merge only QA-passed batches

Do not merge failed batches. Put only final-QA-passed annotation files into the merge-ready directory.

### 11. Run merge coverage checks

The merge script must compare merged annotations against the source table and check for missing keywords, duplicates, and unknown IDs.

If coverage fails, the output is not ready for delivery.

### 12. Export the Chinese review workbook

The final human review table should use Chinese column names and Chinese review conclusions. Prefer `.xlsx`, with filters enabled on every sheet.

### 13. Human review

The human reviewer should focus on semantic correctness, risky keywords, brand/platform/competitor fit, and whether intent groups should be merged or split.
