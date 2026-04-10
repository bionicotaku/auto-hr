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

export type JobRubricDraftItemDto = {
  sort_order: number;
  name: string;
  description: string;
  criterion_type: "weighted" | "hard_requirement";
  weight_input: number;
};

export type JobRubricFinalItemDto = {
  id?: string;
  sort_order: number;
  name: string;
  description: string;
  criterion_type: "weighted" | "hard_requirement";
  weight_input: number;
  weight_normalized: number | null;
  scoring_standard_items: Array<{ key: string; value: string }>;
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
  responsibilities: string[];
  skills: string[];
  created_at: string;
  updated_at: string;
  finalized_at: string | null;
  rubric_items: JobRubricDraftItemDto[];
};

export type JobChatRequestDto = {
  description_text: string;
  responsibilities: string[];
  skills: string[];
  rubric_items: JobRubricDraftItemDto[];
  recent_messages: JobEditorMessageDto[];
  user_input: string;
};

export type JobChatResponseDto = {
  reply_text: string;
};

export type JobGeneratedContentRequestDto = JobChatRequestDto;

export type JobGeneratedContentResponseDto = {
  description_text: string;
  responsibilities: string[];
  skills: string[];
  rubric_items: JobRubricDraftItemDto[];
};

export type JobFinalizeRequestDto = {
  description_text: string;
  responsibilities: string[];
  skills: string[];
  rubric_items: JobRubricDraftItemDto[];
};

export type JobFinalizeResponseDto = {
  job_id: string;
  lifecycle_status: "active";
};

export type JobCandidateImportContextDto = {
  job_id: string;
  title: string;
  summary: string;
  lifecycle_status: "draft" | "active";
};

export type CandidateImportResponseDto = {
  candidate_id: string;
  job_id: string;
};

export type JobListItemDto = {
  job_id: string;
  title: string;
  summary: string;
  lifecycle_status: "draft" | "active";
  candidate_count: number;
  updated_at: string;
};

export type JobListResponseDto = {
  items: JobListItemDto[];
};

export type JobDetailRubricSummaryItemDto = {
  name: string;
  criterion_type: "weighted" | "hard_requirement";
  weight_label: string;
};

export type JobDetailStructuredInfoItemDto = {
  label: string;
  value: string;
};

export type JobDetailResponseDto = {
  job_id: string;
  title: string;
  summary: string;
  description_text: string;
  lifecycle_status: "draft" | "active";
  candidate_count: number;
  rubric_summary: JobDetailRubricSummaryItemDto[];
  structured_info_summary: JobDetailStructuredInfoItemDto[];
};

export type JobCandidateListItemDto = {
  candidate_id: string;
  full_name: string;
  ai_summary: string;
  overall_score_percent: number | null;
  current_status: "pending" | "in_progress" | "rejected" | "offer_sent" | "hired";
  tags: string[];
  created_at: string;
};

export type JobCandidateListQueryDto = {
  sort: "score_desc" | "score_asc" | "created_at_desc" | "created_at_asc";
  status: "all" | "pending" | "in_progress" | "rejected" | "offer_sent" | "hired";
  tags: string[];
  q: string;
};

export type JobCandidateListResponseDto = {
  items: JobCandidateListItemDto[];
  available_tags: string[];
};
