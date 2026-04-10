import { JobDraftEditPlaceholder } from "@/components/job/new/JobDraftEditPlaceholder";

type JobEditPageProps = {
  params: Promise<{ jobId: string }>;
};

export default async function JobEditPage({ params }: JobEditPageProps) {
  const { jobId } = await params;

  return <JobDraftEditPlaceholder jobId={jobId} />;
}

