from pydantic import ValidationError

from app.ai.client import OpenAIResponsesClient
from app.ai.prompts.job_definition import (
    build_create_draft_from_description_prompt,
    build_create_draft_from_form_prompt,
)
from app.schemas.ai.job_definition import (
    JobDraftSchema,
)


class JobDefinitionCreateDraftWorkflow:
    def __init__(self, client: OpenAIResponsesClient) -> None:
        self.client = client

    def from_description(self, description_text: str) -> JobDraftSchema:
        prompt = build_create_draft_from_description_prompt(description_text)
        return self._generate_job_draft(prompt)

    def from_form(self, form_payload: dict) -> JobDraftSchema:
        prompt = build_create_draft_from_form_prompt(form_payload)
        return self._generate_job_draft(prompt)

    def _generate_job_draft(self, prompt: str) -> JobDraftSchema:
        payload = self.client.generate_structured_output(
            prompt=prompt,
            schema_name="job_draft_schema",
            schema=JobDraftSchema.model_json_schema(),
        )

        try:
            return JobDraftSchema.model_validate(payload)
        except ValidationError as exc:
            raise ValueError("LLM returned invalid job draft schema.") from exc
