"use client";

import { useMemo } from "react";
import { usePathname, useRouter, useSearchParams } from "next/navigation";

import { AppShell } from "@/components/layout/AppShell";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { ErrorStateCard } from "@/components/ui/ErrorStateCard";
import { Spinner } from "@/components/ui/Spinner";
import { CandidateList } from "@/components/job/detail/CandidateList";
import { CandidateListToolbar } from "@/components/job/detail/CandidateListToolbar";
import { JobSummaryPanel } from "@/components/job/detail/JobSummaryPanel";
import { getJobApiErrorMessage } from "@/lib/api/jobs";
import { useJobCandidatesQuery, useJobDetailQuery } from "@/lib/query/jobs";
import type { JobCandidateListQueryDto } from "@/lib/api/types";

type JobDetailWorkspaceProps = {
  jobId: string;
};

function readCandidateQuery(searchParams: { get(name: string): string | null; getAll(name: string): string[] }): JobCandidateListQueryDto {
  const sort = searchParams.get("sort");
  const status = searchParams.get("status");
  const q = searchParams.get("q") ?? "";
  const tags = searchParams.getAll("tags");

  return {
    sort:
      sort === "score_asc" || sort === "created_at_desc" || sort === "created_at_asc"
        ? sort
        : "score_desc",
    status:
      status === "pending" ||
      status === "in_progress" ||
      status === "rejected" ||
      status === "offer_sent" ||
      status === "hired"
        ? status
        : "all",
    tags,
    q,
  };
}

export function JobDetailWorkspace({ jobId }: JobDetailWorkspaceProps) {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  const query = useMemo(() => readCandidateQuery(searchParams), [searchParams]);
  const detailQuery = useJobDetailQuery(jobId);
  const candidatesQuery = useJobCandidatesQuery(jobId, query);

  function updateQuery(next: Partial<JobCandidateListQueryDto>) {
    const merged = { ...query, ...next };
    const params = new URLSearchParams();
    params.set("sort", merged.sort);
    params.set("status", merged.status);
    if (merged.q.trim()) {
      params.set("q", merged.q.trim());
    }
    for (const tag of merged.tags) {
      params.append("tags", tag);
    }
    const serialized = params.toString();
    router.replace(serialized ? `${pathname}?${serialized}` : pathname);
  }

  if (detailQuery.isLoading || candidatesQuery.isLoading) {
    return (
      <AppShell
        title="岗位详情"
        description="正在加载岗位信息和候选人列表。"
        actions={
          <Button href="/jobs" variant="secondary">
            返回岗位列表
          </Button>
        }
      >
        <Card className="flex min-h-[260px] items-center justify-center">
          <div className="inline-flex items-center gap-2 text-sm text-slate-600">
            <Spinner className="h-4 w-4 border-slate-300 border-t-slate-800" />
            正在加载岗位工作台
          </div>
        </Card>
      </AppShell>
    );
  }

  if (detailQuery.isError || candidatesQuery.isError) {
    return (
      <AppShell
        title="岗位详情"
        description="加载失败，请稍后重试。"
        actions={
          <Button href="/jobs" variant="secondary">
            返回岗位列表
          </Button>
        }
      >
        <ErrorStateCard
          message={getJobApiErrorMessage(detailQuery.error ?? candidatesQuery.error)}
          actionLabel="重试"
          onAction={() => {
            void Promise.all([detailQuery.refetch(), candidatesQuery.refetch()]);
          }}
        />
      </AppShell>
    );
  }

  if (!detailQuery.data || !candidatesQuery.data) {
    return null;
  }

  return (
    <AppShell
      title="岗位详情"
      description="查看岗位摘要、候选人列表，并继续推进导入和筛选。"
      actions={
        <Button href="/jobs" variant="secondary">
          返回岗位列表
        </Button>
      }
    >
      <div className="space-y-6">
        <JobSummaryPanel job={detailQuery.data} />
        <CandidateListToolbar
          sort={query.sort}
          status={query.status}
          selectedTags={query.tags}
          query={query.q}
          availableTags={candidatesQuery.data.available_tags}
          onSortChange={(value) => updateQuery({ sort: value })}
          onStatusChange={(value) => updateQuery({ status: value })}
          onQueryChange={(value) => updateQuery({ q: value })}
          onToggleTag={(tag) => {
            const nextTags = query.tags.includes(tag)
              ? query.tags.filter((item) => item !== tag)
              : [...query.tags, tag];
            updateQuery({ tags: nextTags });
          }}
        />
        <CandidateList items={candidatesQuery.data.items} />
      </div>
    </AppShell>
  );
}
