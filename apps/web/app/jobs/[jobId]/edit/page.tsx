import { JobEditWorkspace } from "@/components/job/edit/JobEditWorkspace";

type JobEditPageProps = {
  params: Promise<{ jobId: string }>;
};

export default async function JobEditPage({ params }: JobEditPageProps) {
  const { jobId } = await params;

  return <JobEditWorkspace jobId={jobId} />;
}
