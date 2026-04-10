from pydantic import ValidationError

from app.ai.client import OpenAIResponsesClient
from app.ai.prompts.job_definition import build_job_finalize_prompt
from app.schemas.ai.job_definition import (
    JobFinalizeScoringResponseSchema,
)


class JobDefinitionFinalizeWorkflow:
    def __init__(self, client: OpenAIResponsesClient) -> None:
        self.client = client

    def run(
        self,
        *,
        description_text: str,
        rubric_items: list[dict],
    ) -> JobFinalizeScoringResponseSchema:
        prompt = build_job_finalize_prompt(
            description_text=description_text,
            rubric_items=rubric_items,
        )
        payload = self.client.generate_structured_output(
            prompt=prompt,
            schema_name="job_finalize_response_schema",
            schema=JobFinalizeScoringResponseSchema.model_json_schema(),
        )
        try:
            return JobFinalizeScoringResponseSchema.model_validate(payload)
        except ValidationError as exc:
            raise ValueError("LLM returned invalid job finalize schema.") from exc
