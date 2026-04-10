 "use client";

import { useEffect, useMemo, useRef, useState } from "react";

import { AppShell } from "@/components/layout/AppShell";
import { Card } from "@/components/ui/Card";
import { Spinner } from "@/components/ui/Spinner";
import { getJobApiErrorMessage } from "@/lib/api/jobs";
import type { JobEditorMessageDto, JobRubricItemDto } from "@/lib/api/types";
import {
  useJobAgentEditMutation,
  useJobChatMutation,
  useJobEditQuery,
  useJobRegenerateMutation,
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
  const editQuery = useJobEditQuery(jobId);
  const chatMutation = useJobChatMutation(jobId);
  const agentMutation = useJobAgentEditMutation(jobId);
  const regenerateMutation = useJobRegenerateMutation(jobId);

  const [descriptionText, setDescriptionText] = useState("");
  const [rubricItems, setRubricItems] = useState<JobRubricItemDto[]>([]);
  const [chatInput, setChatInput] = useState("");
  const [messages, setMessages] = useState<JobEditorMessageDto[]>([]);
  const [panelError, setPanelError] = useState<string | null>(null);
  const initializedJobIdRef = useRef<string | null>(null);

  useEffect(() => {
    if (!editQuery.data || initializedJobIdRef.current === editQuery.data.id) {
      return;
    }

    initializedJobIdRef.current = editQuery.data.id;
    setDescriptionText(editQuery.data.description_text);
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

  const isBusy = chatMutation.isPending || agentMutation.isPending || regenerateMutation.isPending;

  const headerActions = useMemo(
    () => (
      <>
        <span className="rounded-full bg-amber-50 px-3 py-1 text-sm text-amber-700 ring-1 ring-amber-200">
          草稿
        </span>
        <span className="rounded-full bg-slate-100 px-3 py-1 text-sm text-slate-600 ring-1 ring-slate-200">
          编号 {jobId}
        </span>
      </>
    ),
    [jobId],
  );

  function buildRecentMessages() {
    return messages.slice(-5);
  }

  function updateRubricItem<K extends keyof JobRubricItemDto>(
    index: number,
    field: K,
    value: JobRubricItemDto[K],
  ) {
    setRubricItems((current) =>
      current.map((item, itemIndex) => {
        if (itemIndex !== index) {
          return item;
        }
        return { ...item, [field]: value };
      }),
    );
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
        rubric_items: rubricItems,
        recent_messages: buildRecentMessages(),
        user_input: trimmedInput,
      });
      setDescriptionText(response.description_text);
      setRubricItems(response.rubric_items);
      setMessages((current) => [
        ...current,
        { role: "user", content: trimmedInput },
        { role: "assistant", content: "已应用新的岗位定义。" },
      ]);
      setChatInput("");
    } catch (error) {
      setPanelError(getJobApiErrorMessage(error));
    }
  }

  async function handleRegenerate() {
    try {
      setPanelError(null);
      const response = await regenerateMutation.mutateAsync({
        recent_messages: buildRecentMessages(),
        history_summary: null,
      });
      setDescriptionText(response.description_text);
      setRubricItems(response.rubric_items);
      setMessages((current) => [...current, { role: "system", content: "已重新生成当前岗位定义。" }]);
    } catch (error) {
      setPanelError(getJobApiErrorMessage(error));
    }
  }

  return (
    <AppShell
      title="岗位编辑"
      description="继续完善职位描述与评估规范。"
      actions={headerActions}
    >
      <Card className="flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between">
        <div className="space-y-2">
          <p className="text-sm font-semibold text-slate-900">
            {editQuery.data?.title ?? "岗位草稿"}
          </p>
          <p className="text-sm leading-6 text-slate-600">
            {editQuery.data?.summary ?? "确认描述与评估规范后，再完成当前岗位。"}
          </p>
        </div>
        {editQuery.data?.structured_info_json ? (
          <div className="text-sm leading-6 text-slate-600">
            <span>{String(editQuery.data.structured_info_json.location ?? "地点待补充")}</span>
          </div>
        ) : null}
      </Card>

      {editQuery.isLoading ? (
        <Card className="flex min-h-[240px] items-center justify-center">
          <div className="inline-flex items-center gap-2 text-sm text-slate-600">
            <Spinner className="h-4 w-4 border-slate-300 border-t-slate-800" />
            正在加载岗位草稿
          </div>
        </Card>
      ) : editQuery.isError ? (
        <Card className="space-y-2">
          <h2 className="text-lg font-semibold tracking-tight text-slate-950">加载失败</h2>
          <p className="text-sm leading-6 text-slate-600">{getJobApiErrorMessage(editQuery.error)}</p>
        </Card>
      ) : (
        <>
          <div className="grid gap-6 xl:grid-cols-[1.2fr_0.95fr_0.85fr]">
            <JobDescriptionEditor
              value={descriptionText}
              onChange={setDescriptionText}
              disabled={isBusy}
            />
            <JobRubricEditor
              items={rubricItems.length > 0 ? rubricItems : rubricExamples.map((item, index) => ({
                sort_order: index + 1,
                name: item.title,
                description: item.detail,
                criterion_type: "weighted",
                weight_input: 10,
                weight_normalized: 0.1,
                scoring_standard_json: {},
                agent_prompt_text: "",
                evidence_guidance_text: "",
              }))}
              onItemChange={updateRubricItem}
              disabled={isBusy}
            />
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
            isRegeneratePending={regenerateMutation.isPending}
            onRegenerate={handleRegenerate}
          />
        </>
      )}
    </AppShell>
  );
}
