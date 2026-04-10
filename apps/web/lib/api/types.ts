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
  title: string;
  summary: string;
  description_text: string;
  structured_info_json: Record<string, unknown>;
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

export type CandidateDetailJobContextDto = {
  job_id: string;
  title: string;
};

export type CandidateDetailRawDocumentDto = {
  id: string;
  document_type: "resume" | "other";
  filename: string;
  storage_path: string;
  mime_type: string;
  extracted_text: string;
  page_count: number | null;
  upload_order: number;
};

export type CandidateDetailRawInputDto = {
  raw_text_input: string | null;
  documents: CandidateDetailRawDocumentDto[];
};

export type CandidateDetailIdentityDto = {
  full_name: string;
  current_title: string | null;
  current_company: string | null;
  location_text: string | null;
  email: string | null;
  phone: string | null;
  linkedin_url: string | null;
};

export type CandidateDetailProfileSummaryDto = {
  professional_summary_raw: string | null;
  professional_summary_normalized: string | null;
  years_of_total_experience: number | null;
  years_of_relevant_experience: number | null;
  seniority_level: string | null;
};

export type CandidateDetailNormalizedProfileDto = {
  identity: CandidateDetailIdentityDto;
  profile_summary: CandidateDetailProfileSummaryDto;
  work_experiences: Array<Record<string, unknown>>;
  educations: Array<Record<string, unknown>>;
  skills: Record<string, unknown>;
  employment_preferences: Record<string, unknown>;
  application_answers: Array<Record<string, unknown>>;
  additional_information: Record<string, unknown>;
};

export type CandidateDetailRubricResultDto = {
  job_rubric_item_id: string;
  rubric_name: string;
  rubric_description: string;
  criterion_type: "weighted" | "hard_requirement";
  weight_label: string;
  score_0_to_5: number | null;
  hard_requirement_decision: "pass" | "borderline" | "fail" | null;
  reason_text: string;
  evidence_points: string[];
  uncertainty_note: string | null;
};

export type CandidateDetailTagDto = {
  id: string;
  name: string;
  source: "ai" | "manual";
};

export type CandidateDetailSupervisorDto = {
  hard_requirement_overall: "all_pass" | "has_borderline" | "has_fail";
  overall_score_5: number | null;
  overall_score_percent: number | null;
  ai_summary: string;
  evidence_points: string[];
  recommendation: "advance" | "manual_review" | "hold" | "reject";
  tags: CandidateDetailTagDto[];
};

export type CandidateDetailFeedbackDto = {
  id: string;
  author_name: string | null;
  note_text: string;
  created_at: string;
};

export type CandidateDetailEmailDraftDto = {
  id: string;
  draft_type: "reject" | "advance" | "offer" | "other";
  subject: string;
  body: string;
  created_at: string;
  updated_at: string;
};

export type CandidateDetailActionContextDto = {
  current_status: "pending" | "in_progress" | "rejected" | "offer_sent" | "hired";
  feedbacks: CandidateDetailFeedbackDto[];
  email_drafts: CandidateDetailEmailDraftDto[];
};

export type CandidateDetailDto = {
  candidate_id: string;
  job: CandidateDetailJobContextDto;
  raw_input: CandidateDetailRawInputDto;
  normalized_profile: CandidateDetailNormalizedProfileDto;
  rubric_results: CandidateDetailRubricResultDto[];
  supervisor_summary: CandidateDetailSupervisorDto;
  action_context: CandidateDetailActionContextDto;
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
