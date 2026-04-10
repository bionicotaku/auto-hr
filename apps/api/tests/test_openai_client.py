import json
from types import SimpleNamespace

import httpx
import pytest
from openai import BadRequestError

from app.ai.client import OpenAIResponsesClient
from app.schemas.ai.job_definition import (
    JobDraftSchema,
    JobFinalizeScoringResponseSchema,
)


class FakeResponsesResult:
    def __init__(self, output_text: str):
        self.output_text = output_text


class FakeOpenAIClient:
    def __init__(self, output_text: str):
        self.output_text = output_text
        self.calls: list[dict] = []
        self.responses = SimpleNamespace(create=self.create)

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return FakeResponsesResult(self.output_text)


class FakeBadRequestClient:
    def __init__(self, message: str):
        self.message = message
        self.responses = SimpleNamespace(create=self.create)

    def create(self, **_kwargs):
        request = httpx.Request("POST", "https://api.openai.com/v1/responses")
        response = httpx.Response(
            status_code=400,
            request=request,
            json={"error": {"message": self.message}},
        )
        raise BadRequestError(message=self.message, response=response, body={"error": {"message": self.message}})


def build_client(output_text: str) -> tuple[OpenAIResponsesClient, FakeOpenAIClient]:
    fake = FakeOpenAIClient(output_text)
    client = OpenAIResponsesClient()
    client.client = fake  # type: ignore[assignment]
    return client, fake


def test_generate_structured_output_from_inputs_uses_responses_api_settings() -> None:
    client, fake = build_client(json.dumps({"value": "ok"}))

    payload = client.generate_structured_output_from_inputs(
        inputs=[{"role": "user", "content": [{"type": "input_text", "text": "hello"}]}],
        schema_name="candidate_standardization_schema",
        schema={
            "type": "object",
            "properties": {"value": {"type": "string"}},
            "required": ["value"],
        },
    )

    assert payload == {"value": "ok"}
    call = fake.calls[0]
    assert call["reasoning"] == {"effort": client.settings.openai_reasoning}
    assert call["text"]["format"]["strict"] is True


def test_openai_json_schema_normalization_requires_nullable_fields_and_removes_defaults() -> None:
    client, _ = build_client(json.dumps({"value": "ok"}))

    draft_schema = client._to_openai_json_schema(JobDraftSchema.model_json_schema())
    schema = client._to_openai_json_schema(JobFinalizeScoringResponseSchema.model_json_schema())
    finalize_rubric_schema = schema["$defs"]["JobFinalizeRubricItemEnrichmentSchema"]
    draft_rubric_schema = draft_schema["$defs"]["JobRubricItemDraftSchema"]
    structured_info_schema = draft_schema["$defs"]["JobStructuredInfoSchema"]

    assert "weight_normalized" not in draft_rubric_schema["properties"]
    assert "department" in structured_info_schema["required"]
    assert "default" not in structured_info_schema["properties"]["department"]
    assert "scoring_standard_items" not in draft_rubric_schema["properties"]
    assert finalize_rubric_schema["properties"]["scoring_standard_items"]["type"] == "array"
    assert schema["$defs"]["ScoringStandardItemSchema"]["required"] == [
        "key",
        "value",
    ]


def test_generate_structured_output_from_inputs_rejects_empty_output_text() -> None:
    client, _ = build_client("")

    with pytest.raises(ValueError):
        client.generate_structured_output_from_inputs(
            inputs=[{"role": "user", "content": [{"type": "input_text", "text": "hello"}]}],
            schema_name="candidate_standardization_schema",
            schema={"type": "object", "properties": {}, "required": []},
        )


def test_generate_structured_output_from_inputs_rejects_non_object_json() -> None:
    client, _ = build_client(json.dumps(["not-an-object"]))

    with pytest.raises(ValueError):
        client.generate_structured_output_from_inputs(
            inputs=[{"role": "user", "content": [{"type": "input_text", "text": "hello"}]}],
            schema_name="candidate_standardization_schema",
            schema={"type": "object", "properties": {}, "required": []},
        )


def test_generate_structured_output_surfaces_openai_bad_request_message() -> None:
    client = OpenAIResponsesClient()
    client.client = FakeBadRequestClient("Invalid schema for response_format 'job_draft_schema'.")  # type: ignore[assignment]

    with pytest.raises(ValueError, match="Invalid schema for response_format 'job_draft_schema'."):
        client.generate_structured_output(
            prompt="hello",
            schema_name="job_draft_schema",
            schema={"type": "object", "properties": {"value": {"type": "string"}}, "required": ["value"]},
        )
