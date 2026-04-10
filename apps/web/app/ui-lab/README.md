# apps/web/app/ui-lab

独立视觉预览路由。

当前职责：

- `/ui-lab`：承载与当前业务流程解耦的 canonical 静态 UI 方案预览

规则：

- 这里只放 route-level page
- 不接业务 API
- 不承载 Job / Candidate 真值
- 组件实现继续下沉到 `components/ui-lab/`
