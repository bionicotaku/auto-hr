from dataclasses import dataclass

from pydantic import BaseModel, Field


PLACEHOLDER_CANDIDATE_NAMES = {
    "unknown",
    "unknown candidate",
    "candidate",
    "n/a",
    "na",
    "none",
    "未提供",
    "未知",
    "未知候选人",
    "候选人",
}


def is_effective_candidate_name(full_name: str | None) -> bool:
    if full_name is None:
        return False
    normalized = " ".join(full_name.strip().split())
    if len(normalized) < 2:
        return False
    return normalized.casefold() not in PLACEHOLDER_CANDIDATE_NAMES


class CandidateIdentitySchema(BaseModel):
    full_name: str | None = None
    current_title: str | None = None
    current_company: str | None = None
    location_text: str | None = None
    email: str | None = None
    phone: str | None = None
    linkedin_url: str | None = None


class CandidateProfileSummarySchema(BaseModel):
    professional_summary_raw: str | None = None
    professional_summary_normalized: str | None = None
    years_of_total_experience: float | None = None
    years_of_relevant_experience: float | None = None
    seniority_level: str | None = None


class CandidateWorkExperienceSchema(BaseModel):
    company_name: str | None = None
    title: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    is_current: bool | None = None
    description_raw: str | None = None
    description_normalized: str | None = None
    key_achievements: list[str] = Field(default_factory=list)


class CandidateEducationSchema(BaseModel):
    school_name: str | None = None
    degree: str | None = None
    degree_level: str | None = None
    major: str | None = None
    end_date: str | None = None


class CandidateSkillsSchema(BaseModel):
    skills_raw: list[str] = Field(default_factory=list)
    skills_normalized: list[str] = Field(default_factory=list)


class CandidateEmploymentPreferencesSchema(BaseModel):
    work_authorization: str | None = None
    requires_sponsorship: bool | None = None
    willing_to_relocate: bool | None = None
    preferred_locations: list[str] = Field(default_factory=list)
    preferred_work_modes: list[str] = Field(default_factory=list)


class CandidateApplicationAnswerSchema(BaseModel):
    question_text: str | None = None
    answer_text: str | None = None


class CandidateDocumentSchema(BaseModel):
    document_type: str
    filename: str
    storage_path: str
    text_extracted: str | None = None


class CandidateAdditionalInformationSchema(BaseModel):
    uncategorized_highlights: list[str] = Field(default_factory=list)
    parser_notes: list[str] = Field(default_factory=list)


class CandidateStandardizationSchema(BaseModel):
    is_candidate_like: bool
    invalid_reason: str | None = None
    identity: CandidateIdentitySchema
    profile_summary: CandidateProfileSummarySchema
    work_experiences: list[CandidateWorkExperienceSchema] = Field(default_factory=list)
    educations: list[CandidateEducationSchema] = Field(default_factory=list)
    skills: CandidateSkillsSchema
    employment_preferences: CandidateEmploymentPreferencesSchema
    application_answers: list[CandidateApplicationAnswerSchema] = Field(default_factory=list)
    documents: list[CandidateDocumentSchema] = Field(default_factory=list)
    additional_information: CandidateAdditionalInformationSchema


@dataclass(frozen=True)
class PreparedCandidateDocumentInput:
    filename: str
    storage_path: str
    mime_type: str
    upload_order: int
    extracted_text: str
    page_count: int | None


@dataclass(frozen=True)
class PreparedCandidateImportInput:
    raw_text_input: str | None
    job_id: str
    job_title: str
    job_summary: str
    temp_request_id: str
    documents: list[PreparedCandidateDocumentInput]
