import { ChangeEvent, DragEvent, useState } from "react";

import { Card } from "@/components/ui/Card";

type CandidateFileDropzoneProps = {
  files: File[];
  errorMessage: string | null;
  onSelectFiles: (files: FileList | null) => void;
  onRemoveFile: (index: number) => void;
};

export function CandidateFileDropzone({
  files,
  errorMessage,
  onSelectFiles,
  onRemoveFile,
}: CandidateFileDropzoneProps) {
  const [isDragging, setIsDragging] = useState(false);

  function handleChange(event: ChangeEvent<HTMLInputElement>) {
    onSelectFiles(event.target.files);
    event.target.value = "";
  }

  function handleDragEnter(event: DragEvent<HTMLLabelElement>) {
    event.preventDefault();
    event.stopPropagation();
    setIsDragging(true);
  }

  function handleDragOver(event: DragEvent<HTMLLabelElement>) {
    event.preventDefault();
    event.stopPropagation();
    event.dataTransfer.dropEffect = "copy";
    setIsDragging(true);
  }

  function handleDragLeave(event: DragEvent<HTMLLabelElement>) {
    event.preventDefault();
    event.stopPropagation();
    setIsDragging(false);
  }

  function handleDrop(event: DragEvent<HTMLLabelElement>) {
    event.preventDefault();
    event.stopPropagation();
    setIsDragging(false);
    onSelectFiles(event.dataTransfer.files);
  }

  return (
    <Card className="space-y-4">
      <div className="space-y-2">
        <p className="text-xs font-semibold uppercase tracking-[0.24em] text-[var(--foreground-muted)]">
          PDF upload
        </p>
        <h2 className="text-lg font-semibold tracking-tight text-[var(--foreground)]">上传 PDF</h2>
        <p className="text-sm leading-7 text-[var(--foreground-soft)]">
          最多选择 4 份简历或补充材料，文件会按当前顺序显示。
        </p>
      </div>

      <label
        className={`flex min-h-44 cursor-pointer flex-col items-center justify-center rounded-[28px] border border-dashed px-6 py-8 text-center transition-colors duration-200 ease-out motion-reduce:transition-none ${
          isDragging
            ? "border-[var(--border-strong)] bg-[var(--panel-muted)]"
            : "border-[var(--border)] bg-[var(--panel-muted)] hover:border-[var(--border-strong)] hover:bg-[var(--panel-strong)]"
        }`}
        htmlFor="candidate-import-files"
        onDragEnter={handleDragEnter}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <span className="text-base font-semibold text-[var(--foreground)]">选择 PDF 文件</span>
        <span className="mt-2 text-sm leading-6 text-[var(--foreground-soft)]">
          支持拖拽或点击选择，单次最多 4 个文件。
        </span>
      </label>
      <input
        id="candidate-import-files"
        aria-label="选择 PDF 文件"
        className="sr-only"
        type="file"
        accept="application/pdf,.pdf"
        multiple
        onChange={handleChange}
      />

      {errorMessage ? <p className="text-sm text-[var(--foreground)]">{errorMessage}</p> : null}

      {files.length > 0 ? (
        <div className="space-y-3">
          {files.map((file, index) => (
            <div
              key={`${file.name}-${file.size}-${index}`}
              className="flex items-center justify-between rounded-[22px] border border-[var(--border)] bg-[var(--panel-strong)] px-4 py-3"
            >
              <div className="min-w-0">
                <p className="truncate text-sm font-medium text-[var(--foreground)]">{file.name}</p>
                <p className="text-sm text-[var(--foreground-muted)]">{Math.max(1, Math.round(file.size / 1024))} KB</p>
              </div>
              <button
                type="button"
                className="cursor-pointer text-sm font-medium text-[var(--foreground-muted)] transition-colors duration-200 ease-out hover:text-[var(--foreground)] motion-reduce:transition-none"
                onClick={() => onRemoveFile(index)}
              >
                移除
              </button>
            </div>
          ))}
        </div>
      ) : null}
    </Card>
  );
}
