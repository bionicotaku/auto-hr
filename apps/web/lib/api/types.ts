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

export type JobEditorMessageDto = {
  role: "user" | "assistant" | "system";
  content: string;
};

export type JobRubricItemDto = {
  id?: string;
  sort_order: number;
  name: string;
  description: string;
  criterion_type: "weighted" | "hard_requirement";
  weight_input: number;
  weight_normalized: number | null;
  scoring_standard_json: Record<string, unknown>;
  agent_prompt_text: string;
  evidence_guidance_text: string;
};

export type JobEditResponseDto = {
  id: string;
  lifecycle_status: "draft" | "active";
  creation_mode: "from_description" | "from_form";
  title: string;
  summary: string;
  description_text: string;
  structured_info_json: Record<string, unknown>;
  original_description_input: string | null;
  original_form_input_json: Record<string, unknown> | null;
  editor_history_summary: string | null;
  editor_recent_messages_json: Array<Record<string, unknown>>;
  created_at: string;
  updated_at: string;
  finalized_at: string | null;
  rubric_items: JobRubricItemDto[];
};

export type JobChatRequestDto = {
  description_text: string;
  rubric_items: JobRubricItemDto[];
  recent_messages: JobEditorMessageDto[];
  user_input: string;
};

export type JobChatResponseDto = {
  reply_text: string;
};

export type JobGeneratedContentRequestDto = JobChatRequestDto;

export type JobGeneratedContentResponseDto = {
  description_text: string;
  rubric_items: JobRubricItemDto[];
};

export type JobRegenerateRequestDto = {
  recent_messages: JobEditorMessageDto[];
  history_summary: string | null;
};

export type JobFinalizeRequestDto = {
  description_text: string;
  rubric_items: JobRubricItemDto[];
};

export type JobFinalizeResponseDto = {
  job_id: string;
  lifecycle_status: "active";
};
