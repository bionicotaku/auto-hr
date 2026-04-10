from pydantic import ValidationError

from app.ai.client import OpenAIResponsesClient
from app.ai.prompts.job_definition import build_job_finalize_title_summary_prompt
from app.schemas.ai.job_definition import JobFinalizeTitleSummarySchema


class JobDefinitionFinalizeTitleSummaryWorkflow:
    def __init__(self, client: OpenAIResponsesClient) -> None:
        self.client = client

    def run(
        self,
        *,
        description_text: str,
        responsibilities: list[str],
        skills: list[str],
        rubric_items: list[dict],
    ) -> JobFinalizeTitleSummarySchema:
        prompt = build_job_finalize_title_summary_prompt(
            description_text=description_text,
            responsibilities=responsibilities,
            skills=skills,
            rubric_items=rubric_items,
        )
        payload = self.client.generate_structured_output(
            prompt=prompt,
            schema_name="job_finalize_title_summary_schema",
            schema=JobFinalizeTitleSummarySchema.model_json_schema(),
        )
        try:
            return JobFinalizeTitleSummarySchema.model_validate(payload)
        except ValidationError as exc:
            raise ValueError("LLM returned invalid job finalize title summary schema.") from exc
