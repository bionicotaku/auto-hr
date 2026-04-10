# apps/web/components/ui

基础 UI 组件目录。

当前已有：

- `Button.tsx`
- `Input.tsx`
- `Textarea.tsx`
- `Select.tsx`
- `Card.tsx`
- `Badge.tsx`
- `Spinner.tsx`
- `ErrorStateCard.tsx`
- `AnalysisProgressCard.tsx`

规则：

- 组件 API 简洁
- 风格统一、现代、可复用
- 统一依赖全局 theme tokens 输出 light / dark 视觉
- 不放 Job 或 Candidate 业务逻辑
- `Badge.tsx` 负责统一 mint / lime / blue / amber / orange / red / neutral 这几类彩色标签风格，业务页不要继续单独手写另一套彩色 pill
