type CandidateDetailPageProps = {
  params: Promise<{ candidateId: string }>;
};

export default async function CandidateDetailPage({ params }: CandidateDetailPageProps) {
  const { candidateId } = await params;

  return (
    <main className="min-h-screen bg-slate-50 px-6 py-12">
      <div className="mx-auto max-w-5xl rounded-[28px] border border-slate-200 bg-white p-10 shadow-[0_24px_64px_rgba(15,23,42,0.08)]">
        <p className="text-sm font-semibold uppercase tracking-[0.22em] text-emerald-700">
          Candidate
        </p>
        <h1 className="mt-3 text-3xl font-semibold tracking-tight text-slate-950">
          候选人详情骨架：{candidateId}
        </h1>
        <p className="mt-4 max-w-2xl text-sm leading-7 text-slate-600">
          后续会按最新设计补齐原始输入区、标准化信息区、rubric 逐项分析区、supervisor 汇总区和操作区。
        </p>
      </div>
    </main>
  );
}
