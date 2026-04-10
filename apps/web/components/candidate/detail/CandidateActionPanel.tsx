import { useEffect, useState } from "react";

import { useQueryClient } from "@tanstack/react-query";

import type {
  CandidateDetailActionContextDto,
  CandidateDetailTagDto,
} from "@/lib/api/types";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Select } from "@/components/ui/Select";
import { Spinner } from "@/components/ui/Spinner";
import { Textarea } from "@/components/ui/Textarea";
import { getJobApiErrorMessage } from "@/lib/api/jobs";
import {
  useCandidateEmailDraftMutation,
  useCandidateFeedbackMutation,
  useCandidateStatusMutation,
  useCandidateTagMutation,
} from "@/lib/query/candidates";

type CandidateActionPanelProps = {
  candidateId: string;
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

export function CandidateActionPanel({ candidateId, actionContext, tags }: CandidateActionPanelProps) {
  const queryClient = useQueryClient();
  const statusMutation = useCandidateStatusMutation(candidateId);
  const tagMutation = useCandidateTagMutation(candidateId);
  const feedbackMutation = useCandidateFeedbackMutation(candidateId);
  const emailDraftMutation = useCandidateEmailDraftMutation(candidateId);

  const [statusValue, setStatusValue] = useState(actionContext.current_status);
  const [tagName, setTagName] = useState("");
  const [noteText, setNoteText] = useState("");
  const [authorName, setAuthorName] = useState("");
  const [draftType, setDraftType] = useState<"reject" | "advance" | "offer" | "other">("advance");
  const [statusError, setStatusError] = useState<string | null>(null);
  const [tagError, setTagError] = useState<string | null>(null);
  const [feedbackError, setFeedbackError] = useState<string | null>(null);
  const [draftError, setDraftError] = useState<string | null>(null);

  useEffect(() => {
    setStatusValue(actionContext.current_status);
  }, [actionContext.current_status]);

  async function refreshDetail() {
    await queryClient.invalidateQueries({ queryKey: ["candidate-detail", candidateId] });
  }

  async function handleStatusUpdate() {
    try {
      setStatusError(null);
      await statusMutation.mutateAsync({ current_status: statusValue });
      await refreshDetail();
    } catch (error) {
      setStatusError(getJobApiErrorMessage(error));
    }
  }

  async function handleAddTag() {
    try {
      setTagError(null);
      await tagMutation.mutateAsync({ tag_name: tagName });
      setTagName("");
      await refreshDetail();
    } catch (error) {
      setTagError(getJobApiErrorMessage(error));
    }
  }

  async function handleAddFeedback() {
    try {
      setFeedbackError(null);
      await feedbackMutation.mutateAsync({
        note_text: noteText,
        author_name: authorName || null,
      });
      setNoteText("");
      setAuthorName("");
      await refreshDetail();
    } catch (error) {
      setFeedbackError(getJobApiErrorMessage(error));
    }
  }

  async function handleCreateEmailDraft() {
    try {
      setDraftError(null);
      await emailDraftMutation.mutateAsync({ draft_type: draftType });
      await refreshDetail();
    } catch (error) {
      setDraftError(getJobApiErrorMessage(error));
    }
  }

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

          <div className="space-y-3 rounded-2xl border border-slate-200 bg-white px-4 py-4">
            <label className="text-sm font-medium text-slate-900" htmlFor="candidate-status-select">
              更新状态
            </label>
            <Select
              id="candidate-status-select"
              aria-label="候选人状态选择"
              value={statusValue}
              onChange={(event) => setStatusValue(event.target.value as typeof statusValue)}
              disabled={statusMutation.isPending}
            >
              <option value="pending">待处理</option>
              <option value="in_progress">处理中</option>
              <option value="rejected">已淘汰</option>
              <option value="offer_sent">已发 Offer</option>
              <option value="hired">已录用</option>
            </Select>
            {statusError ? <p className="text-sm leading-6 text-rose-700">{statusError}</p> : null}
            <Button
              variant="secondary"
              onClick={handleStatusUpdate}
              disabled={statusMutation.isPending || statusValue === actionContext.current_status}
            >
              {statusMutation.isPending ? (
                <span className="inline-flex items-center gap-2">
                  <Spinner className="h-4 w-4 border-slate-300 border-t-slate-800" />
                  更新中
                </span>
              ) : (
                "更新状态"
              )}
            </Button>
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

          <div className="space-y-3 rounded-2xl border border-slate-200 bg-white px-4 py-4">
            <label className="text-sm font-medium text-slate-900" htmlFor="candidate-tag-input">
              添加标签
            </label>
            <input
              id="candidate-tag-input"
              aria-label="人工标签输入框"
              className="h-11 w-full rounded-xl border border-slate-200 bg-white px-4 text-sm text-slate-950 shadow-sm outline-none transition focus:border-emerald-500 focus:ring-4 focus:ring-emerald-100"
              value={tagName}
              onChange={(event) => setTagName(event.target.value)}
              disabled={tagMutation.isPending}
              placeholder="输入人工标签"
            />
            {tagError ? <p className="text-sm leading-6 text-rose-700">{tagError}</p> : null}
            <Button
              variant="secondary"
              onClick={handleAddTag}
              disabled={tagMutation.isPending || !tagName.trim()}
            >
              {tagMutation.isPending ? (
                <span className="inline-flex items-center gap-2">
                  <Spinner className="h-4 w-4 border-slate-300 border-t-slate-800" />
                  添加中
                </span>
              ) : (
                "添加标签"
              )}
            </Button>
          </div>

          <div className="space-y-3 rounded-2xl border border-slate-200 bg-white px-4 py-4">
            <label className="text-sm font-medium text-slate-900" htmlFor="candidate-draft-type-select">
              生成邮件草稿
            </label>
            <Select
              id="candidate-draft-type-select"
              aria-label="邮件草稿类型选择"
              value={draftType}
              onChange={(event) => setDraftType(event.target.value as typeof draftType)}
              disabled={emailDraftMutation.isPending}
            >
              <option value="advance">推进</option>
              <option value="reject">拒绝</option>
              <option value="offer">Offer</option>
              <option value="other">其他</option>
            </Select>
            {draftError ? <p className="text-sm leading-6 text-rose-700">{draftError}</p> : null}
            <Button onClick={handleCreateEmailDraft} disabled={emailDraftMutation.isPending}>
              {emailDraftMutation.isPending ? (
                <span className="inline-flex items-center gap-2">
                  <Spinner className="h-4 w-4 border-white/30 border-t-white" />
                  生成中
                </span>
              ) : (
                "生成邮件草稿"
              )}
            </Button>
          </div>
        </div>

        <div className="grid gap-4 lg:grid-cols-2">
          <div className="space-y-3 rounded-2xl border border-slate-200 bg-white px-4 py-4">
            <div className="space-y-3 rounded-2xl border border-slate-200 bg-slate-50 px-3 py-3">
              <label className="text-sm font-medium text-slate-900" htmlFor="candidate-feedback-author">
                备注署名
              </label>
              <input
                id="candidate-feedback-author"
                aria-label="备注署名输入框"
                className="h-11 w-full rounded-xl border border-slate-200 bg-white px-4 text-sm text-slate-950 shadow-sm outline-none transition focus:border-emerald-500 focus:ring-4 focus:ring-emerald-100"
                value={authorName}
                onChange={(event) => setAuthorName(event.target.value)}
                disabled={feedbackMutation.isPending}
                placeholder="可选"
              />
              <label className="text-sm font-medium text-slate-900" htmlFor="candidate-feedback-note">
                添加备注
              </label>
              <Textarea
                id="candidate-feedback-note"
                aria-label="备注输入框"
                className="min-h-[140px] bg-white"
                value={noteText}
                onChange={(event) => setNoteText(event.target.value)}
                disabled={feedbackMutation.isPending}
              />
              {feedbackError ? <p className="text-sm leading-6 text-rose-700">{feedbackError}</p> : null}
              <Button
                variant="secondary"
                onClick={handleAddFeedback}
                disabled={feedbackMutation.isPending || !noteText.trim()}
              >
                {feedbackMutation.isPending ? (
                  <span className="inline-flex items-center gap-2">
                    <Spinner className="h-4 w-4 border-slate-300 border-t-slate-800" />
                    保存中
                  </span>
                ) : (
                  "记录备注"
                )}
              </Button>
            </div>

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
