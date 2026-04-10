# auto-hr

## 开发约定

本仓库所有 Python 相关命令统一通过仓库根目录虚拟环境运行，不在 `apps/api` 内单独创建虚拟环境。

- 虚拟环境路径：`./.venv`
- Python 可执行文件：`./.venv/bin/python`
- Pip 可执行文件：`./.venv/bin/pip`

常用命令示例：

```bash
./scripts/bootstrap.sh
./.venv/bin/python -V
./.venv/bin/pip install -e apps/api
```

## 文档目录

设计、架构、规范、实施类文档统一放在 [`docs/`](/Users/evan/Downloads/auto-hr/docs/README.md)。
各工程目录自己的 `README.md` 保留在目录内部，用于说明该目录职责、关键文件和局部约束。

补充约束：

- 用户界面不得展示技术实现细节，这类内容只允许留在 `docs/` 或工程目录 `README.md`
- 如果使用子 agent，统一只允许 `gpt-5.4`

- [文档索引](/Users/evan/Downloads/auto-hr/docs/README.md)
- [工程实现文档](/Users/evan/Downloads/auto-hr/docs/工程实现文档.md)
- [实施步骤文档](/Users/evan/Downloads/auto-hr/docs/实施步骤文档.md)
