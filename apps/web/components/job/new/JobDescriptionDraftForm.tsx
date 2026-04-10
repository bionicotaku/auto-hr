"use client";

import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";

import { AppShell } from "@/components/layout/AppShell";
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
  const canSubmit = description.trim().length > 0;
  const errorMessage = submitError;

  function handleBack() {
    router.push("/jobs/new");
  }

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
    <AppShell
      title="导入职位描述"
      description="粘贴已有职位描述，生成岗位初稿。"
      backHref="/jobs/new"
      actions={
        <Button variant="secondary" onClick={handleBack}>
          返回
        </Button>
      }
      className="max-w-4xl"
    >
      <div className="grid gap-6 xl:grid-cols-[1.05fr_0.95fr]">
        <Card className="space-y-6">
          <div className="space-y-2">
            <p className="text-xs font-semibold uppercase tracking-[0.24em] text-[var(--foreground-muted)]">
              Form workspace
            </p>
            <h2 className="text-lg font-semibold tracking-tight text-[var(--foreground)]">职位描述</h2>
            <p className="text-sm leading-6 text-[var(--foreground-soft)]">
              建议包含岗位职责、任职要求、地点和工作方式。
            </p>
          </div>

          <form className="space-y-6" onSubmit={handleSubmit}>
            <div className="space-y-3">
              <label className="text-sm font-semibold text-[var(--foreground)]" htmlFor="job-description">
                职位描述
              </label>
              <Textarea
                id="job-description"
                placeholder="粘贴完整的职位描述。"
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
                className="rounded-[24px] border border-[var(--border)] bg-[var(--accent-danger)] px-4 py-3 text-sm leading-6 text-[var(--foreground)]"
              >
                {errorMessage}
              </div>
            ) : null}

            <div className="flex flex-wrap gap-3">
              <Button type="submit" disabled={isSubmitting || !canSubmit}>
                {isSubmitting ? (
                  <span className="inline-flex items-center gap-2">
                    <Spinner className="h-4 w-4 border-white/30 border-t-white" />
                    生成中
                  </span>
                ) : (
                  "生成岗位初稿"
                )}
              </Button>
              <Button type="button" variant="secondary" onClick={handleBack}>
                返回
              </Button>
            </div>
          </form>
        </Card>

        <Card tone="muted" className="space-y-4">
          <div className="space-y-2">
            <h2 className="text-lg font-semibold tracking-tight text-[var(--foreground)]">填写建议</h2>
            <p className="text-sm leading-7 text-[var(--foreground-soft)]">
              文本越完整，系统越容易生成可直接进入编辑页的岗位初稿。
            </p>
          </div>

          <div className="space-y-3">
            {[
              "优先包含岗位职责、任职要求、地点与办公方式。",
              "如果已有团队背景或业务目标，也可以一并粘贴。",
              "生成失败时不清空输入，便于直接补充后再次提交。",
            ].map((item) => (
              <div
                key={item}
                className="rounded-[22px] border border-[var(--border)] bg-[var(--panel-strong)] px-4 py-4 text-sm leading-6 text-[var(--foreground-soft)]"
              >
                {item}
              </div>
            ))}
          </div>
        </Card>
      </div>
    </AppShell>
  );
}
