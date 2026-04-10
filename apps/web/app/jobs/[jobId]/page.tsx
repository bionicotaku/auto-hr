import { JobDetailWorkspace } from "@/components/job/detail/JobDetailWorkspace";

type JobDetailPageProps = {
  params: Promise<{ jobId: string }>;
};

export default async function JobDetailPage({ params }: JobDetailPageProps) {
  const { jobId } = await params;

  return <JobDetailWorkspace jobId={jobId} />;
}
