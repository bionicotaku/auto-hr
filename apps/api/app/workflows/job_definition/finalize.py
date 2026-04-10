from pydantic import ValidationError

from app.ai.client import OpenAIResponsesClient
from app.ai.prompts.job_definition import build_job_finalize_prompt
from app.schemas.ai.job_definition import JobFinalizeResponseSchema


class JobDefinitionFinalizeWorkflow:
    def __init__(self, client: OpenAIResponsesClient) -> None:
        self.client = client

    def run(
        self,
        *,
        title: str,
        summary: str,
        description_text: str,
        rubric_items: list[dict],
        structured_info_json: dict,
        original_description_input: str | None,
        original_form_input_json: dict | None,
    ) -> JobFinalizeResponseSchema:
        prompt = build_job_finalize_prompt(
            title=title,
            summary=summary,
            description_text=description_text,
            rubric_items=rubric_items,
            structured_info_json=structured_info_json,
            original_description_input=original_description_input,
            original_form_input_json=original_form_input_json,
        )
        payload = self.client.generate_structured_output(
            prompt=prompt,
            schema_name="job_finalize_response_schema",
            schema=JobFinalizeResponseSchema.model_json_schema(),
        )
        try:
            return JobFinalizeResponseSchema.model_validate(payload)
        except ValidationError as exc:
            raise ValueError("LLM returned invalid job finalize schema.") from exc
