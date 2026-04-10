"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { useRouter } from "next/navigation";

import { AppShell } from "@/components/layout/AppShell";
import { Badge } from "@/components/ui/Badge";
import { AnalysisProgressCard } from "@/components/ui/AnalysisProgressCard";
import { Card } from "@/components/ui/Card";
import { ErrorStateCard } from "@/components/ui/ErrorStateCard";
import { Spinner } from "@/components/ui/Spinner";
import { useAnalysisRun } from "@/hooks/useAnalysisRun";
import { getJobApiErrorMessage } from "@/lib/api/jobs";
import type { JobEditorMessageDto, JobRubricDraftItemDto } from "@/lib/api/types";
import {
  useJobAgentEditMutation,
  useDeleteJobDraftMutation,
  useJobChatMutation,
  useJobEditQuery,
  useJobFinalizeMutation,
} from "@/lib/query/jobs";

import { JobAiChatPanel } from "./JobAiChatPanel";
import { JobDescriptionEditor } from "./JobDescriptionEditor";
import { JobEditActionBar } from "./JobEditActionBar";
import { JobRubricEditor } from "./JobRubricEditor";

type JobEditWorkspaceProps = {
  jobId: string;
};

const rubricExamples = [
  {
    title: "核心能力",
    detail: "整理最重要的胜任力，并写清楚什么样的经历才算通过。",
  },
  {
    title: "必须项",
    detail: "把不可妥协的要求单独列出，避免和一般加分项混在一起。",
  },
  {
    title: "评分标准",
    detail: "让每个评估项都能被清晰判断，方便后续查看候选人是否匹配。",
  },
];

