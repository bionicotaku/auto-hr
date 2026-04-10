"use client";

import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";

import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { Select } from "@/components/ui/Select";
import { Spinner } from "@/components/ui/Spinner";
import { Textarea } from "@/components/ui/Textarea";
import { getJobApiErrorMessage } from "@/lib/api/jobs";
import { useCreateJobFromFormMutation } from "@/lib/query/job-mutations";

const EMPLOYMENT_TYPE_OPTIONS = [
  { value: "full_time", label: "全职" },
  { value: "part_time", label: "兼职" },
  { value: "contract", label: "合同工" },
  { value: "internship", label: "实习" },
  { value: "temporary", label: "临时" },
];

const WORK_MODE_OPTIONS = [
  { value: "onsite", label: "线下办公" },
  { value: "hybrid", label: "混合办公" },
  { value: "remote", label: "远程办公" },
];

type FormState = {
  title: string;
  department: string;
  location: string;
  employmentType: string;
  seniorityTarget: string;
  requiredExperienceSummary: string;
  preferredExperienceSummary: string;
  onsiteRemoteMode: string;
};

const initialFormState: FormState = {
  title: "",
  department: "",
  location: "",
  employmentType: "full_time",
  seniorityTarget: "",
  requiredExperienceSummary: "",
  preferredExperienceSummary: "",
  onsiteRemoteMode: "hybrid",
};

