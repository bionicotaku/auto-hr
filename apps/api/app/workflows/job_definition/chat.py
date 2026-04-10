from pydantic import ValidationError

from app.ai.client import OpenAIResponsesClient
from app.ai.prompts.job_definition import build_job_chat_prompt
from app.schemas.ai.job_definition import JobChatResponseSchema


class JobDefinitionChatWorkflow:
    def __init__(self, client: OpenAIResponsesClient) -> None:
        self.client = client

    def run(
        self,
        *,
        description_text: str,
        responsibilities: list[str],
        skills: list[str],
        rubric_items: list[dict],
        recent_messages: list[dict],
        user_input: str,
    ) -> JobChatResponseSchema:
        prompt = build_job_chat_prompt(
            description_text=description_text,
            responsibilities=responsibilities,
            skills=skills,
            rubric_items=rubric_items,
            recent_messages=recent_messages,
            user_input=user_input,
        )
        payload = self.client.generate_structured_output(
            prompt=prompt,
            schema_name="job_chat_response_schema",
            schema=JobChatResponseSchema.model_json_schema(),
        )
        try:
            return JobChatResponseSchema.model_validate(payload)
        except ValidationError as exc:
            raise ValueError("LLM returned invalid job chat schema.") from exc
