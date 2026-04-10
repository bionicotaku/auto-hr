"use client";

import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";

import { AppShell } from "@/components/layout/AppShell";
import { CandidateImportContextCard } from "@/components/candidate/import/CandidateImportContextCard";
import { CandidateFileDropzone } from "@/components/candidate/import/CandidateFileDropzone";
import { CandidateImportForm } from "@/components/candidate/import/CandidateImportForm";
import { Card } from "@/components/ui/Card";
import { ErrorStateCard } from "@/components/ui/ErrorStateCard";
import { Spinner } from "@/components/ui/Spinner";
import { getJobApiErrorMessage } from "@/lib/api/jobs";
import { useCandidateImportMutation, useJobCandidateImportContextQuery } from "@/lib/query/jobs";

type CandidateImportWorkspaceProps = {
  jobId: string;
};

const MAX_FILES = 4;

export function CandidateImportWorkspace({ jobId }: CandidateImportWorkspaceProps) {
  const router = useRouter();
  const contextQuery = useJobCandidateImportContextQuery(jobId);
  const importMutation = useCandidateImportMutation(jobId);

  const [rawTextInput, setRawTextInput] = useState("");
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [fileError, setFileError] = useState<string | null>(null);
  const [globalError, setGlobalError] = useState<string | null>(null);

  const isFormValid = useMemo(() => Boolean(rawTextInput.trim() || selectedFiles.length > 0), [
    rawTextInput,
    selectedFiles.length,
  ]);
  const disabledReason = useMemo(() => {
    if (!isFormValid) {
      return "请先填写候选人文本或上传至少一份 PDF。";
    }
    return null;
  }, [isFormValid]);

  function handleSelectFiles(fileList: FileList | null) {
    if (!fileList) {
      return;
    }

    const incomingFiles = Array.from(fileList);
    const nextFiles = [...selectedFiles, ...incomingFiles];

    if (nextFiles.length > MAX_FILES) {
      setFileError("最多上传 4 个 PDF 文件。");
      return;
    }

    const invalidFile = incomingFiles.find((file) => {
      const fileName = file.name.toLowerCase();
      return file.type !== "application/pdf" && !fileName.endsWith(".pdf");
    });

    if (invalidFile) {
      setFileError("只能上传 PDF 文件。");
      return;
    }

    setSelectedFiles(nextFiles);
    setFileError(null);
    setGlobalError(null);
  }

  function handleRemoveFile(index: number) {
    setSelectedFiles((current) => current.filter((_, fileIndex) => fileIndex !== index));
    setFileError(null);
  }

  function handleCancel() {
    router.push("/jobs");
  }

  async function handleSubmit() {
    if (!isFormValid || importMutation.isPending) {
      return;
    }

    const formData = new FormData();
    const normalizedText = rawTextInput.trim();
    if (normalizedText) {
      formData.append("raw_text_input", normalizedText);
    }
    for (const file of selectedFiles) {
      formData.append("files", file);
    }

    try {
      setGlobalError(null);
      const response = await importMutation.mutateAsync(formData);
      router.push(`/candidates/${response.candidate_id}`);
    } catch (error) {
      setGlobalError(getJobApiErrorMessage(error));
    }
  }

  return (
    <AppShell
      title="导入候选人"
      description="准备候选人的原始文本和简历文件，后续可继续进入分析链路。"
    >
      {contextQuery.isLoading ? (
        <Card className="flex min-h-[240px] items-center justify-center">
          <div className="inline-flex items-center gap-2 text-sm text-slate-600">
            <Spinner className="h-4 w-4 border-slate-300 border-t-slate-800" />
            正在加载岗位信息
          </div>
        </Card>
      ) : contextQuery.isError ? (
        <ErrorStateCard
          message={getJobApiErrorMessage(contextQuery.error)}
          actionLabel="重试"
          onAction={() => {
            void contextQuery.refetch();
          }}
        />
      ) : contextQuery.data ? (
        <div className="space-y-6">
          <CandidateImportContextCard context={contextQuery.data} />
          <div className="grid gap-6 xl:grid-cols-[1.05fr_0.95fr]">
            <CandidateImportForm
              textValue={rawTextInput}
              onTextChange={(value) => {
                setRawTextInput(value);
                setGlobalError(null);
              }}
              disabledReason={disabledReason}
              globalError={globalError}
              onSubmit={handleSubmit}
              onCancel={handleCancel}
              submitDisabled={!isFormValid || importMutation.isPending}
              isSubmitting={importMutation.isPending}
            />
            <CandidateFileDropzone
              files={selectedFiles}
              errorMessage={fileError}
              onSelectFiles={handleSelectFiles}
              onRemoveFile={handleRemoveFile}
            />
          </div>
        </div>
      ) : null}
    </AppShell>
  );
}
