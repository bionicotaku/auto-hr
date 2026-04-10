"use client";

import Link from "next/link";

import { AppShell } from "@/components/layout/AppShell";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { ErrorStateCard } from "@/components/ui/ErrorStateCard";
import { Spinner } from "@/components/ui/Spinner";
import { getJobApiErrorMessage } from "@/lib/api/jobs";
import { useJobsQuery } from "@/lib/query/jobs";

export function JobsOverview() {
  const jobsQuery = useJobsQuery();
  const jobCount = jobsQuery.data?.items.length ?? 0;

  return (
    <AppShell
      title="岗位"
      description="创建并维护岗位定义，统一职位描述和评估规范。"
      backHref="/"
      actions={
        <div className="flex items-end gap-3">
          <div className="min-w-[132px] rounded-[24px] border border-[var(--border)] bg-[var(--panel-muted)] px-4 py-3">
            <p className="text-center text-xs font-semibold uppercase tracking-[0.2em] text-[var(--foreground-muted)]">
              已生效岗位
            </p>
            <p className="mt-2 text-center text-2xl font-semibold text-[var(--foreground)]">{jobCount}</p>
          </div>
          <Button href="/jobs/new" size="lg">
            新建岗位
          </Button>
        </div>
      }
    >
      {jobsQuery.isLoading ? (
        <Card className="flex min-h-[280px] items-center justify-center">
          <div className="inline-flex items-center gap-2 text-sm text-[var(--foreground-soft)]">
            <Spinner className="h-4 w-4" />
            正在加载岗位列表
          </div>
        </Card>
      ) : jobsQuery.isError ? (
        <ErrorStateCard
          message={getJobApiErrorMessage(jobsQuery.error)}
          actionLabel="重试"
          onAction={() => {
            void jobsQuery.refetch();
          }}
        />
      ) : jobsQuery.data && jobsQuery.data.items.length > 0 ? (
        <div className="grid gap-5 lg:grid-cols-2">
          {jobsQuery.data.items.map((job) => {
            return (
              <Link
                key={job.job_id}
                aria-label={`进入岗位：${job.title}`}
                className="group block rounded-[28px] focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-[var(--ring)]"
                href={`/jobs/${job.job_id}`}
              >
                <Card className="flex min-h-[250px] flex-col justify-between gap-6 transition-transform duration-300 ease-out group-hover:-translate-y-1 group-hover:border-[var(--border-strong)] group-hover:shadow-[var(--shadow-shell)] motion-reduce:transform-none motion-reduce:transition-none motion-reduce:group-hover:translate-y-0">
                  <div className="space-y-4">
                    <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                      <div className="flex flex-wrap items-center gap-2">
                        <Badge tone="mint">
                          已生效
                        </Badge>
                        <span className="text-xs text-[var(--foreground-muted)]">
                          {new Date(job.updated_at).toLocaleDateString("zh-CN")}
                        </span>
                      </div>
                      <div className="sm:text-right">
                        <Badge tone="blue">
                          {job.candidate_count} 位候选人
                        </Badge>
                      </div>
                    </div>

                    <div className="space-y-3">
                      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                        <h2 className="text-xl font-semibold tracking-tight text-[var(--foreground)]">
                          {job.title}
                        </h2>
                      </div>
                      <p className="text-sm leading-7 text-[var(--foreground-soft)]">{job.summary}</p>
                    </div>
                  </div>
                </Card>
              </Link>
            );
          })}
        </div>
      ) : (
        <div className="grid gap-6 xl:grid-cols-[1.4fr_0.9fr]">
          <Card className="flex min-h-[320px] flex-col justify-between gap-6">
            <div className="space-y-3">
              <p className="text-xs font-semibold uppercase tracking-[0.24em] text-[var(--foreground-muted)]">
                Empty state
              </p>
              <h2 className="text-xl font-semibold tracking-tight text-[var(--foreground)]">还没有岗位</h2>
              <p className="max-w-xl text-sm leading-7 text-[var(--foreground-soft)]">
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
              <h2 className="text-lg font-semibold tracking-tight text-[var(--foreground)]">开始方式</h2>
              <p className="text-sm leading-7 text-[var(--foreground-soft)]">
                选择最适合当前场景的入口，先拿到岗位初稿，再进入编辑工作区。
              </p>
            </div>

            <div className="space-y-3">
              <div className="rounded-[24px] border border-[var(--border)] bg-[var(--panel-muted)] px-4 py-4">
                <p className="text-sm font-semibold text-[var(--foreground)]">导入职位描述</p>
                <p className="mt-1 text-sm leading-6 text-[var(--foreground-soft)]">
                  适合已经有现成 JD 的岗位。
                </p>
              </div>
              <div className="rounded-[24px] border border-[var(--border)] bg-[var(--panel-muted)] px-4 py-4">
                <p className="text-sm font-semibold text-[var(--foreground)]">填写岗位信息</p>
                <p className="mt-1 text-sm leading-6 text-[var(--foreground-soft)]">
                  适合先从岗位名称、地点和要求起步。
                </p>
              </div>
            </div>
          </Card>
        </div>
      )}
    </AppShell>
  );
}