export function JobEditWorkspace({ jobId }: JobEditWorkspaceProps) {
  const router = useRouter();
  const editQuery = useJobEditQuery(jobId);
  const chatMutation = useJobChatMutation(jobId);
  const agentMutation = useJobAgentEditMutation(jobId);
  const finalizeMutation = useJobFinalizeMutation(jobId);
  const deleteDraftMutation = useDeleteJobDraftMutation(jobId);
  const analysisRun = useAnalysisRun({
    onCompleted: (event) => {
      if (event.result_resource_type === "job") {
        router.push(`/jobs/${event.result_resource_id}`);
      }
    },
  });

  const [title, setTitle] = useState("");
  const [summary, setSummary] = useState("");
  const [descriptionText, setDescriptionText] = useState("");
  const [structuredInfoJson, setStructuredInfoJson] = useState<Record<string, unknown>>({});
  const [responsibilitiesText, setResponsibilitiesText] = useState("");
  const [skillsText, setSkillsText] = useState("");
  const [rubricItems, setRubricItems] = useState<JobRubricDraftItemDto[]>([]);
  const [chatInput, setChatInput] = useState("");
  const [messages, setMessages] = useState<JobEditorMessageDto[]>([]);
  const [panelError, setPanelError] = useState<string | null>(null);
  const initializedJobIdRef = useRef<string | null>(null);

  useEffect(() => {
    if (!editQuery.data || initializedJobIdRef.current === editQuery.data.id) {
      return;
    }

    initializedJobIdRef.current = editQuery.data.id;
    setTitle(editQuery.data.title);
    setSummary(editQuery.data.summary);
    setDescriptionText(editQuery.data.description_text);
    setStructuredInfoJson(editQuery.data.structured_info_json);
    setResponsibilitiesText(joinLines(editQuery.data.responsibilities));
    setSkillsText(joinLines(editQuery.data.skills));
    setRubricItems(editQuery.data.rubric_items);
    setMessages(
      editQuery.data.editor_recent_messages_json.flatMap((message) => {
        if (
          typeof message === "object" &&
          message !== null &&
          "role" in message &&
          "content" in message &&
          typeof message.role === "string" &&
          typeof message.content === "string"
        ) {
          return [{ role: message.role as JobEditorMessageDto["role"], content: message.content }];
        }
        return [];
      }),
    );
    setPanelError(null);
  }, [editQuery.data]);

  const isBusy =
    chatMutation.isPending ||
    agentMutation.isPending ||
    finalizeMutation.isPending ||
    deleteDraftMutation.isPending ||
    analysisRun.isRunning;

  const headerActions = useMemo(
    () => (
      <>
        <Badge tone={editQuery.data?.lifecycle_status === "active" ? "success" : "warning"}>
          {editQuery.data?.lifecycle_status === "active" ? "已生效" : "草稿"}
        </Badge>
        <span className="rounded-full bg-[var(--panel-muted)] px-3 py-1 text-sm text-[var(--foreground-soft)] ring-1 ring-[var(--border)]">
          编号 {jobId}
        </span>
      </>
    ),
    [editQuery.data?.lifecycle_status, jobId],
  );

  const initialEditSnapshot = useMemo(() => {
    if (!editQuery.data) {
      return null;
    }

    return JSON.stringify({
      title: editQuery.data.title,
      summary: editQuery.data.summary,
      description_text: editQuery.data.description_text,
      structured_info_json: mergeStructuredInfoFields(editQuery.data.structured_info_json, {
        responsibilities: editQuery.data.responsibilities,
        skills: editQuery.data.skills,
      }),
      rubric_items: editQuery.data.rubric_items.map((item) => ({
        sort_order: item.sort_order,
        name: item.name,
        description: item.description,
        criterion_type: item.criterion_type,
        weight_input: item.weight_input,
      })),
    });
  }, [editQuery.data]);

  function buildRecentMessages() {
    return messages.slice(-5);
  }

  function parseLines(value: string) {
    return value
      .split("\n")
      .map((item) => item.trim())
      .filter(Boolean);
  }

  function updateRubricItem<K extends keyof JobRubricDraftItemDto>(
    index: number,
    field: K,
    value: JobRubricDraftItemDto[K],
  ) {
    setRubricItems((current) =>
      current.map((item, itemIndex) => {
        if (itemIndex !== index) {
          return item;
        }
        if (field === "weight_input") {
          const weightInput = Number(value);
          return {
            ...item,
            weight_input: weightInput,
            criterion_type: weightInput === 100 ? "hard_requirement" : "weighted",
          };
        }
        return { ...item, [field]: value };
      }),
    );
  }

  function buildCurrentEditSnapshot() {
    return JSON.stringify({
      title,
      summary,
      description_text: descriptionText,
      structured_info_json: mergeStructuredInfoFields(structuredInfoJson, {
        responsibilities: parseLines(responsibilitiesText),
        skills: parseLines(skillsText),
      }),
      rubric_items: rubricItems.map((item) => ({
        sort_order: item.sort_order,
        name: item.name,
        description: item.description,
        criterion_type: item.criterion_type,
        weight_input: item.weight_input,
      })),
    });
  }

  async function handleChatSubmit() {
    const trimmedInput = chatInput.trim();
    if (!trimmedInput) {
      setPanelError("请先输入修改要求。");
      return;
    }

    try {
      setPanelError(null);
      const response = await chatMutation.mutateAsync({
        description_text: descriptionText,
        responsibilities: parseLines(responsibilitiesText),
        skills: parseLines(skillsText),
        rubric_items: rubricItems,
        recent_messages: buildRecentMessages(),
        user_input: trimmedInput,
      });
      setMessages((current) => [
        ...current,
        { role: "user", content: trimmedInput },
        { role: "assistant", content: response.reply_text },
      ]);
      setChatInput("");
    } catch (error) {
      setPanelError(getJobApiErrorMessage(error));
    }
  }

  async function handleAgentSubmit() {
    const trimmedInput = chatInput.trim();
    if (!trimmedInput) {
      setPanelError("请先输入修改要求。");
      return;
    }

    try {
      setPanelError(null);
      const response = await agentMutation.mutateAsync({
        description_text: descriptionText,
        responsibilities: parseLines(responsibilitiesText),
        skills: parseLines(skillsText),
        rubric_items: rubricItems,
        recent_messages: buildRecentMessages(),
        user_input: trimmedInput,
      });
      setTitle(response.title);
      setSummary(response.summary);
      setDescriptionText(response.description_text);
      setStructuredInfoJson(response.structured_info_json);
      setResponsibilitiesText(joinLines(response.responsibilities));
      setSkillsText(joinLines(response.skills));
      setRubricItems(response.rubric_items);
      setMessages((current) => [
        ...current,
        { role: "user", content: trimmedInput },
        { role: "assistant", content: "已生成新版岗位定义。" },
      ]);
      setChatInput("");
    } catch (error) {
      setPanelError(getJobApiErrorMessage(error));
    }
  }

  async function handleFinalize() {
    try {
      setPanelError(null);
      if (
        editQuery.data?.lifecycle_status === "active" &&
        initialEditSnapshot !== null &&
        buildCurrentEditSnapshot() === initialEditSnapshot
      ) {
        router.push(`/jobs/${jobId}`);
        return;
      }
      await analysisRun.start(() =>
        finalizeMutation.mutateAsync({
          description_text: descriptionText,
          responsibilities: parseLines(responsibilitiesText),
          skills: parseLines(skillsText),
          rubric_items: rubricItems,
        }),
      );
    } catch (error) {
      setPanelError(getJobApiErrorMessage(error));
    }
  }

  async function handleCancel() {
    try {
      setPanelError(null);
      if (editQuery.data?.lifecycle_status === "active") {
        router.push(`/jobs/${jobId}`);
        return;
      }
      await deleteDraftMutation.mutateAsync();
      router.push("/jobs");
    } catch (error) {
      setPanelError(getJobApiErrorMessage(error));
    }
  }

  return (
    <AppShell
      title="岗位编辑"
      description="继续完善职位描述与评估规范。"
      backHref={editQuery.data?.lifecycle_status === "active" ? `/jobs/${jobId}` : "/jobs"}
      actions={headerActions}
    >
      <Card className="flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between">
        <div className="space-y-2">
          <p className="text-xs font-semibold uppercase tracking-[0.24em] text-[var(--foreground-muted)]">
            Workspace summary
          </p>
          <p className="text-sm font-semibold text-[var(--foreground)]">
            {title || editQuery.data?.title || "岗位草稿"}
          </p>
          <p className="text-sm leading-6 text-[var(--foreground-soft)]">
            {summary || editQuery.data?.summary || "确认描述与评估规范后，再完成当前岗位。"}
          </p>
        </div>
        {Object.keys(structuredInfoJson).length > 0 || editQuery.data?.structured_info_json ? (
          <div className="rounded-full border border-[var(--border)] bg-[var(--panel-muted)] px-4 py-2 text-sm leading-6 text-[var(--foreground-soft)]">
            <span>{String((structuredInfoJson.location ?? editQuery.data?.structured_info_json.location) ?? "地点待补充")}</span>
          </div>
        ) : null}
      </Card>

      {editQuery.isLoading ? (
        <Card className="flex min-h-[240px] items-center justify-center">
          <div className="inline-flex items-center gap-2 text-sm text-[var(--foreground-soft)]">
            <Spinner className="h-4 w-4" />
            正在加载岗位信息
          </div>
        </Card>
      ) : editQuery.isError ? (
        <ErrorStateCard
          message={getJobApiErrorMessage(editQuery.error)}
          actionLabel="重试"
          onAction={() => {
            void editQuery.refetch();
          }}
        />
      ) : (
        <>
          <div className="grid gap-6 xl:grid-cols-[1.18fr_0.82fr]">
            <div className="grid gap-6">
              <JobDescriptionEditor
                value={descriptionText}
                responsibilitiesValue={responsibilitiesText}
                skillsValue={skillsText}
                onChange={setDescriptionText}
                onResponsibilitiesChange={setResponsibilitiesText}
                onSkillsChange={setSkillsText}
                disabled={isBusy}
              />
              <JobRubricEditor
                items={rubricItems.length > 0 ? rubricItems : rubricExamples.map((item, index) => ({
                  sort_order: index + 1,
                  name: item.title,
                  description: item.detail,
                  criterion_type: "weighted",
                  weight_input: 10,
                }))}
                onItemChange={updateRubricItem}
                disabled={isBusy}
              />
            </div>
            <JobAiChatPanel
              messages={messages}
              inputValue={chatInput}
              errorMessage={panelError}
              isChatPending={chatMutation.isPending}
              isAgentPending={agentMutation.isPending}
              onInputChange={setChatInput}
              onChatSubmit={handleChatSubmit}
              onAgentSubmit={handleAgentSubmit}
            />
          </div>

          <JobEditActionBar
            isFinalizePending={finalizeMutation.isPending || analysisRun.isRunning}
            isCancelPending={
              editQuery.data?.lifecycle_status === "draft" && deleteDraftMutation.isPending
            }
            onCancel={handleCancel}
            onFinalize={handleFinalize}
          />
          {analysisRun.state !== "idle" ? (
            <AnalysisProgressCard
              title="岗位分析进度"
              currentStage={analysisRun.currentStage}
              currentAiStep={analysisRun.currentAiStep}
              totalAiSteps={analysisRun.totalAiSteps}
              errorMessage={analysisRun.errorMessage}
            />
          ) : null}
        </>
      )}
    </AppShell>
  );
}

function joinLines(items: string[]) {
  return items.join("\n");
}

function mergeStructuredInfoFields(
  structuredInfoJson: Record<string, unknown>,
  fields: {
    responsibilities: string[];
    skills: string[];
  },
) {
  return {
    ...structuredInfoJson,
    responsibilities: fields.responsibilities,
    skills: fields.skills,
  };
}
