import type { CandidateDetailRawInputDto } from "@/lib/api/types";
import { Card } from "@/components/ui/Card";

type CandidateRawInputPanelProps = {
  rawInput: CandidateDetailRawInputDto;
};

function documentTypeLabel(documentType: "resume" | "other") {
  return documentType === "resume" ? "简历" : "附件";
}

export function CandidateRawInputPanel({ rawInput }: CandidateRawInputPanelProps) {
  return (
    <Card className="space-y-5">
      <div className="space-y-1">
        <h2 className="text-lg font-semibold tracking-tight text-slate-950">原始输入</h2>
        <p className="text-sm leading-6 text-slate-600">保留文本和文件痕迹，方便人工回看 AI 的分析依据。</p>
      </div>

      <div className="space-y-2">
        <p className="text-sm font-medium text-slate-900">原始文本</p>
        <div className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-4 text-sm leading-7 text-slate-600">
          {rawInput.raw_text_input?.trim() ? rawInput.raw_text_input : "未提供原始文本。"}
        </div>
      </div>

      <div className="space-y-3">
        <p className="text-sm font-medium text-slate-900">原始文件</p>
        {rawInput.documents.length > 0 ? (
          <div className="space-y-3">
            {rawInput.documents.map((document) => (
              <div key={document.id} className="rounded-2xl border border-slate-200 bg-white px-4 py-4">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div className="flex flex-wrap items-center gap-2">
                    <p className="text-sm font-semibold text-slate-900">{document.filename}</p>
                    <span className="rounded-full bg-slate-100 px-2.5 py-1 text-xs text-slate-600">
                      {documentTypeLabel(document.document_type)}
                    </span>
                    {document.page_count !== null ? (
                      <span className="rounded-full bg-slate-100 px-2.5 py-1 text-xs text-slate-600">
                        {document.page_count} 页
                      </span>
                    ) : null}
                  </div>
                  <a
                    href={document.file_url}
                    target="_blank"
                    rel="noreferrer"
                    className="text-sm font-medium text-slate-700 underline decoration-slate-300 underline-offset-4 transition hover:text-slate-950"
                  >
                    查看原文件
                  </a>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-sm leading-6 text-slate-600">未上传 PDF 文件。</p>
        )}
      </div>
    </Card>
  );
}
