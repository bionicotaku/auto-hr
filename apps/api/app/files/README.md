# apps/api/app/files

本目录负责文件与临时目录处理。

- `temp_manager.py`：Candidate 导入临时上下文与清理
- `storage.py`：上传文件落盘
- `pdf_extract.py`：PDF 文本抽取

规则：

- 临时目录与正式目录分离
- 文件处理不包含 AI 业务逻辑
- 导入失败时必须可清理
