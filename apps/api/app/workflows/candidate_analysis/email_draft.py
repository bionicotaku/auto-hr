from app.ai.client import OpenAIResponsesClient
from app.ai.prompts.candidate_email_draft import build_candidate_email_draft_prompt
from app.schemas.ai.candidate_email_draft import CandidateEmailDraftSchema


class CandidateEmailDraftWorkflow:
    def __init__(self, client: OpenAIResponsesClient) -> None:
        self.client = client

    def run(
        self,
        *,
        draft_type: str,
        job_title: str,
        job_summary: str,
        candidate_context: dict,
    ) -> CandidateEmailDraftSchema:
        prompt = build_candidate_email_draft_prompt(
            draft_type=draft_type,
            job_title=job_title,
            job_summary=job_summary,
            candidate_context=candidate_context,
        )
        payload = self.client.generate_structured_output(
            prompt=prompt,
            schema_name="candidate_email_draft_schema",
            schema=CandidateEmailDraftSchema.model_json_schema(),
        )
        return CandidateEmailDraftSchema.model_validate(payload)
