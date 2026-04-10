export class ApiError extends Error {
  status: number;
  payload: unknown;

  constructor(message: string, status: number, payload: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.payload = payload;
  }
}

export type CreateJobFromDescriptionRequestDto = {
  description_text: string;
};

export type CreateJobFromFormRequestDto = {
  job_title: string;
  department?: string;
  location?: string;
  employment_type?: string;
  seniority_level?: string;
  business_context?: string;
  responsibilities_summary?: string;
  requirements_summary?: string;
};

export type CreateJobDraftResponseDto = {
  jobId: string;
  job_id?: string;
  id?: string;
  title?: string;
  summary?: string;
  descriptionText?: string;
  description_text?: string;
};