export function JobFormDraftForm() {
  const router = useRouter();
  const mutation = useCreateJobFromFormMutation();
  const [formState, setFormState] = useState<FormState>(initialFormState);
  const [submitError, setSubmitError] = useState<string | null>(null);

  const isSubmitting = mutation.isPending;

  function updateField<K extends keyof FormState>(field: K, value: FormState[K]) {
    setFormState((current) => ({ ...current, [field]: value }));
    if (submitError) {
      setSubmitError(null);
    }
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!formState.title.trim() || !formState.department.trim() || !formState.location.trim() || !formState.seniorityTarget.trim()) {
      setSubmitError("请至少填写岗位名称、部门、地点和目标资历。");
      return;
    }

    try {
      setSubmitError(null);
      const result = await mutation.mutateAsync({
        job_title: formState.title.trim(),
        department: formState.department.trim(),
        location: formState.location.trim(),
        employment_type: formState.employmentType,
        seniority_level: formState.seniorityTarget.trim(),
        business_context: formState.preferredExperienceSummary.trim()
          ? `办公方式：${formState.onsiteRemoteMode}；偏好经验：${formState.preferredExperienceSummary.trim()}`
          : `办公方式：${formState.onsiteRemoteMode}`,
        requirements_summary: formState.requiredExperienceSummary.trim() || undefined,
      });
      // 成功后只做跳转，不在前端缓存 draft 结果。
      router.push(`/jobs/${result.jobId}/edit`);
    } catch (error) {
      setSubmitError(getJobApiErrorMessage(error));
    }
  }

  return (
    <main className="relative min-h-screen overflow-hidden bg-[radial-gradient(circle_at_top_left,_rgba(14,165,233,0.18),_transparent_28%),radial-gradient(circle_at_top_right,_rgba(16,185,129,0.18),_transparent_30%),linear-gradient(180deg,_#f7fbf8_0%,_#eef6ff_48%,_#f7f7f1_100%)] px-6 py-10 text-slate-950 sm:px-10 lg:px-12">
      <div className="absolute inset-x-0 top-0 h-52 bg-[linear-gradient(90deg,_rgba(255,255,255,0.5),_rgba(255,255,255,0.08),_rgba(255,255,255,0.5))] blur-3xl" />

      <div className="relative mx-auto flex w-full max-w-5xl flex-col gap-8">
        <section className="grid gap-6 rounded-[32px] border border-white/70 bg-white/78 p-8 shadow-[0_30px_80px_rgba(15,23,42,0.10)] backdrop-blur xl:p-10">
          <div className="flex flex-wrap items-center gap-3">
            <Badge tone="success">基础信息生成</Badge>
            <Badge tone="neutral">draft 创建</Badge>
          </div>

          <div className="space-y-4">
            <p className="text-sm font-semibold uppercase tracking-[0.28em] text-emerald-700">
              Structured input
            </p>
            <h1 className="text-4xl font-semibold tracking-tight text-slate-950 sm:text-5xl">
              填写岗位基础信息，系统生成 draft Job 后进入编辑页。
            </h1>
            <p className="max-w-3xl text-base leading-7 text-slate-600 sm:text-lg">
              这一页只保存当前表单状态，提交失败会保留所有输入值。成功后直接跳转到 `/jobs/[jobId]/edit`。
            </p>
          </div>
        </section>

        <Card className="space-y-8">
          <form className="space-y-8" onSubmit={handleSubmit}>
            <div className="grid gap-5 md:grid-cols-2">
              <div className="space-y-3">
                <label className="text-sm font-semibold text-slate-800" htmlFor="job-title">
                  岗位名称
                </label>
                <Input
                  id="job-title"
                  placeholder="例如：Senior Frontend Engineer"
                  value={formState.title}
                  onChange={(event) => updateField("title", event.target.value)}
                />
              </div>

              <div className="space-y-3">
                <label className="text-sm font-semibold text-slate-800" htmlFor="job-department">
                  部门
                </label>
                <Input
                  id="job-department"
                  placeholder="例如：Platform / Product / Growth"
                  value={formState.department}
                  onChange={(event) => updateField("department", event.target.value)}
                />
              </div>

              <div className="space-y-3">
                <label className="text-sm font-semibold text-slate-800" htmlFor="job-location">
                  地点
                </label>
                <Input
                  id="job-location"
                  placeholder="例如：New York / Shanghai / Remote"
                  value={formState.location}
                  onChange={(event) => updateField("location", event.target.value)}
                />
              </div>

              <div className="space-y-3">
                <label className="text-sm font-semibold text-slate-800" htmlFor="job-employment-type">
                  雇佣类型
                </label>
                <Select
                  id="job-employment-type"
                  value={formState.employmentType}
                  onChange={(event) => updateField("employmentType", event.target.value)}
                >
                  {EMPLOYMENT_TYPE_OPTIONS.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </Select>
              </div>

              <div className="space-y-3">
                <label className="text-sm font-semibold text-slate-800" htmlFor="job-seniority-target">
                  目标资历
                </label>
                <Input
                  id="job-seniority-target"
                  placeholder="例如：Senior / Staff / 3-5 years"
                  value={formState.seniorityTarget}
                  onChange={(event) => updateField("seniorityTarget", event.target.value)}
                />
              </div>

              <div className="space-y-3">
                <label className="text-sm font-semibold text-slate-800" htmlFor="job-work-mode">
                  办公方式
                </label>
                <Select
                  id="job-work-mode"
                  value={formState.onsiteRemoteMode}
                  onChange={(event) => updateField("onsiteRemoteMode", event.target.value)}
                >
                  {WORK_MODE_OPTIONS.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </Select>
              </div>
            </div>

            <div className="grid gap-5 lg:grid-cols-2">
              <div className="space-y-3">
                <label className="text-sm font-semibold text-slate-800" htmlFor="required-experience-summary">
                  必要经验摘要
                </label>
                <Textarea
                  id="required-experience-summary"
                  placeholder="例如：需要有 B2B SaaS / React / TypeScript 经验。"
                  value={formState.requiredExperienceSummary}
                  onChange={(event) => updateField("requiredExperienceSummary", event.target.value)}
                />
              </div>

              <div className="space-y-3">
                <label className="text-sm font-semibold text-slate-800" htmlFor="preferred-experience-summary">
                  偏好经验摘要
                </label>
                <Textarea
                  id="preferred-experience-summary"
                  placeholder="例如：希望有 AI 产品、招聘产品或设计系统经验。"
                  value={formState.preferredExperienceSummary}
                  onChange={(event) => updateField("preferredExperienceSummary", event.target.value)}
                />
              </div>
            </div>

            {submitError ? (
              <div
                aria-live="polite"
                className="rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm leading-6 text-rose-700"
              >
                {submitError}
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
