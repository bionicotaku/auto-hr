import type {
  CandidateDetailActionContextDto,
  CandidateDetailTagDto,
} from "@/lib/api/types";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";

type CandidateActionPanelProps = {
  actionContext: CandidateDetailActionContextDto;
  tags: CandidateDetailTagDto[];
};

function statusLabel(status: CandidateDetailActionContextDto["current_status"]) {
  if (status === "pending") {
    return "待处理";
  }
  if (status === "in_progress") {
    return "处理中";
  }
  if (status === "rejected") {
    return "已淘汰";
  }
  if (status === "offer_sent") {
    return "已发 Offer";
  }
  return "已录用";
}

function draftTypeLabel(draftType: "reject" | "advance" | "offer" | "other") {
  if (draftType === "reject") {
    return "拒绝";
  }
  if (draftType === "advance") {
    return "推进";
  }
  if (draftType === "offer") {
    return "Offer";
  }
  return "其他";
}

export function CandidateActionPanel({ actionContext, tags }: CandidateActionPanelProps) {
  return (
    <Card className="space-y-5">
      <div className="space-y-1">
        <h2 className="text-lg font-semibold tracking-tight text-slate-950">处理状态</h2>
        <p className="text-sm leading-6 text-slate-600">查看当前状态、已有标签、备注记录和邮件草稿。</p>
      </div>

      <div className="grid gap-4 xl:grid-cols-[0.78fr_1.22fr]">
        <div className="space-y-4">
          <div className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-4">
            <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">当前状态</p>
            <p className="mt-2 text-lg font-semibold text-slate-950">{statusLabel(actionContext.current_status)}</p>
          </div>

          <div className="space-y-2">
            <p className="text-sm font-medium text-slate-900">标签</p>
            {tags.length > 0 ? (
              <div className="flex flex-wrap gap-2">
                {tags.map((tag) => (
                  <span
                    key={tag.id}
                    className="rounded-full bg-slate-100 px-3 py-1 text-xs text-slate-600"
                  >
                    {tag.name}
                  </span>
                ))}
              </div>
            ) : (
              <p className="text-sm leading-6 text-slate-600">当前没有标签。</p>
            )}
          </div>

          <div className="flex flex-wrap gap-3">
            <Button variant="secondary" disabled>
              更新状态
            </Button>
            <Button variant="secondary" disabled>
              添加标签
            </Button>
            <Button variant="secondary" disabled>
              记录备注
            </Button>
            <Button disabled>生成邮件草稿</Button>
          </div>
        </div>

        <div className="grid gap-4 lg:grid-cols-2">
          <div className="space-y-3 rounded-2xl border border-slate-200 bg-white px-4 py-4">
            <p className="text-sm font-medium text-slate-900">备注记录</p>
            {actionContext.feedbacks.length > 0 ? (
              <div className="space-y-3">
                {actionContext.feedbacks.map((feedback) => (
                  <div key={feedback.id} className="rounded-2xl bg-slate-50 px-3 py-3">
                    <div className="flex items-center justify-between gap-3">
                      <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">
                        {feedback.author_name || "未署名"}
                      </p>
                      <p className="text-xs text-slate-500">
                        {new Date(feedback.created_at).toLocaleString("zh-CN")}
                      </p>
                    </div>
                    <p className="mt-2 text-sm leading-6 text-slate-700">{feedback.note_text}</p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm leading-6 text-slate-600">当前还没有备注记录。</p>
            )}
          </div>

          <div className="space-y-3 rounded-2xl border border-slate-200 bg-white px-4 py-4">
            <p className="text-sm font-medium text-slate-900">邮件草稿</p>
            {actionContext.email_drafts.length > 0 ? (
              <div className="space-y-3">
                {actionContext.email_drafts.map((draft) => (
                  <div key={draft.id} className="rounded-2xl bg-slate-50 px-3 py-3">
                    <div className="flex items-center justify-between gap-3">
                      <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">
                        {draftTypeLabel(draft.draft_type)}
                      </p>
                      <p className="text-xs text-slate-500">
                        {new Date(draft.updated_at).toLocaleString("zh-CN")}
                      </p>
                    </div>
                    <p className="mt-2 text-sm font-medium text-slate-900">{draft.subject}</p>
                    <p className="mt-2 text-sm leading-6 text-slate-700">{draft.body}</p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm leading-6 text-slate-600">当前还没有邮件草稿。</p>
            )}
          </div>
        </div>
      </div>
    </Card>
  );
}
