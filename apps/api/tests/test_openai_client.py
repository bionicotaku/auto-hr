import json
from types import SimpleNamespace

import pytest

from app.ai.client import OpenAIResponsesClient


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
