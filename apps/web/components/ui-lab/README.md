# apps/web/components/ui-lab

静态 UI 方案预览组件目录。

当前职责：

- 承载 `/ui-lab` 使用的展示型组件
- 输出不依赖业务数据的布局、卡片和交互状态

规则：

- 不引入 Job / Candidate 业务语义
- 不接后端接口
- 这里只保留一套 canonical preview 组件，不保留并行实验版本
