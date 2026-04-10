from pydantic import ValidationError

from app.ai.client import OpenAIResponsesClient
from app.ai.prompts.job_definition import build_job_regenerate_prompt
from app.schemas.ai.job_definition import JobAgentEditResponseSchema


class JobDefinitionRegenerateWorkflow:
    def __init__(self, client: OpenAIResponsesClient) -> None:
        self.client = client

    def run(
        self,
        *,
        original_description_input: str | None,
        original_form_input_json: dict | None,
        title: str,
        summary: str,
        structured_info_json: dict,
        history_summary: str | None,
        recent_messages: list[dict],
    ) -> JobAgentEditResponseSchema:
        prompt = build_job_regenerate_prompt(
            original_description_input=original_description_input,
            original_form_input_json=original_form_input_json,
            title=title,
            summary=summary,
            structured_info_json=structured_info_json,
            history_summary=history_summary,
            recent_messages=recent_messages,
        )
        payload = self.client.generate_structured_output(
            prompt=prompt,
            schema_name="job_regenerate_response_schema",
            schema=JobAgentEditResponseSchema.model_json_schema(),
        )
        try:
            return JobAgentEditResponseSchema.model_validate(payload)
        except ValidationError as exc:
            raise ValueError("LLM returned invalid job regenerate schema.") from exc
