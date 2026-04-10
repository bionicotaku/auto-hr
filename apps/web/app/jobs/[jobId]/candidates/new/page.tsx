import { CandidateImportWorkspace } from "@/components/candidate/import/CandidateImportWorkspace";

type CandidateImportPageProps = {
  params: Promise<{ jobId: string }>;
};

export default async function CandidateImportPage({ params }: CandidateImportPageProps) {
  const { jobId } = await params;

  return <CandidateImportWorkspace jobId={jobId} />;
}
