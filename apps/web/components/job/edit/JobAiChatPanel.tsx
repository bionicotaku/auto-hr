import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Spinner } from "@/components/ui/Spinner";
import { Textarea } from "@/components/ui/Textarea";
import type { JobEditorMessageDto } from "@/lib/api/types";

type JobAiChatPanelProps = {
  messages: JobEditorMessageDto[];
  inputValue: string;
  errorMessage: string | null;
  isChatPending: boolean;
  isAgentPending: boolean;
  onInputChange: (value: string) => void;
  onChatSubmit: () => void;
  onAgentSubmit: () => void;
};

const roleLabelMap: Record<JobEditorMessageDto["role"], string> = {
  user: "你",
  assistant: "AI",
  system: "系统",
};

export function JobAiChatPanel({
  messages,
  inputValue,
  errorMessage,
  isChatPending,
  isAgentPending,
  onInputChange,
  onChatSubmit,
  onAgentSubmit,
}: JobAiChatPanelProps) {
  return (
    <Card className="space-y-4">
      <div className="space-y-2">
        <p className="text-xs font-semibold uppercase tracking-[0.24em] text-[var(--foreground-muted)]">
          AI workspace
        </p>
        <h2 className="text-lg font-semibold tracking-tight text-[var(--foreground)]">修改要求</h2>
        <p className="text-sm leading-6 text-[var(--foreground-soft)]">
          获取建议，或直接让系统生成一版新的岗位定义并覆盖当前内容。
        </p>
      </div>

      <div className="min-h-[220px] space-y-3 rounded-[24px] border border-[var(--border)] bg-[var(--panel-muted)] px-4 py-4">
        {messages.length === 0 ? (
          <p className="text-sm leading-6 text-[var(--foreground-muted)]">暂无消息。</p>
        ) : (
          messages.map((message, index) => (
            <div
              key={`${message.role}-${index}`}
              className="rounded-[22px] border border-[var(--border)] bg-[var(--panel-strong)] px-4 py-3"
            >
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--foreground-muted)]">
                {roleLabelMap[message.role]}
              </p>
              <p className="mt-2 whitespace-pre-wrap text-sm leading-6 text-[var(--foreground-soft)]">
                {message.content}
              </p>
            </div>
          ))
        )}
      </div>

      <Textarea
        aria-label="修改要求输入框"
        className="min-h-[180px] bg-slate-50"
        placeholder="例如：把必须项单独列出，并弱化不必要的加分要求。"
        value={inputValue}
        onChange={(event) => onInputChange(event.target.value)}
      />

      {errorMessage ? (
        <div className="rounded-[24px] border border-[var(--border)] bg-[var(--accent-danger)] px-4 py-3 text-sm leading-6 text-[var(--foreground)]">
          {errorMessage}
        </div>
      ) : null}

      <div className="flex flex-wrap gap-3">
        <Button onClick={onChatSubmit} disabled={isChatPending || isAgentPending}>
          {isChatPending ? (
            <span className="inline-flex items-center gap-2">
              <Spinner className="h-4 w-4 border-white/30 border-t-white" />
              生成建议中
            </span>
          ) : (
            "获取建议"
          )}
        </Button>
        <Button variant="secondary" onClick={onAgentSubmit} disabled={isChatPending || isAgentPending}>
          {isAgentPending ? (
            <span className="inline-flex items-center gap-2">
              <Spinner className="h-4 w-4 border-slate-300 border-t-slate-800" />
              生成新版中
            </span>
          ) : (
            "生成新版"
          )}
        </Button>
      </div>
    </Card>
  );
}
