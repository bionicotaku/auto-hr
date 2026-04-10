 "use client";

import { AppShell } from "@/components/layout/AppShell";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Spinner } from "@/components/ui/Spinner";
import { getJobApiErrorMessage } from "@/lib/api/jobs";
import { useJobsQuery } from "@/lib/query/jobs";

export function JobsOverview() {
  const jobsQuery = useJobsQuery();

  return (
    <AppShell
      title="岗位"
      description="创建并维护岗位定义，统一职位描述和评估规范。"
      actions={
        <Button href="/jobs/new" size="lg">
          新建岗位
        </Button>
      }
    >
      {jobsQuery.isLoading ? (
        <Card className="flex min-h-[280px] items-center justify-center">
          <div className="inline-flex items-center gap-2 text-sm text-slate-600">
            <Spinner className="h-4 w-4 border-slate-300 border-t-slate-800" />
            正在加载岗位列表
          </div>
        </Card>
      ) : jobsQuery.isError ? (
        <Card className="space-y-2">
          <h2 className="text-lg font-semibold tracking-tight text-slate-950">加载失败</h2>
          <p className="text-sm leading-7 text-slate-600">{getJobApiErrorMessage(jobsQuery.error)}</p>
        </Card>
      ) : jobsQuery.data && jobsQuery.data.items.length > 0 ? (
        <div className="grid gap-5 lg:grid-cols-2">
          {jobsQuery.data.items.map((job) => {
            return (
              <Card key={job.job_id} className="flex min-h-[240px] flex-col justify-between">
                <div className="space-y-4">
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <span className="rounded-xl bg-slate-100 px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-slate-600">
                        已生效
                      </span>
                      <span className="text-xs text-slate-500">
                        {new Date(job.updated_at).toLocaleDateString("zh-CN")}
                      </span>
                    </div>
                    <h2 className="text-xl font-semibold tracking-tight text-slate-950">{job.title}</h2>
                    <p className="text-sm leading-7 text-slate-600">{job.summary}</p>
                  </div>
                  <div className="flex flex-wrap gap-3 text-sm text-slate-600">
                    <span>{job.candidate_count} 位候选人</span>
                    <span>最近更新 {new Date(job.updated_at).toLocaleTimeString("zh-CN", { hour: "2-digit", minute: "2-digit" })}</span>
                  </div>
                </div>
                <div className="flex flex-wrap gap-3 pt-5">
                  <Button href={`/jobs/${job.job_id}`}>进入岗位</Button>
                  <Button href={`/jobs/${job.job_id}/candidates/new`} variant="secondary">
                    添加候选人
                  </Button>
                </div>
              </Card>
            );
          })}
        </div>
      ) : (
        <div className="grid gap-6 xl:grid-cols-[1.4fr_0.9fr]">
          <Card className="flex min-h-[320px] flex-col justify-between">
            <div className="space-y-3">
              <h2 className="text-xl font-semibold tracking-tight text-slate-950">还没有岗位</h2>
              <p className="max-w-xl text-sm leading-7 text-slate-600">
                从一个新岗位开始。你可以直接导入已有职位描述，也可以先填写岗位信息，再进入统一编辑页继续完善。
              </p>
            </div>

            <div className="flex flex-wrap gap-3">
              <Button href="/jobs/new" size="lg">
                新建岗位
              </Button>
            </div>
          </Card>

          <Card className="space-y-4">
            <div className="space-y-2">
              <h2 className="text-lg font-semibold tracking-tight text-slate-950">开始方式</h2>
              <p className="text-sm leading-7 text-slate-600">选择最适合当前场景的入口，先拿到岗位初稿，再进入编辑工作区。</p>
            </div>

            <div className="space-y-3">
              <div className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-4">
                <p className="text-sm font-semibold text-slate-900">导入职位描述</p>
                <p className="mt-1 text-sm leading-6 text-slate-600">适合已经有现成 JD 的岗位。</p>
              </div>
              <div className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-4">
                <p className="text-sm font-semibold text-slate-900">填写岗位信息</p>
                <p className="mt-1 text-sm leading-6 text-slate-600">适合先从岗位名称、地点和要求起步。</p>
              </div>
            </div>
          </Card>
        </div>
      )}
    </AppShell>
  );
}
