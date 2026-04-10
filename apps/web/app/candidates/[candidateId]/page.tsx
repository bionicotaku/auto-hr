import { CandidateDetailWorkspace } from "@/components/candidate/detail/CandidateDetailWorkspace";

type CandidateDetailPageProps = {
  params: Promise<{ candidateId: string }>;
};

export default async function CandidateDetailPage({ params }: CandidateDetailPageProps) {
  const { candidateId } = await params;

  return <CandidateDetailWorkspace candidateId={candidateId} />;
}
