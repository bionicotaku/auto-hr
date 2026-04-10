"use client";

import { useEffect, useMemo, useState } from "react";

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

const DEFAULT_CANDIDATE_QUERY: JobCandidateListQueryDto = {
  sort: "score_desc",
  status: "all",
  tags: [],
  q: "",
};

export function JobDetailWorkspace({ jobId }: JobDetailWorkspaceProps) {
  const [sort, setSort] = useState<JobCandidateListQueryDto["sort"]>(DEFAULT_CANDIDATE_QUERY.sort);
  const [status, setStatus] = useState<JobCandidateListQueryDto["status"]>(DEFAULT_CANDIDATE_QUERY.status);
  const [selectedTags, setSelectedTags] = useState<string[]>(DEFAULT_CANDIDATE_QUERY.tags);
  const [searchQuery, setSearchQuery] = useState(DEFAULT_CANDIDATE_QUERY.q);
  const [debouncedSearchQuery, setDebouncedSearchQuery] = useState(DEFAULT_CANDIDATE_QUERY.q);

  useEffect(() => {
    const timeoutId = window.setTimeout(() => {
      setDebouncedSearchQuery(searchQuery.trim());
    }, 250);

    return () => {
      window.clearTimeout(timeoutId);
    };
  }, [searchQuery]);

  const query = useMemo(
    () => ({
      sort,
      status,
      tags: selectedTags,
      q: debouncedSearchQuery,
    }),
    [debouncedSearchQuery, selectedTags, sort, status],
  );
  const detailQuery = useJobDetailQuery(jobId);
  const candidatesQuery = useJobCandidatesQuery(jobId, query);

  if (detailQuery.isLoading || (candidatesQuery.isLoading && !candidatesQuery.data)) {
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
          sort={sort}
          status={status}
          selectedTags={selectedTags}
          query={searchQuery}
          availableTags={candidatesQuery.data.available_tags}
          onSortChange={setSort}
          onStatusChange={setStatus}
          onQueryChange={setSearchQuery}
          onToggleTag={(tag) => {
            setSelectedTags((currentTags) =>
              currentTags.includes(tag)
                ? currentTags.filter((item) => item !== tag)
                : [...currentTags, tag],
            );
          }}
        />
        {candidatesQuery.isFetching ? (
          <div className="inline-flex items-center gap-2 text-sm text-slate-500">
            <Spinner className="h-4 w-4 border-slate-300 border-t-slate-800" />
            正在更新候选人列表
          </div>
        ) : null}
        <CandidateList items={candidatesQuery.data.items} />
      </div>
    </AppShell>
  );
}
