import { ChangeEvent } from "react";

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
  function handleChange(event: ChangeEvent<HTMLInputElement>) {
    onSelectFiles(event.target.files);
    event.target.value = "";
  }

  return (
    <Card className="space-y-4">
      <div className="space-y-2">
        <h2 className="text-lg font-semibold tracking-tight text-slate-950">上传 PDF</h2>
        <p className="text-sm leading-7 text-slate-600">最多选择 4 份简历或补充材料，文件会按当前顺序显示。</p>
      </div>

      <label
        className="flex min-h-44 cursor-pointer flex-col items-center justify-center rounded-3xl border border-dashed border-slate-300 bg-slate-50 px-6 py-8 text-center transition hover:border-slate-400 hover:bg-white"
        htmlFor="candidate-import-files"
      >
        <span className="text-base font-semibold text-slate-900">选择 PDF 文件</span>
        <span className="mt-2 text-sm leading-6 text-slate-600">支持拖拽或点击选择，单次最多 4 个文件。</span>
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

      {errorMessage ? <p className="text-sm text-rose-600">{errorMessage}</p> : null}

      {files.length > 0 ? (
        <div className="space-y-3">
          {files.map((file, index) => (
            <div
              key={`${file.name}-${file.size}-${index}`}
              className="flex items-center justify-between rounded-2xl border border-slate-200 bg-white px-4 py-3"
            >
              <div className="min-w-0">
                <p className="truncate text-sm font-medium text-slate-900">{file.name}</p>
                <p className="text-sm text-slate-500">{Math.max(1, Math.round(file.size / 1024))} KB</p>
              </div>
              <button
                type="button"
                className="text-sm font-medium text-slate-500 transition hover:text-slate-900"
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
