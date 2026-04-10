from pydantic import ValidationError

from app.ai.client import OpenAIResponsesClient
from app.ai.prompts.job_definition import build_job_agent_edit_prompt
from app.schemas.ai.job_definition import JobAgentEditResponseSchema


class JobDefinitionAgentEditWorkflow:
    def __init__(self, client: OpenAIResponsesClient) -> None:
        self.client = client

    def run(
        self,
        *,
        title: str,
        summary: str,
        description_text: str,
        structured_info_json: dict,
        responsibilities: list[str],
        skills: list[str],
        rubric_items: list[dict],
        recent_messages: list[dict],
        user_input: str,
    ) -> JobAgentEditResponseSchema:
        prompt = build_job_agent_edit_prompt(
            title=title,
            summary=summary,
            description_text=description_text,
            structured_info_json=structured_info_json,
            responsibilities=responsibilities,
            skills=skills,
            rubric_items=rubric_items,
            recent_messages=recent_messages,
            user_input=user_input,
        )
        payload = self.client.generate_structured_output(
            prompt=prompt,
            schema_name="job_agent_edit_response_schema",
            schema=JobAgentEditResponseSchema.model_json_schema(),
        )
        try:
            return JobAgentEditResponseSchema.model_validate(payload)
        except ValidationError as exc:
            raise ValueError("LLM returned invalid job agent edit schema.") from exc
