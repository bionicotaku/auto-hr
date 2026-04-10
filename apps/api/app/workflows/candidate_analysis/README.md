# apps/api/app/workflows/candidate_analysis

Candidate 分析工作流目录。

- `import_prepare.py`：整理文本与临时文件输入
- `standardize.py`：做 Candidate 标准化
- `score_items.py`：并发逐项评分
- `summarize.py`：supervisor 汇总
- `persist.py`：把分析 bundle 和正式文件转换为可入库数据
