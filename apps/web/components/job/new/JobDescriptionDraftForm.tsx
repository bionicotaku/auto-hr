"use client";

import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";

import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Spinner } from "@/components/ui/Spinner";
import { Textarea } from "@/components/ui/Textarea";
import { getJobApiErrorMessage } from "@/lib/api/jobs";
import { useCreateJobFromDescriptionMutation } from "@/lib/query/job-mutations";

export function JobDescriptionDraftForm() {
  const router = useRouter();
  const mutation = useCreateJobFromDescriptionMutation();
  const [description, setDescription] = useState("");
  const [submitError, setSubmitError] = useState<string | null>(null);

  const isSubmitting = mutation.isPending;
  const errorMessage = submitError;

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const trimmedDescription = description.trim();
    if (!trimmedDescription) {
      setSubmitError("请先输入已有工作描述。");
      return;
    }

    try {
      setSubmitError(null);
      const result = await mutation.mutateAsync({ description_text: trimmedDescription });
      // 跳转是唯一的成功收口，失败不清空用户输入。
      router.push(`/jobs/${result.jobId}/edit`);
    } catch (error) {
      setSubmitError(getJobApiErrorMessage(error));
    }
  }

  return (
    <main className="relative min-h-screen overflow-hidden bg-[radial-gradient(circle_at_top_left,_rgba(14,165,233,0.18),_transparent_28%),radial-gradient(circle_at_top_right,_rgba(16,185,129,0.18),_transparent_30%),linear-gradient(180deg,_#f7fbf8_0%,_#eef6ff_48%,_#f7f7f1_100%)] px-6 py-10 text-slate-950 sm:px-10 lg:px-12">
      <div className="absolute inset-x-0 top-0 h-52 bg-[linear-gradient(90deg,_rgba(255,255,255,0.5),_rgba(255,255,255,0.08),_rgba(255,255,255,0.5))] blur-3xl" />

      <div className="relative mx-auto flex w-full max-w-4xl flex-col gap-8">
        <section className="grid gap-6 rounded-[32px] border border-white/70 bg-white/78 p-8 shadow-[0_30px_80px_rgba(15,23,42,0.10)] backdrop-blur xl:p-10">
          <div className="flex flex-wrap items-center gap-3">
            <Badge tone="accent">已有描述导入</Badge>
            <Badge tone="neutral">draft 创建</Badge>
          </div>

          <div className="space-y-4">
            <p className="text-sm font-semibold uppercase tracking-[0.28em] text-emerald-700">
              Job creation
            </p>
            <h1 className="text-4xl font-semibold tracking-tight text-slate-950 sm:text-5xl">
              输入原始职位描述，系统会生成 draft Job 并跳转编辑页。
            </h1>
            <p className="max-w-2xl text-base leading-7 text-slate-600 sm:text-lg">
              失败时仅展示错误信息，输入内容会保留在当前页面，便于继续修改后重新提交。
            </p>
          </div>
        </section>

        <Card className="space-y-6">
          <form className="space-y-6" onSubmit={handleSubmit}>
            <div className="space-y-3">
              <label className="text-sm font-semibold text-slate-800" htmlFor="job-description">
                原始工作描述
              </label>
              <Textarea
                id="job-description"
                placeholder="粘贴完整的职位描述原文，包含岗位职责、要求和背景信息。"
                value={description}
                onChange={(event) => {
                  setDescription(event.target.value);
                  if (submitError) {
                    setSubmitError(null);
                  }
                }}
              />
            </div>

            {errorMessage ? (
              <div
                aria-live="polite"
                className="rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm leading-6 text-rose-700"
              >
                {errorMessage}
              </div>
            ) : null}

            <div className="flex flex-wrap gap-3">
              <Button type="submit" disabled={isSubmitting}>
                {isSubmitting ? (
                  <span className="inline-flex items-center gap-2">
                    <Spinner className="h-4 w-4 border-white/30 border-t-white" />
                    生成中
                  </span>
                ) : (
                  "生成"
                )}
              </Button>
              <Button
                type="button"
                variant="secondary"
                onClick={() => {
                  router.push("/jobs");
                }}
              >
                取消
              </Button>
            </div>
          </form>
        </Card>
      </div>
    </main>
  );
}
