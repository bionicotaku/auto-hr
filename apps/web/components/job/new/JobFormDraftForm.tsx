"use client";

import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";

import { AppShell } from "@/components/layout/AppShell";
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
      setSubmitError("请补全岗位名称、部门、地点和资历要求。");
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
      router.push(`/jobs/${result.jobId}/edit`);
    } catch (error) {
      setSubmitError(getJobApiErrorMessage(error));
    }
  }

  return (
    <AppShell
      title="填写岗位信息"
      description="先补全关键岗位信息，再生成岗位初稿。"
      actions={
        <Button href="/jobs/new" variant="secondary">
          返回
        </Button>
      }
      className="max-w-5xl"
    >
      <Card className="space-y-8">
        <div className="space-y-2">
          <h2 className="text-lg font-semibold tracking-tight text-slate-950">岗位信息</h2>
          <p className="text-sm leading-6 text-slate-600">先填最关键的岗位信息，其他内容进入编辑页后再继续调整。</p>
        </div>

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
                  用工类型
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
                  资历要求
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
                  必要要求
                </label>
                <Textarea
                  id="required-experience-summary"
                  placeholder="例如：需要有 React、TypeScript 或招聘相关经验。"
                  value={formState.requiredExperienceSummary}
                  onChange={(event) => updateField("requiredExperienceSummary", event.target.value)}
                />
              </div>

              <div className="space-y-3">
                <label className="text-sm font-semibold text-slate-800" htmlFor="preferred-experience-summary">
                  加分项
                </label>
                <Textarea
                  id="preferred-experience-summary"
                  placeholder="例如：有 AI 产品、招聘产品或设计系统经验。"
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
                  "生成岗位初稿"
                )}
              </Button>
              <Button
                type="button"
                variant="secondary"
                onClick={() => {
                  router.push("/jobs");
                }}
              >
                返回
              </Button>
            </div>
          </form>
      </Card>
    </AppShell>
  );
}
