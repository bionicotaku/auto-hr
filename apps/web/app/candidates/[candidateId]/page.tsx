import { CandidateDetailEmptyState } from "@/components/candidate/CandidateDetailEmptyState";

type CandidateDetailPageProps = {
  params: Promise<{ candidateId: string }>;
};

export default async function CandidateDetailPage({ params }: CandidateDetailPageProps) {
  const { candidateId } = await params;

  return <CandidateDetailEmptyState candidateId={candidateId} />;
}
